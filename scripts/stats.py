"""Read the public numbers for the profile cards from the GitHub GraphQL API."""
from __future__ import annotations

import json
import os
import random
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone

ENDPOINT = "https://api.github.com/graphql"
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

PROFILE = """
query ($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    following { totalCount }
    all: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
    own: repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      nodes {
        name
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

YEAR = """
query ($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def _query(q: str, variables: dict, token: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"query": q, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "pond-profile",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(f"GitHub API said: {payload['errors']}")
    return payload["data"]


def _runs(days: list[tuple[str, int]]) -> tuple[int, int]:
    """(current streak, best streak) over days with at least one contribution."""
    best = run = 0
    for _, n in days:
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    tail = days[::-1]
    if tail and tail[0][1] == 0:  # today is not over yet
        tail = tail[1:]
    current = 0
    for _, n in tail:
        if n == 0:
            break
        current += 1
    return current, best


def fetch(login: str, ignore: list[str]) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set (use --sample to preview locally)")

    user = _query(PROFILE, {"login": login}, token)["user"]
    cc = user["contributionsCollection"]
    weeks = [[(d["date"], LEVEL[d["contributionLevel"]], d["contributionCount"]) for d in w["contributionDays"]]
             for w in cc["contributionCalendar"]["weeks"]]

    # contributionsCollection only looks one year back, so walk the whole
    # account history in 365-day chunks to find the longest streak ever.
    created = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    seen: dict[str, int] = {}
    start = created
    while start < now:
        end = min(start + timedelta(days=365), now)
        chunk = _query(YEAR, {"login": login, "from": start.isoformat(), "to": end.isoformat()}, token)
        for w in chunk["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                seen[d["date"]] = d["contributionCount"]
        start = end
    current, best = _runs(sorted(seen.items()))

    skip = {name.lower() for name in ignore}
    languages: Counter = Counter()
    stars = 0
    for repo in user["own"]["nodes"]:
        stars += repo["stargazerCount"]
        if repo["name"].lower() in skip:
            continue
        for edge in repo["languages"]["edges"]:
            languages[edge["node"]["name"]] += edge["size"]

    stats = {
        "days": (now.date() - created.date()).days,
        "repos": user["all"]["totalCount"],
        "stars": stars,
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "followers": user["followers"]["totalCount"],
        "following": user["following"]["totalCount"],
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "current": current,
        "best": best,
        "languages": languages.most_common(),
        "weeks": weeks,
    }
    line = (f"{stats['repos']} public repos, {stats['stars']} stars, "
            f"{stats['contributions']} contributions this year, streak {current} (best {best})")
    print("  " + line)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::notice title=Profile stats::{line}")
    return stats


def sample() -> dict:
    """Made-up but plausible numbers, so the layout can be previewed offline."""
    rnd = random.Random(7)
    today = date.today()
    start = today - timedelta(days=364 + (today.weekday() + 1) % 7)
    weeks, week, d = [], [], start
    while d <= today:
        n = 0 if rnd.random() < 0.55 else rnd.choice([1, 1, 2, 3, 4, 6])
        week.append((d.isoformat(), 0 if n == 0 else min(4, 1 + n // 2), n))
        if len(week) == 7:
            weeks.append(week)
            week = []
        d += timedelta(days=1)
    if week:
        weeks.append(week)
    total = sum(n for w in weeks for _, _, n in w)
    return {
        "days": 750, "repos": 2, "stars": 1, "commits": 214, "prs": 1, "issues": 2,
        "followers": 3, "following": 4, "contributions": total, "current": 4, "best": 23,
        "languages": [("TypeScript", 320_000), ("Python", 90_000), ("HTML", 12_000), ("CSS", 8_000)],
        "weeks": weeks,
    }
