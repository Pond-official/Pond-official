"""A pixel-art cat girl, drawn as coloured cells.

Reference: long honey-blonde hair with a straight fringe, big fluffy cat ears,
turquoise eyes, an oversized white shirt.

Everything is generated geometrically instead of hand-counted rows: the head is
an ellipse, the ears are triangles, the long hair is a tube swept along a bezier
so it tapers where it meets the shoulder. Hand-written rows kept drifting into a
square face.

Every symbol maps to a palette key, so one drawing recolours itself for the
light and the dark card. Blinking is a small overlay (`render_lid`) rather than
a second full sprite.
"""
from __future__ import annotations
import math

W, H = 72, 60

# . none  h hair  t hair light  u hair dark  S skin  s skin shade
# E ink   K iris  W white    M mouth  B blush  c cloth light
EYE = [
    "...EEEEE...",
    "..EEEEEEE..",
    ".EIIIIIIIE.",
    "EIIKKKKKIIE",
    "EIIKKKKKIIE",
    "EIKWWKKKIIE",
    "EIKWWKKKIIE",
    "EIIKEEEKKII",
    "EIIKEEEKKII",
    "EIIKEEEKKII",
    ".EIKKKKKIE.",
    "..EILLLIE..",
    "...EEEEE...",
]
EYE_AT = ((24, 21), (37, 21))
EYE_W, EYE_H = 11, 13

LID = [
    "...........",
    "...........",
    "...........",
    "...........",
    "...........",
    "...........",
    ".EE.....EE.",
    "..EE...EE..",
    "....EEE....",
    "...........",
    "...........",
    "...........",
    "...........",
]

# a gentle closed-mouth smile
MOUTH = [
    "M...M",
    ".MMM.",
]
MOUTH_AT = (34, 36)

BLUSH = [
    ".BBB.",
    "BBBBB",
    ".BBB.",
]
BLUSH_AT = ((25, 34), (42, 34))

SYMBOLS = {
    "h": "hair",
    "t": "hair2",
    "u": "hair3",
    "S": "skin",
    "s": "skin2",
    "E": "ink",
    "I": "pupil",
    "K": "iris",
    "L": "iris2",
    "W": "eye_white",
    "M": "mouth",
    "B": "blush",
    "c": "cloth2",
}

CX = 36.0
HEAD = (CX, 23.5, 18.0, 16.0)
FACE = (CX, 26.6, 14.2, 13.2)

# long hair falling on both sides, tapering to a soft end
HAIR_L = ((20.0, 15.0), (11.0, 30.0), (11.5, 47.0), (15.0, 58.0))
HAIR_R = tuple((W - 1 - x, y) for x, y in HAIR_L)

EAR_L = ((11.0, 2.5), (6.0, 18.0), (28.0, 13.0))
EAR_R = tuple((W - 1 - x, y) for x, y in EAR_L)


