"""A tiny SVG canvas plus the two animation idioms used by every card.

GitHub shows README images as <img>, so there is no script and no web font:
everything has to be static markup plus CSS keyframes baked into the file.
"""
from __future__ import annotations

from xml.sax.saxutils import escape


class Canvas:
    def __init__(self, width: float, height: float):
        self.w, self.h = width, height
        self.css: list[str] = []
        self._keys: set[str] = set()
        self.defs: dict[str, str] = {}
        self.body: list[str] = []
        self._seq = 0

    def uid(self, prefix: str = "u") -> str:
        self._seq += 1
        return f"{prefix}{self._seq}"

    def add(self, *parts: str) -> None:
        self.body.extend(p for p in parts if p)

    def style(self, css: str, key: str | None = None) -> None:
        if key is not None:
            if key in self._keys:
                return
            self._keys.add(key)
        self.css.append(css)

    def define(self, ident: str, content: str) -> None:
        if ident not in self.defs:
            self.defs[ident] = content

    def svg(self, title: str) -> str:
        t = escape(title, {'"': "&quot;"})
        css = "".join(self.css) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:g}" height="{self.h:g}" '
            f'viewBox="0 0 {self.w:g} {self.h:g}" role="img" aria-label="{t}">'
            f"<title>{t}</title><style>{css}</style>"
            f'<defs>{"".join(self.defs.values())}</defs>'
            f'{"".join(self.body)}</svg>'
        )


class Clock:
    """Visibility windows inside one looping animation.

    Every element that appears and disappears gets a class whose keyframes
    say when it is on. `static` decides what shows when CSS animation is off.
    """

    def __init__(self, canvas: Canvas, total: float, name: str):
        self.c, self.total, self.name = canvas, total, name
        self._cache: dict[tuple, str] = {}

    def show(self, start: float, end: float, static: bool = False) -> str:
        key = (round(start, 3), round(end, 3), static)
        if key in self._cache:
            return self._cache[key]
        cls = f"{self.name}{len(self._cache)}"
        a = max(0.0, start) / self.total * 100
        b = min(end, self.total) / self.total * 100
        kf = ["0%{opacity:0}"] if a > 0 else []
        kf.append(f"{a:.3f}%{{opacity:1}}")
        if b < 100:
            kf.append(f"{b:.3f}%{{opacity:0}}")
            kf.append("100%{opacity:0}")
        self.c.style(
            f".{cls}{{opacity:{1 if static else 0};animation:{cls}k {self.total:.2f}s step-end infinite}}"
            f"@keyframes {cls}k{{{''.join(kf)}}}"
        )
        self._cache[key] = cls
        return cls


def frames(canvas: Canvas, name: str, timeline: list[tuple[int, float]], count: int) -> list[str]:
    """Flip-book animation built from static frames.

    timeline holds (frame index, seconds) played in a loop; frame k is only
    visible during its own slots. Returns the class name of every frame.
    """
    total = sum(d for _, d in timeline)
    classes: list[str] = []
    for k in range(count):
        cls = f"{name}{k}"
        slots, t = [], 0.0
        for idx, d in timeline:
            a, b = t / total * 100, (t + d) / total * 100
            if idx == k:
                slots.append((a, b))
            t += d
        if not slots:
            canvas.style(f".{cls}{{opacity:0}}")
            classes.append(cls)
            continue
        kf, end = [], 0.0
        for a, b in slots:
            if a > end + 1e-6:
                kf += [f"{end:.3f}%{{opacity:0}}", f"{a:.3f}%{{opacity:0}}"]
            kf += [f"{a:.3f}%{{opacity:1}}", f"{b:.3f}%{{opacity:1}}"]
            end = b
        if end < 100:
            kf += [f"{end:.3f}%{{opacity:0}}", "100%{opacity:0}"]
        canvas.style(
            f"@keyframes {cls}{{{''.join(kf)}}}"
            f".{cls}{{animation:{cls} {total:.2f}s step-end infinite}}"
        )
        classes.append(cls)
    return classes
