"""ASCII art: the frog, its moods, and the big title banner."""
from __future__ import annotations

import pyfiglet

# The whole frog is plain monospace, so a mood is just a different face row.
FROG_BODY = [
    "   @..@   ",
    "  (----)  ",
    " ( >__< ) ",
    " ^^ ~~ ^^ ",
]

FROG_FACES = {
    "idle": "   @..@   ",
    "blink": "   @--@   ",
    "happy": "   @^^@   ",
}

# Bubbles rising out of the water: (row offset, column offset, character)
BUBBLES = [
    [(0, 7, "o")],
    [(0, 7, "o"), (-1, 8, "o")],
    [(0, 7, "o"), (-1, 8, "o"), (-2, 9, ".")],
    [(-1, 8, "o"), (-2, 9, ".")],
]

# z's drifting off a sleeping frog
SLEEP_Z = [
    [(0, 8, "z")],
    [(0, 8, "z"), (-1, 9, "Z")],
    [(0, 8, "z"), (-1, 9, "Z"), (-2, 10, "z")],
    [(-1, 9, "Z"), (-2, 10, "z")],
]


def banner(text: str) -> list[str]:
    rows = pyfiglet.figlet_format(text, font="ansi_shadow", width=400).rstrip("\n").split("\n")
    rows = [r.rstrip() for r in rows]
    while rows and not rows[-1].strip():
        rows.pop()
    return rows
