"""A pixel-art cat girl, drawn as coloured cells.

Each row is a run-length list of (symbol, count); symbols map to palette keys,
so the sprite recolours itself for the light and dark cards. Blinking is a
second grid with the eyes swapped for a lid line.
"""
from __future__ import annotations

W = 24

EYES = (6, 7, 8, 15, 16, 17)

# . transparent  H hair  S skin  E eye  W eye light  M mouth  B blush  C clothes  A bell
HEAD = [
    [(".", 4), ("H", 1), (".", 14), ("H", 1), (".", 4)],             # ear tips
    [(".", 3), ("H", 3), (".", 4), ("H", 1), (".", 7), ("H", 3), (".", 3)],   # ears + ahoge
    [(".", 2), ("H", 5), (".", 3), ("H", 1), (".", 6), ("H", 5), (".", 2)],
    [(".", 2), ("H", 20), (".", 2)],                                 # fringe
    [(".", 1), ("H", 22), (".", 1)],
    [(".", 1), ("H", 22), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    # eyes: three cells wide, one lit pixel in the corner
    [(".", 1), ("H", 3), ("S", 2), ("W", 1), ("E", 2), ("S", 6), ("W", 1), ("E", 2), ("S", 2), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 2), ("E", 3), ("S", 6), ("E", 3), ("S", 2), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 7), ("M", 2), ("S", 7), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 1), ("B", 2), ("S", 10), ("B", 2), ("S", 1), ("H", 3), (".", 1)],
    [(".", 1), ("H", 3), ("S", 16), ("H", 3), (".", 1)],
    [(".", 1), ("H", 4), ("S", 14), ("H", 4), (".", 1)],             # chin
    [(".", 2), ("H", 4), ("S", 12), ("H", 4), (".", 2)],
    [(".", 2), ("H", 5), ("S", 10), ("H", 5), (".", 2)],
    [(".", 3), ("H", 5), ("C", 3), ("A", 2), ("C", 3), ("H", 5), (".", 3)],
    [(".", 2), ("H", 6), ("C", 8), ("H", 6), (".", 2)],
    [(".", 2), ("H", 6), ("C", 8), ("H", 6), (".", 2)],
]

SYMBOLS = {
    "H": "hair",
    "S": "skin",
    "E": "ink",
    "W": "eye_light",
    "M": "mouth",
    "B": "blush",
    "C": "cloth",
    "A": "bell",
}


def _grid(rows) -> list[list[str]]:
    out = []
    for row in rows:
        cells = []
        for sym, n in row:
            cells.extend([sym] * n)
        if len(cells) != W:
            raise ValueError(f"row has {len(cells)} cells, expected {W}: {row}")
        out.append(cells)
    return out


def _blink(open_grid: list[list[str]]) -> list[list[str]]:
    shut = [list(r) for r in open_grid]
    for y in (7, 8):
        for x in EYES:
            shut[y][x] = "S"
    for x in EYES:  # one thin lid line instead of the open eye
        shut[8][x] = "H"
    return shut


OPEN_GRID = _grid(HEAD)
SHUT_GRID = _blink(OPEN_GRID)
HEIGHT = len(OPEN_GRID)


def render(canvas, palette: dict, x: float, y: float, px: float, grid=None, cls: str = "") -> None:
    """Draw the sprite with its top-left corner at (x, y); one cell is px wide."""
    grid = grid or OPEN_GRID
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
            out.append(f'<rect{k} x="{x + gx * px:.1f}" y="{y + gy * px:.1f}" '
                       f'width="{(end - gx) * px:.1f}" height="{px:.1f}" fill="{palette[SYMBOLS[sym]]}"/>')
            gx = end
    canvas.add("".join(out))
