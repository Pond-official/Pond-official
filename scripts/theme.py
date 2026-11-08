"""Two palettes: paper by day, pond at night.

Every colour used by the cards lives here, so a new look is one dict away.
"""

LIGHT = dict(
    name="light",
    base="#fbfbf7",
    mantle="#f1f1ea",
    crust="#e3e3da",
    surface0="#d8d8cf",
    surface2="#b6b6ab",
    text="#20262c",
    subtext0="#565e66",
    overlay1="#868e96",
    overlay0="#a9b0b6",
    jade="#0f766e",
    jade2="#14b8a6",
    amber="#b45309",
    amber2="#d97706",
    blue="#1d4ed8",
    plum="#6d28d9",
    rose="#be123c",
    # heat levels 0..4 for the contribution grid
    heat=["#e4e4dc", "#a9dbd2", "#5cb9aa", "#1e8d7b", "#0d6a5b"],
    shadow="#20262c",
)

DARK = dict(
    name="dark",
    base="#0d1117",
    mantle="#161b22",
    crust="#090c10",
    surface0="#2b323b",
    surface2="#3d4650",
    text="#dbe4ec",
    subtext0="#9fabb6",
    overlay1="#76818c",
    overlay0="#58626c",
    jade="#5eead4",
    jade2="#2dd4bf",
    amber="#fbbf24",
    amber2="#f59e0b",
    blue="#7aa2f7",
    plum="#b69cff",
    rose="#f7768e",
    heat=["#1a1f26", "#1e433f", "#2a7b6f", "#47b09d", "#8be8d5"],
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
