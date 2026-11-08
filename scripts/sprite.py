"""A pixel-art cat girl, drawn as coloured cells.

The silhouette is authored once at 24x20 (run-length rows, so every row is
guaranteed the right width), then doubled to 48x40 so there is room for real
detail: eye catchlights, inner-ear shading, a highlight along the fringe and a
bell on the collar. Every symbol maps to a palette key, so the same drawing
recolours itself for the light and dark cards. Blinking is a second grid.
"""
from __future__ import annotations

BASE_W = 24
SCALE = 2
W = BASE_W * SCALE

# . none   H hair   h hair light   S skin   s skin shade   E ink   W eye light
# M mouth  B blush  C cloth  c cloth light  A accent
# The 24x20 original: ears big enough to read as cat ears at any size.
BASE = [
    [(".", 4), ("H", 1), (".", 14), ("H", 1), (".", 4)],
    [(".", 3), ("H", 3), (".", 4), ("H", 1), (".", 7), ("H", 3), (".", 3)],
    [(".", 2), ("H", 5), (".", 3), ("H", 1), (".", 6), ("H", 5), (".", 2)],
    [(".", 2), ("H", 20), (".", 2)],
    [(".", 1), ("H", 22), (".", 1)],
    [(".", 1), ("H", 22), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 2), ("W", 1), ("E", 2), ("S", 6), ("W", 1), ("E", 2), ("S", 2), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 2), ("E", 3), ("S", 6), ("E", 3), ("S", 2), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 7), ("M", 2), ("S", 7), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 1), ("B", 2), ("S", 10), ("B", 2), ("S", 1), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 4), ("S", 14), ("H", 4), (".", 1)],
    [(".", 2), ("H", 4), ("S", 12), ("H", 4), (".", 2)],
    [(".", 2), ("H", 5), ("S", 10), ("H", 5), (".", 2)],
    [(".", 3), ("H", 5), ("C", 3), ("A", 2), ("C", 3), ("H", 5), (".", 3)],
    [(".", 2), ("H", 6), ("C", 8), ("H", 6), (".", 2)],
    [(".", 2), ("H", 6), ("c", 8), ("H", 6), (".", 2)],
]

# detail stamps, in the doubled coordinate system
EYE = [  # 7x6, stamped over each eye
    "EEEEEEE",
    "EWWEEEE",
    "EWEEEEE",
    "EEEEEEE",
    "EEEEEEE",
    ".EEEEE.",
]
EYE_AT = ((14, 11), (14, 30))   # top-left corner of the left/right eye

STAMPS = [
    # inner ear: a lighter wedge inside each ear
    (7, 5, ["..hh.", ".hh.."], "h"),
    (7, 38, [".hh..", "..hh."], "h"),
]


def _grid() -> list[list[str]]:
    rows = []
    for i, row in enumerate(BASE):
        cells = []
        for sym, n in row:
            cells.extend([sym] * n)
        if len(cells) != BASE_W:
            raise ValueError(f"base row {i} has {len(cells)} cells, expected {BASE_W}")
        line = []
        for ch in cells:
            line.extend([ch, ch])
        rows.append(line)
        rows.append(list(line))
    return rows


def _stamp(grid, y: int, x: int, art: list[str], ch: str) -> None:
    for dy, line in enumerate(art):
        for dx, c in enumerate(line):
            if c != ".":
                grid[y + dy][x + dx] = c


def _detail(grid: list[list[str]]) -> list[list[str]]:
    # eyes: replace the coarse 6x4 block with a proper 7x6 eye
    for y, x in EYE_AT:
        for dy in range(6):
            for dx in range(7):
                grid[y + dy][x + dx] = "S"
        _stamp(grid, y, x, EYE, "E")

    # a highlight running along the top of the fringe
    for x in range(12, 36):
        if grid[8][x] == "H":
            grid[8][x] = "h"
    for x in range(10, 38):
        if grid[9][x] == "H":
            grid[9][x] = "h"

    # inner ear shading
    for y, x, art, ch in STAMPS:
        _stamp(grid, y, x, art, ch)

    # hair strands falling past the shoulders, a shade darker
    for y in range(32, 38):
        for x in range(2, 8):
            if grid[y][x] == "H":
                grid[y][x] = "h"
        for x in range(40, 46):
            if grid[y][x] == "H":
                grid[y][x] = "h"

    # a lighter edge on the collar, so it separates from the hair
    for x in (10, 11, 12, 13, 34, 35, 36, 37):
        if grid[34][x] == "C":
            grid[34][x] = "c"
        if grid[35][x] == "C":
            grid[35][x] = "c"

    # the bell sits lower on the collar, otherwise it reads as a red mouth
    for y in range(len(grid)):
        for x in range(W):
            if grid[y][x] == "A":
                grid[y][x] = "C"
    for y in (36, 37):
        for x in range(22, 26):
            grid[y][x] = "A"
    return grid


OPEN_GRID = _detail(_grid())
HEIGHT = len(OPEN_GRID)

SYMBOLS = {
    "H": "hair",
    "h": "hair2",
    "S": "skin",
    "s": "skin2",
    "E": "ink",
    "W": "eye_white",
    "M": "mouth",
    "B": "blush",
    "C": "cloth",
    "c": "cloth2",
    "A": "accent",
}

EYE_ROWS = tuple(range(14, 20))


def _blink(grid: list[list[str]]) -> list[list[str]]:
    shut = [list(r) for r in grid]
    for y in EYE_ROWS:
        for x in range(W):
            if shut[y][x] in "EW":
                shut[y][x] = "S"
    for y, x in EYE_AT:
        for dx in range(7):  # one thin lid line
            shut[y + 4][x + dx] = "E"
    return shut


SHUT_GRID = _blink(OPEN_GRID)


def render(canvas, palette: dict, x: float, y: float, px: float, grid=None, cls: str = "") -> None:
    """Draw the sprite with its top-left corner at (x, y); one cell is px wide."""
    grid = grid or OPEN_GRID
    pad = 0.4  # slight overlap, otherwise fractional cell sizes leave hairlines
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