def _inside(x: float, y: float, box) -> bool:
    cx, cy, rx, ry = box
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def _tri(x: float, y: float, a, b, c) -> bool:
    def side(p, q, r):
        return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])
    d1, d2, d3 = side((x, y), a, b), side((x, y), b, c), side((x, y), c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


def _shrink(tri, t: float):
    cx = sum(p[0] for p in tri) / 3
    cy = sum(p[1] for p in tri) / 3
    return tuple((cx + (p[0] - cx) * t, cy + (p[1] - cy) * t) for p in tri)


def _bez(t: float, p):
    u = 1 - t
    return (u ** 3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t ** 3 * p[3][0],
            u ** 3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t ** 3 * p[3][1])


def _tube(grid, curve, r0: float, r1: float, sym: str,
          shift=(0.0, 0.0), span=(0.0, 1.0), power: float = 0.9) -> None:
    """Sweep a disc of shrinking radius along a bezier and fill the cells it covers."""
    n = 260
    for i in range(n + 1):
        t = i / n
        if not (span[0] <= t <= span[1]):
            continue
        x, y = _bez(t, curve)
        x += shift[0]
        y += shift[1]
        r = r0 + (r1 - r0) * (t ** power)
        for yy in range(int(y - r) - 1, int(y + r) + 2):
            if not (0 <= yy < H):
                continue
            for xx in range(int(x - r) - 1, int(x + r) + 2):
                if 0 <= xx < W and (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2 <= r * r:
                    grid[yy][xx] = sym


def _stamp(grid, art: list[str], x: int, y: int) -> None:
    for dy, line in enumerate(art):
        for dx, ch in enumerate(line):
            if ch != ".":
                grid[y + dy][x + dx] = ch


def _ears(grid) -> None:
    for tri in (EAR_L, EAR_R):
        for y in range(H):
            for x in range(W):
                if _tri(x + 0.5, y + 0.5, *tri):
                    grid[y][x] = "h"
    # the inside of the ear is skin, so it reads as fur
    for tri in (EAR_L, EAR_R):
        inner = _shrink(tri, 0.5)
        for y in range(H):
            for x in range(W):
                if _tri(x + 0.5, y + 0.5, *inner) and y < 15:
                    grid[y][x] = "S"


def _build() -> list[list[str]]:
    grid = [["."] * W for _ in range(H)]

    # ---- the long hair first, so the head sits on top of it
    for curve in (HAIR_L, HAIR_R):
        out = -1.4 if curve is HAIR_L else 1.4
        _tube(grid, curve, 5.8, 3.6, "u", shift=(out, 0.6))
        _tube(grid, curve, 5.0, 2.9, "h")
        _tube(grid, curve, 1.1, 0.8, "t", shift=(-out * 1.9, -1.4), span=(0.06, 0.60))

    # ---- head, then the ears on top of it
    for y in range(H):
        for x in range(W):
            if _inside(x + 0.5, y + 0.5, HEAD):
                grid[y][x] = "h"
    _ears(grid)

    # ---- face
    for y in range(H):
        for x in range(W):
            if _inside(x + 0.5, y + 0.5, FACE):
                grid[y][x] = "S"

    # ---- a straight fringe with a little wave, plus the locks in front of the ears
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if not _inside(px, py, FACE):
                continue
            fringe = 20.4 + 0.7 * math.sin((px - CX) / 2.3)
            k = max(0.0, 1 - ((py - FACE[1]) / FACE[3]) ** 2) ** 0.3
            if py <= fringe:
                grid[y][x] = "h"
            elif abs(px - CX) >= 13.6 * k:
                grid[y][x] = "h"

    # ---- seams in the fringe, and a light band across the crown

    cx, cy, rx, ry = HEAD
    for y in range(H):
        for x in range(W):
            if grid[y][x] != "h":
                continue
            r = (((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2) ** 0.5
            if 0.72 <= r <= 0.88 and y < 19:
                grid[y][x] = "t"

    # ---- light on the left, shade on the right, so the hair is not flat
    for y in range(H):
        for x in range(48, 56):
            if grid[y][x] == "h":
                grid[y][x] = "u"

    # ---- the fringe casts a shadow on the forehead
    for y in range(9, 24):
        for x in range(W):
            if grid[y][x] == "S":
                above = grid[y - 1][x]
                if above in "htu":
                    grid[y][x] = "s"

    # ---- neck and an oversized white shirt (before the face, or they eat the mouth)
    for y in range(41, H):
        hw = min(21.0, 8.0 + (y - 41) * 1.3)
        for x in range(W):
            if abs(x + 0.5 - CX) <= hw:
                grid[y][x] = "W"
    for y in range(38, 45):
        for x in range(32, 41):
            grid[y][x] = "S"
    # a shadow under the chin, otherwise the jaw melts into the white shirt
    for x in range(31, 42):
        if grid[38][x] == "S":
            grid[38][x] = "s"
    # collar seam and the shoulder line, otherwise a white shirt is a white blob
    for y in range(42, H):
        hw = min(21.0, 8.0 + (y - 42) * 1.3)
        for x in range(W):
            if abs(abs(x + 0.5 - CX) - hw) <= 1.0 and grid[y][x] == "W":
                grid[y][x] = "c"
    for y in (43, 44):
        for x in range(31, 42):
            if grid[y][x] == "W":
                grid[y][x] = "c"

    _stamp(grid, EYE, *EYE_AT[0])
    _stamp(grid, EYE, *EYE_AT[1])
    _stamp(grid, MOUTH, *MOUTH_AT)
    for x, y in BLUSH_AT:
        _stamp(grid, BLUSH, x, y)
    return grid


OPEN_GRID = _build()
HEIGHT = len(OPEN_GRID)


def render(canvas, palette: dict, x: float, y: float, px: float, grid=None, cls: str = "") -> None:
    """Draw the sprite with its top-left corner at (x, y); one cell is px wide."""
    grid = grid or OPEN_GRID
    pad = 0.35  # slight overlap, otherwise fractional cell sizes leave hairlines
    out = []
    for gy, row in enumerate(grid):
        gx = 0
        while gx < W:
            sym = row[gx]
            if sym == ".":
                gx += 1
                continue
            end = gx
            while end < W and row[end] == sym:
                end += 1
            k = f' class="{cls}"' if cls else ""
            out.append(f'<rect{k} x="{x + gx * px:.2f}" y="{y + gy * px:.2f}" '
                       f'width="{(end - gx) * px + pad:.2f}" height="{px + pad:.2f}" '
                       f'fill="{palette[SYMBOLS[sym]]}"/>')
            gx = end
    canvas.add("".join(out))


def render_lid(canvas, palette: dict, x: float, y: float, px: float, cls: str = "") -> None:
    """The blinking overlay: skin over both eyes, then the closed lids."""
    k = f' class="{cls}"' if cls else ""
    out = []
    for ex, ey in EYE_AT:
        out.append(f'<rect{k} x="{x + ex * px:.2f}" y="{y + ey * px:.2f}" '
                   f'width="{EYE_W * px + 0.35:.2f}" height="{EYE_H * px + 0.35:.2f}" '
                   f'fill="{palette["skin"]}"/>')
    for dy, line in enumerate(LID):
        gx = 0
        while gx < EYE_W:
            sym = line[gx]
            if sym == ".":
                gx += 1
                continue
            end = gx
            while end < EYE_W and line[end] == sym:
                end += 1
            for ex, ey in EYE_AT:
                out.append(f'<rect{k} x="{x + (ex + gx) * px:.2f}" y="{y + (ey + dy) * px:.2f}" '
                           f'width="{(end - gx) * px + 0.35:.2f}" height="{px + 0.35:.2f}" '
                           f'fill="{palette[SYMBOLS[sym]]}"/>')
            gx = end
    canvas.add("".join(out))
