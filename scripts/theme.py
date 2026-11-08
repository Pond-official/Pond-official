"""Two palettes: paper by day, plum night by evening.

Every colour used by the cards lives here, so a new look is one dict away.
"""

LIGHT = dict(
    name="light",
    base="#fdfbfc",
    mantle="#f6f0f3",
    crust="#e9dfe4",
    surface0="#dbd0d6",
    surface2="#b9aeb4",
    text="#2b2330",
    subtext0="#5f5560",
    overlay1="#8b8189",
    overlay0="#aca2a9",
    sakura="#d4537e",
    sakura2="#f07fa8",
    plum="#7c4dba",
    plum2="#9d6fe0",
    gold="#b07d18",
    gold2="#d9a520",
    sky="#3b6fd4",
    # the character
    hair="#3a3347",
    skin="#efd2c0",
    ink="#2a2531",
    eye_light="#fdfbfc",
    mouth="#d4537e",
    blush="#f4b8c8",
    cloth="#7c5cbf",
    bell="#e0a33a",
    # heat levels 0..4 for the contribution grid
    heat=["#ecdde3", "#e3a8c0", "#d4789f", "#b8457d", "#8c2c5c"],
    shadow="#2b2330",
)

DARK = dict(
    name="dark",
    base="#14111a",
    mantle="#1c1826",
    crust="#0d0b12",
    surface0="#322b3d",
    surface2="#453b52",
    text="#ece4f2",
    subtext0="#b3a7bd",
    overlay1="#867a92",
    overlay0="#655a70",
    sakura="#f58fb4",
    sakura2="#ffa8c8",
    plum="#c3a2ff",
    plum2="#d7bcff",
    gold="#f0c05a",
    gold2="#ffd47a",
    sky="#8ab4ff",
    hair="#cdb0e6",
    skin="#f2ddcf",
    ink="#241f2b",
    eye_light="#ffffff",
    mouth="#f277a8",
    blush="#e88fb8",
    cloth="#9d7bea",
    bell="#f0c05a",
    heat=["#241f2d", "#4a2b3d", "#8a3f61", "#c25c88", "#f087b0"],
    shadow="#000000",
)

THEMES = {"light": LIGHT, "dark": DARK}


def mix(a: str, b: str, t: float) -> str:
    """Blend two #rrggbb colours, t=0 gives a."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def ramp(stops: list[str], t: float) -> str:
    """Colour at position t (0..1) across several stops."""
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    pos = t * (len(stops) - 1)
    i = int(pos)
    return mix(stops[i], stops[i + 1], pos - i)
