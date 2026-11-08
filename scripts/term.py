"""Monospace text drawn as vector outlines.

GitHub's image sandbox refuses web fonts, so each glyph is converted to a path
once and reused with <use>. Wide characters (CJK) take two cells, exactly like a
terminal, so mixed Chinese and ASCII always lines up.
"""
from __future__ import annotations

import os
import re
import unicodedata
import urllib.request
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

# google/fonts pinned to one commit: the URLs can never move under us
FONT_ROOT = "https://raw.githubusercontent.com/google/fonts/47d54ca1ebb14fd864695f1d39dc734f39017c33/ofl/"

FACES = {
    "mono": ("jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf", {"wght": 420}),
    "mono_b": ("jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf", {"wght": 760}),
    "cjk": ("notosanssc/NotoSansSC%5Bwght%5D.ttf", {"wght": 450}),
    "cjk_b": ("notosanssc/NotoSansSC%5Bwght%5D.ttf", {"wght": 750}),
    "sym": ("notosanssymbols2/NotoSansSymbols2-Regular.ttf", None),
}

STACK = {False: ["mono", "cjk", "sym"], True: ["mono_b", "cjk_b", "sym"]}

ASC, DESC = 1.02, 0.30  # JetBrains Mono line metrics, in em
CELL = 0.6  # advance width of one cell
NUDGE = {"cjk": 0.05, "cjk_b": 0.05}  # CJK sits slightly low next to Latin


def _n(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Face:
    def __init__(self, key: str, path: Path, location):
        self.key = key
        self.tt = TTFont(str(path), lazy=True)
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet(location=location) if location else self.tt.getGlyphSet()

    def has(self, ch: str) -> bool:
        return ord(ch) in self.cmap

    def adv(self, name: str) -> float:
        return self.gs[name].width / self.upm

    def path(self, name: str, size: float) -> str:
        s = size / self.upm
        pen = SVGPathPen(self.gs, ntos=_n)
        self.gs[name].draw(TransformPen(pen, (s, 0, 0, -s, 0, 0)))
        return pen.getCommands()


def _cache_dir() -> Path:
    d = Path(os.environ.get("FONT_CACHE", Path(__file__).resolve().parent.parent / ".cache" / "fonts"))
    d.mkdir(parents=True, exist_ok=True)
    return d


_LOADED: dict[str, Face] = {}


def face(key: str) -> Face:
    if key not in _LOADED:
        rel, loc = FACES[key]
        name = rel.split("/")[-1].replace("%5B", "[").replace("%5D", "]")
        dest = _cache_dir() / name
        if not dest.exists():
            print(f"  fetching {name} ...", flush=True)
            tmp = dest.with_name(dest.name + ".part")
            with urllib.request.urlopen(FONT_ROOT + rel, timeout=300) as r, open(tmp, "wb") as f:
                f.write(r.read())
            tmp.replace(dest)
        _LOADED[key] = Face(key, dest, loc)
    return _LOADED[key]


_MISSING: set[str] = set()


def pick(ch: str, bold: bool = False, prefer: tuple = ()):
    """Which face draws this character, and how wide it is in cells."""
    for key in (*prefer, *STACK[bold]):
        f = face(key)
        if f.has(ch):
            g = f.cmap[ord(ch)]
            adv = f.adv(g)
            wide = unicodedata.east_asian_width(ch) in ("W", "F") or adv > 0.78
            return f, g, adv, 2 if wide else 1
    if ch not in _MISSING:  # colour emoji and friends: draw the tofu box
        _MISSING.add(ch)
        print(f"  warning: no face has {ch!r} (U+{ord(ch):04X}); drawing a box")
    return pick("\u25a1", bold)


def _ident(f: Face, glyph: str, size: float) -> str:
    return f"{f.key}{int(size * 10)}-{re.sub(r'[^A-Za-z0-9_-]', '_', glyph)}"


def glyph(c: "Canvas", ch: str, x: float, y: float, size: float, bold: bool = True, prefer: tuple = (),
          attrs: str = "") -> str:
    """One character: left edge of its cell at x, baseline at y."""
    f, g, adv, n = pick(ch, bold, prefer)
    ident = _ident(f, g, size)
    if ident not in c.defs:
        c.define(ident, f'<path id="{ident}" d="{f.path(g, size)}"/>')
    a = f" {attrs}" if attrs else ""
    return f'<use href="#{ident}" x="{_n(x)}" y="{_n(y)}"{a}/>'


def ink_box(ch: str, size: float, bold: bool = True, prefer: tuple = ()) -> tuple[float, float, float, float]:
    """Ink bounds (x0, y0, x1, y1) in px relative to the glyph origin, y down."""
    f, g, _, _ = pick(ch, bold, prefer)
    pen = BoundsPen(f.gs)
    f.gs[g].draw(pen)
    k = size / f.upm
    x0, y0, x1, y1 = pen.bounds or (0, 0, 0, 0)
    return x0 * k, -y1 * k, x1 * k, -y0 * k


def cells(s: str) -> int:
    return sum(1 if ch == " " else pick(ch)[3] for ch in s)


TAG = re.compile(r"\[(/|[a-z0-9_ ]+)\]")


def parse(markup: str, default: str = "text") -> list[tuple[str, str, bool]]:
    """'[jade b]Pond[/]!' -> [('Pond', 'jade', True), ('!', 'text', False)].

    Write '[[' for a literal bracket.
    """
    out: list[tuple[str, str, bool]] = []
    stack = [(default, False)]
    pos = 0
    text = markup.replace("[[", "\x00")
    for m in TAG.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()].replace("\x00", "["), *stack[-1]))
        tag = m.group(1)
        if tag == "/":
            if len(stack) > 1:
                stack.pop()
        else:
            parts = tag.split()
            color = next((p for p in parts if p != "b"), stack[-1][0])
            stack.append((color, "b" in parts))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:].replace("\x00", "["), *stack[-1]))
    return [o for o in out if o[0]]


