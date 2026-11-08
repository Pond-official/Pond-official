"""A little cat, drawn with characters on the terminal grid.

No pixels: every stroke is a real character sitting on the same cell grid the
terminal cards use, then converted to a vector outline by `term`. So the cat is
in the same visual language as the rest of the page - one character wide, one
line high, always aligned - and it recolours itself for the light and the dark
card through the palette keys below.

The eyes are drawn as their own groups, so blinking is a CSS class swap instead
of a second copy of the drawing.
"""
from __future__ import annotations

from term import Term

# The classic internet cat, kept character for character: `==` are the whiskers,
# `^` the nose, `(` `)` the paws. Rows are centred on the widest one, otherwise
# the head sits left of the body.
ROWS = [
    "     /\\_____/\\   ",
    "   /  o   o  \\   ",
    "  ( ==  ^  == )  ",
    "   )         (   ",
    "  (           )  ",
    " ( (  )   (  ) ) ",
    "(__(__)___(__)__)",
]

COLS = max(len(r) for r in ROWS)
LINES = len(ROWS)
LH = 1.3                       # line height, in em
EYE_ROW = 1                     # the row the eyes sit on
BODY = 3                        # rows 0..2 are the head, the rest is the body

# character -> palette key
INK = {
    "/": "fg2", "\\": "fg2", "(": "fg2", ")": "fg2", "_": "fg2",
    "o": "iris", "^": "mouth", "=": "overlay1", "-": "overlay1",
}


def measure(size: float) -> tuple[float, float]:
    """Width and height in px of the whole drawing at a given font size."""
    return COLS * size * 0.6, LINES * size * LH


def _runs(row: str):
    """Yield (column, text, colour) for each run of equal colour."""
    col, buf, cur = 0, "", None
    for ch in row:
        ink = INK.get(ch)
        if ink is None:
            if buf:
                yield col - len(buf), buf, cur
            buf, cur = "", None
            col += 1
            continue
        if ink != cur and buf:
            yield col - len(buf), buf, cur
            buf = ""
        buf, cur = buf + ch, ink
        col += 1
    if buf:
        yield col - len(buf), buf, cur


def render(c, P: dict, x: float, y: float, size: float, blink=None, bold: bool = True,
           body: bool = True) -> None:
    """Draw the cat with its top-left corner at (x, y).

    blink=None    open eyes only
    blink="shut"  closed eyes only (sleeping)
    blink="cls"   open eyes, plus closed lids in a group with that CSS class,
                  so the card can flip between them
    body=False    head only, for when the drawing sits behind a word
    """
    t = Term(c, P, x, y, size=size, lh=LH)
    rows = ROWS if body else ROWS[:BODY]
    blank = ["".join(" " if ch == "o" else ch for ch in row) for row in rows]
    for r, row in enumerate(blank):
        for col, text, ink in _runs(row):
            c.add(t.text(col, r, text, ink, bold=bold))

    eyes = [(i, EYE_ROW) for i, ch in enumerate(ROWS[EYE_ROW]) if ch == "o"]

    def draw_open():
        for i, r in eyes:
            c.add(t.text(i, r, "o", "iris", bold=bold))

    def draw_shut():
        for i, r in eyes:
            c.add(t.text(i, r, "-", "fg2", bold=bold))

    if blink == "shut":
        draw_shut()
        return

    if isinstance(blink, (list, tuple)):
        # two frames that take turns: the open eyes must disappear while the
        # lids are up, so each state gets its own visibility class. The attributes
        # are what shows when CSS animation is off: open eyes, lids hidden.
        open_cls, shut_cls = blink
        c.add(f'<g class="{open_cls}" opacity="1">')
        draw_open()
        c.add("</g>", f'<g class="{shut_cls}" opacity="0">')
        draw_shut()
        c.add("</g>")
        return

    draw_open()
