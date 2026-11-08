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
    # the character
    hair="#5a4a7d",
    hair2="#7d69a8",
    skin="#f9e4da",
    skin2="#eccabc",
    ink="#241c33",
    iris="#7c5fd3",
    eye_white="#ffffff",
    mouth="#cf5a86",
    blush="#f3b4c8",
    cloth="#6f5aa8",
    cloth2="#a18fd6",
    bell="#e6b23c",
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
    hair="#b7a4e6",
    hair2="#e2d6ff",
    skin="#f7e4d9",
    skin2="#dcbfb2",
    ink="#181124",
    iris="#8f74d8",
    eye_white="#ffffff",
    mouth="#f08cb2",
    blush="#dc8fac",
    cloth="#8d76c9",
    cloth2="#b7a4e6",
    bell="#f2c766",
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
