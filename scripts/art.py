"""Text art: the big title banner and the z's that drift off a sleeper."""
from __future__ import annotations

import pyfiglet

# z's drifting up: (row offset, column offset, character)
SLEEP_Z = [
    [(0, 0, "z")],
    [(0, 0, "z"), (-1, 2, "Z")],
    [(0, 0, "z"), (-1, 2, "Z"), (-2, 4, "z")],
    [(-1, 2, "Z"), (-2, 4, "z")],
]


def banner(text: str) -> list[str]:
    rows = pyfiglet.figlet_format(text, font="ansi_shadow", width=400).rstrip("\n").split("\n")
    rows = [r.rstrip() for r in rows]
    while rows and not rows[-1].strip():
        rows.pop()
    return rows
