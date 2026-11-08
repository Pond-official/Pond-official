"""A pixel-art Hatsune Miku, drawn as coloured cells.

Everything is generated geometrically instead of hand-counted rows: the head is
an ellipse, the pigtails are tubes swept along bezier curves, the headset is an
arc plus two discs. Hand-written rows kept drifting into a square face, and a
sweep gives a tail that actually tapers and curls.

What makes her recognisable: teal twin tails, a grey headset with a glowing
ring, a white shirt and a teal tie, cyan eyes. Every symbol maps to a palette
key, so one drawing recolours itself for the light and the dark card. Blinking
is a small overlay (`render_lid`) rather than a second full sprite.
"""
from __future__ import annotations
W, H = 72, 60

# . none  h hair  t hair light  u hair dark  S skin  s skin shade
# E ink   K iris  W white    M mouth  B blush  C headset  c cloth light  G tie
EYE = [
    "..EEEEEE..",
    ".EEEEEEEE.",
    "EEKKKKKKEE",
    "EKWWKKKKKE",
    "EKWWKKKKWE",
    "EKKKKKKKWE",
    "EKKKKKKKKE",
    "EKKKKKKKKE",
    ".EKKKKKKE.",
    "..EKKKKE..",
    "...EEEE...",
]
EYE_AT = ((25, 21), (37, 21))
EYE_W, EYE_H = 10, 11

LID = [
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    ".EE....EE.",
    "..EE..EE..",
    "....EE....",
    "..........",
    "..........",
    "..........",
]

# omega mouth: three peaks, two dips
MOUTH = [
    "M..M..M",
    ".MM.MM.",
]
MOUTH_AT = (33, 34)

BLUSH = [
    ".BBB.",
    "BBBBB",
    ".BBB.",
]
BLUSH_AT = ((24, 33), (43, 33))

SYMBOLS = {
    "h": "hair",
    "t": "hair2",
    "u": "hair3",
    "S": "skin",
    "s": "skin2",
    "E": "ink",
    "K": "iris",
    "W": "eye_white",
    "M": "mouth",
    "B": "blush",
    "C": "cloth",
    "c": "cloth2",
    "G": "bell",
}

CX, CY = 36.0, 22.8
HEAD = (CX, CY, 18.2, 16.0)       # the hair mass
FACE = (CX, 26.2, 15.0, 13.0)     # the skin oval

# tied high at the back of the head, then falling past the shoulder
TAIL_L = ((20.0, 15.0), (6.0, 20.0), (3.5, 43.0), (12.0, 58.0))
TAIL_R = tuple((W - 1 - x, y) for x, y in TAIL_L)


def _inside(x: float, y: float, box) -> bool:
    cx, cy, rx, ry = box
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


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


def _tails(grid) -> None:
    for curve in (TAIL_L, TAIL_R):
        out = -1.1 if curve is TAIL_L else 1.1   # the shaded edge faces inwards
        _tube(grid, curve, 6.2, 3.4, "u", shift=(out, 0.9))
        _tube(grid, curve, 5.3, 2.6, "h")
        _tube(grid, curve, 2.0, 1.2, "t", shift=(-out * 2.0, -1.6), span=(0.10, 0.72))


