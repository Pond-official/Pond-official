"""A pixel-art cat girl, drawn as coloured cells.

The head is built from a couple of ellipses and two triangles rather than
hand-counted rows, so the outline is always round and symmetric - hand-written
rows kept drifting into a square face. On top of that sit the details that make
her read as a cat girl: pink inner ears, an ahoge, a clip on the fringe, big
two-tone eyes with catchlights, an omega mouth, blush, and a ribbon with a bell.

Every symbol maps to a palette key, so one drawing recolours itself for the
light and the dark card. Blinking is not a second full sprite: the cards draw
this one, then stamp a small "eyes shut" overlay on top, which keeps the file
small.
"""
from __future__ import annotations

W, H = 72, 60

# . none   H hair   h hair light   S skin   E ink   K iris   W white (eye + collar)
# M mouth  B blush / inner ear    C cloth  c cloth light   A accent   G bell
EYE = [
    "....EEEE....",
    "..EEEEEEEE..",
    ".EEEEEEEEEE.",
    "EEEEEEEEEEEE",
    "EEWWEEEEEEEE",
    "EEWWEEEEEWWE",
    "EEEEEEEEEEWE",
    "KKKKKKKKKKKK",
    "KKKKKKKKKKKK",
    ".KKKKKKKKKK.",
    "..KKKKKKKK..",
    "...KKKKKK...",
]
EYE_AT = ((21, 26), (39, 26))
EYE_W, EYE_H = 12, 12

# a soft U, stamped over the eyes when she blinks
LID = [
    "............",
    "............",
    "............",
    "............",
    "............",
    ".EE......EE.",
    "..EE....EE..",
    "....EEEE....",
    "............",
    "............",
    "............",
    "............",
]

# omega mouth: three peaks, two dips
MOUTH = [
    "M..M..M",
    ".MM.MM.",
]
MOUTH_AT = (33, 42)

BLUSH = [
    ".BBBBBB.",
    "BBBBBBBB",
    ".BBBBBB.",
]
BLUSH_AT = ((17, 39), (47, 39))

SYMBOLS = {
    "H": "hair",
    "h": "hair2",
    "S": "skin",
    "s": "skin2",
    "E": "ink",
    "K": "iris",
    "W": "eye_white",
    "M": "mouth",
    "B": "blush",
    "C": "cloth",
    "c": "cloth2",
    "A": "accent",
    "G": "bell",
}

CX = 36.0
HEAD = (CX, 30.0, 26.6, 25.0)     # cx, cy, rx, ry - the whole hair mass
FACE = (CX, 32.0, 21.0, 16.2)     # the skin oval inside it

EAR_L = ((9.0, 0.0), (1.0, 17.0), (22.0, 13.0))
EAR_R = ((W - 9.0, 0.0), (W - 1.0, 17.0), (W - 22.0, 13.0))


def _inside(x: float, y: float, box) -> bool:
    cx, cy, rx, ry = box
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def _tri(x: float, y: float, a, b, c) -> bool:
    def side(p, q, r):
        return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])
    d1, d2, d3 = side((x, y), a, b), side((x, y), b, c), side((x, y), c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


def _shrink(p, tri, t: float):
    cx = sum(q[0] for q in tri) / 3
    cy = sum(q[1] for q in tri) / 3
    return (cx + (p[0] - cx) * t, cy + (p[1] - cy) * t)


def _stamp(grid, art: list[str], x: int, y: int) -> None:
    for dy, line in enumerate(art):
        for dx, ch in enumerate(line):
            if ch != ".":
                grid[y + dy][x + dx] = ch


def _ears(grid) -> None:
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if _tri(px, py, *EAR_L) or _tri(px, py, *EAR_R):
                grid[y][x] = "H"
    # pink inner ear
    for tri in (EAR_L, EAR_R):
        inner = tuple(_shrink(p, tri, 0.52) for p in tri)
        for y in range(H):
            for x in range(W):
                if _tri(x + 0.5, y + 0.5, *inner):
                    grid[y][x] = "B"


def _build() -> list[list[str]]:
    grid = [["."] * W for _ in range(H)]

    # ---- hair mass: a round head, then a curtain of hair down to the frame
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if _inside(px, py, HEAD):
                grid[y][x] = "H"
            elif py > 30:
                curtain = HEAD[2] * max(0.0, 1 - ((py - 30) / 33) ** 2) ** 0.5
                if abs(px - CX) <= curtain:
                    grid[y][x] = "H"

    _ears(grid)

    # ---- face
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if _inside(px, py, FACE):
                grid[y][x] = "S"

    # ---- fringe and side locks
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if not _inside(px, py, FACE):
                continue
            fringe = min(23.0, 23.5 - 0.0125 * (px - CX) ** 2)
            if py <= fringe or abs(px - CX) >= 16.5:
                grid[y][x] = "H"

    # ---- a light arc along the top of the hair
    cx, cy, rx, ry = HEAD
    for y in range(H):
        for x in range(W):
            if grid[y][x] != "H":
                continue
            r = (((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2) ** 0.5
            if 0.74 <= r <= 0.90 and y < 30:
                grid[y][x] = "h"

    # ---- ahoge: a chunky curl standing up off the crown
    for x, y in [(35, 6), (36, 6), (37, 6), (35, 5), (36, 5), (37, 5),
                 (35, 4), (36, 4), (35, 3), (36, 3), (36, 2), (37, 2),
                 (37, 1), (38, 1)]:
        grid[y][x] = "H"

    # ---- a diamond clip on the fringe
    for x, y in [(46, 18), (45, 19), (46, 19), (47, 19), (46, 20)]:
        grid[y][x] = "A"

    _stamp(grid, EYE, *EYE_AT[0])
    _stamp(grid, EYE, *EYE_AT[1])
    _stamp(grid, MOUTH, *MOUTH_AT)
    for x, y in BLUSH_AT:
        _stamp(grid, BLUSH, x, y)

    # ---- body: shoulders growing out of the neck, hair falling past them
    for y in range(48, H):
        hw = min(22.0, 8.5 + (y - 48) * 1.6)
        for x in range(W):
            if abs(x + 0.5 - CX) <= hw:
                grid[y][x] = "C"
    # the neck, in front of the collar
    for y in range(46, 52):
        for x in range(34, 39):
            grid[y][x] = "S"
    # a white collar opening into a V
    for y in range(50, 56):
        for x in range(W):
            if grid[y][x] != "C":
                continue
            if abs(x + 0.5 - CX) >= 3.0 + (y - 50) * 2.6:
                grid[y][x] = "W"
    # a ribbon tied at the throat
    for y in (53, 55):
        for x in list(range(29, 32)) + list(range(40, 43)):
            grid[y][x] = "A"
    for x in range(29, 43):
        grid[54][x] = "A"
    # and a bell hanging off it
    for y in (56, 57, 58):
        for x in (34, 35, 36, 37):
            grid[y][x] = "G"
    for x in (35, 36):
        grid[59][x] = "G"
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
