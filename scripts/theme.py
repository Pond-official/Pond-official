"""Two palettes: pale lavender by day, deep violet at night.

One hue does almost all the work - the accent is a single violet, and every
neutral carries a little of it so the whole page feels like the same paper.
"""

LIGHT = dict(
    name="light",
    base="#fdfbff",
    mantle="#f5f0fd",
    crust="#ece4f8",
    surface0="#ded3f0",
    surface2="#b9a8d8",
    text="#231a33",
    subtext0="#5b5175",
    overlay1="#8b80a6",
    overlay0="#b5aac9",
    # emphasis ramp: fg is the darkest, fg3 the lightest
    fg="#2b2140",
    fg2="#4c4166",
    fg3="#d8cdee",
    mute="#7a6d96",
    accent="#8b5cf6",
    accent2="#c3a6f7",
    # the character: Miku - teal hair, cyan eyes, white shirt, grey headset
    hair="#35bfb5",
    hair2="#7fe8de",
    hair3="#1b8b84",
    skin="#fbe7dd",
    skin2="#eccdbf",
    ink="#1d2b39",
    iris="#17a3bd",
    eye_white="#ffffff",
    mouth="#d9577f",
    blush="#f6b8cb",
    cloth="#3c4154",
    cloth2="#eef5f6",
    bell="#39c5bb",
    # heat levels 0..4 for the contribution grid
    heat=["#f3edfd", "#d9c9f7", "#b294ee", "#8259dd", "#4c2b9e"],
    shadow="#2b2140",
)

DARK = dict(
    name="dark",
    base="#141020",
    mantle="#1b1629",
    crust="#0d0a15",
    surface0="#332b47",
    surface2="#4d4170",
    text="#f2ecff",
    subtext0="#b6aad2",
    overlay1="#8f83ab",
    overlay0="#645a7e",
    fg="#f4eeff",
    fg2="#d2c6ee",
    fg3="#3b3157",
    mute="#a89cc6",
    accent="#b18cf8",
    accent2="#d8c2ff",
    hair="#4fd8cd",
    hair2="#8ff0e7",
    hair3="#2a9a93",
    skin="#f7e4d9",
    skin2="#dcbfb2",
    ink="#16202e",
    iris="#4ec3e8",
    eye_white="#ffffff",
    mouth="#f08cb2",
    blush="#dc8fac",
    cloth="#4a5068",
    cloth2="#e8f2f3",
    bell="#5fdcd2",
    heat=["#241d36", "#3d3159", "#6b53a8", "#9b7ae0", "#cdb4fb"],
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