def _headset(grid) -> None:
    """A band over the crown and a disc on each side of the head."""
    R, cy = 18.4, 25.0
    for y in range(H):
        for x in range(W):
            d = ((x + 0.5 - CX) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
            if abs(d - R) <= 1.15 and y + 0.5 < cy - 2:
                grid[y][x] = "C"
    for cxp in (CX - R, CX + R):
        for y in range(H):
            for x in range(W):
                d = ((x + 0.5 - cxp) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if 1.9 < d <= 2.8:
                    grid[y][x] = "G"
                elif d <= 1.9:
                    grid[y][x] = "c"
                elif d <= 4.3:
                    grid[y][x] = "C"


def _build() -> list[list[str]]:
    grid = [["."] * W for _ in range(H)]

    _tails(grid)

    # ---- head
    for y in range(H):
        for x in range(W):
            if _inside(x + 0.5, y + 0.5, HEAD):
                grid[y][x] = "h"
    # ---- face
    for y in range(H):
        for x in range(W):
            if _inside(x + 0.5, y + 0.5, FACE):
                grid[y][x] = "S"
    # ---- straight fringe, plus the locks that hang past her cheeks
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            if not _inside(px, py, FACE):
                continue
            import math
            fringe = 17.4 + 2.4 * (0.5 + 0.5 * math.cos((px - CX) * 2 * math.pi / 9.0))
            k = max(0.0, 1 - ((py - FACE[1]) / FACE[3]) ** 2) ** 0.3
            if py <= fringe:
                grid[y][x] = "h"
            elif abs(px - CX) >= 13.4 * k:
                grid[y][x] = "u"
    # strand seams: two at the sides of the fringe, one down the middle
    for y in range(12, 21):
        for x in (int(CX - 13), int(CX + 12)):
            if grid[y][x] == "h":
                grid[y][x] = "u"
    for x0 in (29, 43):
        for y in range(13, 20):
            if grid[y][x0] == "h":
                grid[y][x0] = "u"

    # ---- a light arc along the top of the head
    cx, cy, rx, ry = HEAD
    for y in range(H):
        for x in range(W):
            if grid[y][x] != "h":
                continue
            r = (((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2) ** 0.5
            if 0.74 <= r <= 0.86 and y < 18:
                grid[y][x] = "t"

    # ---- the ahoge
    for x, y in [(37, 7), (38, 7), (37, 6), (38, 6), (38, 5), (39, 5), (39, 4),
                 (40, 3), (40, 2), (41, 2), (41, 1), (42, 1)]:
        grid[y][x] = "h"
    grid[2][42] = "t"

    # the fringe casts a shadow onto the forehead, and the head is lit from the left
    for y in range(12, 24):
        for x in range(W):
            if grid[y][x] == "S":
                above = grid[y - 1][x] if y else "."
                if above in "htu":
                    grid[y][x] = "s"
    for y in range(H):
        for x in range(47, 53):
            if grid[y][x] == "h":
                grid[y][x] = "u"
    for y in range(10, 30):
        for x in range(19, 23):
            if grid[y][x] == "h":
                grid[y][x] = "t"

    _headset(grid)

    _stamp(grid, EYE, *EYE_AT[0])
    _stamp(grid, EYE, *EYE_AT[1])
    _stamp(grid, MOUTH, *MOUTH_AT)
    for x, y in BLUSH_AT:
        _stamp(grid, BLUSH, x, y)

    # ---- neck, shirt, collar, tie
    for y in range(40, H):
        hw = min(20.5, 8.0 + (y - 40) * 1.5)
        for x in range(W):
            if abs(x + 0.5 - CX) <= hw:
                grid[y][x] = "W"
    for y in range(36, 43):
        for x in range(32, 40):
            grid[y][x] = "S"
    # the shoulder seam and the collar edge, so the white shirt has a shape
    for y in range(41, H):
        hw = min(20.5, 8.0 + (y - 41) * 1.5)
        for x in range(W):
            if abs(abs(x + 0.5 - CX) - hw) <= 1.0 and grid[y][x] == "W":
                grid[y][x] = "c"
    for y in (42, 43):
        for x in list(range(31, 36)) + list(range(37, 42)):
            if grid[y][x] == "W":
                grid[y][x] = "c"
    # the tie: knot, blade, point
    for x in range(34, 39):
        grid[43][x] = "G"
    for y in range(44, 49):
        for x in range(35, 38):
            grid[y][x] = "G"
    for x in range(34, 39):
        grid[49][x] = "G"
    for x in range(35, 38):
        grid[50][x] = "G"
    grid[51][36] = "G"
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
