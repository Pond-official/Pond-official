"""Draw every picture used by README.md.

    python scripts/generate.py                     # everything (needs GITHUB_TOKEN)
    python scripts/generate.py --static            # only what needs no GitHub data
    python scripts/generate.py --sample --out ./p  # fake numbers, local preview
"""
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cards  # noqa: E402
import stats as gh  # noqa: E402
from theme import THEMES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def save(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")  # LF everywhere: no churn on CI
    print(f"  {path.relative_to(path.parent.parent)}  ({len(svg) // 1024} KB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", action="store_true", help="skip the cards that need GitHub data")
    ap.add_argument("--sample", action="store_true", help="made-up numbers, for local preview")
    ap.add_argument("--out", default=str(ROOT), help="where assets/ and profile/ go")
    a = ap.parse_args()

    with open(ROOT / "config.toml", "rb") as f:
        cfg = tomllib.load(f)
    out = Path(a.out)

    numbers = None
    if not a.static:
        if a.sample:
            numbers = gh.sample()
        else:
            print("reading GitHub ...")
            numbers = gh.fetch(cfg["profile"]["github"], cfg["neofetch"].get("exclude_repos", []))

    for name, pal in THEMES.items():
        print(f"[{name}]")
        save(out / "assets" / f"header-{name}.svg", cards.header(cfg, pal))
        save(out / "assets" / f"stack-{name}.svg", cards.stack(cfg, pal))
        save(out / "assets" / f"footer-{name}.svg", cards.footer(cfg, pal))
        for badge in cfg["badges"]:
            save(out / "assets" / f"badge-{badge['name']}-{name}.svg",
                 cards.badge(badge["label"], badge["value"], badge["color"], pal))
        if numbers:
            save(out / "profile" / f"neofetch-{name}.svg", cards.neofetch(cfg, pal, numbers))
            save(out / "profile" / f"activity-{name}.svg", cards.activity(cfg, pal, numbers))


if __name__ == "__main__":
    main()
