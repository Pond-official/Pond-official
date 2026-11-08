"""Two palettes: paper white by day, ink black at night.

Monochrome on purpose - one muted red carries every accent.
"""

LIGHT = dict(
    name="light",
    base="#ffffff",
    mantle="#f5f5f5",
    crust="#e6e6e6",
    surface0="#d6d6d6",
    surface2="#b3b3b3",
    text="#111111",
    subtext0="#5a5a5a",
    overlay1="#8c8c8c",
    overlay0="#b8b8b8",
    # emphasis ramp: fg is the darkest, fg3 the lightest
    fg="#111111",
    fg2="#3d3d3d",
    fg3="#cfcfcf",
    mute="#7d7d7d",
    accent="#c2453c",
    accent2="#e07a72",
    # the character
    hair="#1b1b1b",
    hair2="#454545",
    skin="#efefef",
    skin2="#dcdcdc",
    ink="#111111",
    eye_white="#ffffff",
    mouth="#2b2b2b",
    blush="#d8d8d8",
    cloth="#2e2e2e",
    cloth2="#4a4a4a",
    bell="#c2453c",
    # heat levels 0..4 for the contribution grid
    heat=["#ececec", "#c9c9c9", "#8e8e8e", "#4a4a4a", "#161616"],
    shadow="#111111",
)

DARK = dict(
    name="dark",
    base="#0b0b0b",
    mantle="#161616",
    crust="#050505",
    surface0="#2d2d2d",
    surface2="#454545",
    text="#f5f5f5",
    subtext0="#a5a5a5",
    overlay1="#787878",
    overlay0="#585858",
    fg="#f5f5f5",
    fg2="#cfcfcf",
    fg3="#3a3a3a",
    mute="#9a9a9a",
    accent="#e06a60",
    accent2="#f09a92",
    hair="#a3a3a3",
    hair2="#cfcfcf",
    skin="#e9e9e9",
    skin2="#cfcfcf",
    ink="#111111",
    eye_white="#ffffff",
    mouth="#2b2b2b",
    blush="#bdbdbd",
    cloth="#d4d4d4",
    cloth2="#a8a8a8",
    bell="#e06a60",
    heat=["#1d1d1d", "#3a3a3a", "#6b6b6b", "#a3a3a3", "#e8e8e8"],
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