def plain(markup: str) -> str:
    return "".join(t for t, _, _ in parse(markup))


class Term:
    """A grid of character cells starting at (x, y)."""

    def __init__(self, c: "Canvas", palette: dict, x: float, y: float, size: float = 14.0, lh: float = 1.5):
        self.c, self.P = c, palette
        self.x, self.y, self.size = x, y, size
        self.cw = size * CELL
        self.lh = size * lh

    def col_x(self, col: float) -> float:
        return self.x + col * self.cw

    def row_y(self, row: float) -> float:
        return self.y + row * self.lh

    def baseline(self, row: float) -> float:
        return self.row_y(row) + (self.lh - (ASC + DESC) * self.size) / 2 + ASC * self.size

    def _ref(self, f: Face, g: str) -> str:
        ident = _ident(f, g, self.size)
        if ident not in self.c.defs:
            self.c.define(ident, f'<path id="{ident}" d="{f.path(g, self.size)}"/>')
        return ident

    def pieces(self, col: float, row: float, s: str, bold: bool = False, cls=None, start: int = 0):
        """Yield (svg, width in cells) for each run of characters."""
        cx, skip, i = col, 0, -1
        for i, ch in enumerate(s):
            if i < skip:
                continue
            if ch == " ":
                cx += 1
                continue
            if ch == "\u2588":  # solid blocks become one rect per run: no seams
                j = i
                while j < len(s) and s[j] == "\u2588":
                    j += 1
                top = self.baseline(row) - ASC * self.size
                k = cls(start + i) if cls else None
                kc = f' class="{k}"' if k else ""
                yield (f'<rect x="{_n(self.col_x(cx))}" y="{_n(top)}" width="{_n((j - i) * self.cw + .4)}" '
                       f'height="{_n((ASC + DESC) * self.size + .4)}"{kc}/>'), j - i
                cx += j - i
                skip = j
                continue
            f, g, adv, n = pick(ch, bold)
            ref = self._ref(f, g)
            x = self.col_x(cx) + (n * self.cw - adv * self.size) / 2
            y = self.baseline(row) + NUDGE.get(f.key, 0) * self.size
            k = cls(start + i) if cls else None
            kc = f' class="{k}"' if k else ""
            yield f'<use href="#{ref}" x="{_n(x)}" y="{_n(y)}"{kc}/>', n
            cx += n

    def text(self, col: float, row: float, s: str, color: str = "text", bold: bool = False, cls=None,
             start: int = 0, attrs: str = "") -> str:
        fill = self.P.get(color, color)
        uses = "".join(u for u, _ in self.pieces(col, row, s, bold, cls, start))
        a = f" {attrs}" if attrs else ""
        return f'<g fill="{fill}"{a}>{uses}</g>' if uses else ""

    def blocks(self, col: float, row: float, s: str) -> list[tuple[float, float, float, float]]:
        """(x, y, w, h) of every run of solid blocks in s."""
        out, i = [], 0
        while i < len(s):
            if s[i] != "\u2588":
                i += 1
                continue
            j = i
            while j < len(s) and s[j] == "\u2588":
                j += 1
            top = self.baseline(row) - ASC * self.size
            out.append((self.col_x(col + i), top, (j - i) * self.cw, (ASC + DESC) * self.size))
            i = j
        return out

    def markup(self, col: float, row: float, m: str, cls=None, default: str = "text") -> tuple[str, int]:
        """Draw '[jade]coloured[/] text'. Returns (svg, cells used)."""
        out, cx, i = [], col, 0
        for run, color, bold in parse(m, default):
            out.append(self.text(cx, row, run, color, bold, cls, start=i))
            cx += cells(run)
            i += len(run)
        return "".join(out), int(cx - col)
