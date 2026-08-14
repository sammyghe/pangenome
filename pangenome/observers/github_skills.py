"""GitHub — where capability packets actually recombine.

SKILL.md is now loaded by several unrelated agent runtimes. That makes a skill
repo a textbook mobile element: self-contained, portable across hosts with no
shared ancestry, and forked-then-edited rather than inherited. A fork is a
replication event with mutation; a star is an adoption proxy.

Fork counts are the more biologically faithful signal (they are replication),
stars the more responsive one (they are exposure). Both are recorded; the
epidemiology layer uses stars as the default signal and forks as the generation
counter.
"""

from __future__ import annotations

import os
import urllib.parse

from ..safety import fetch_json

SEARCH = "https://api.github.com/search/repositories"

# Each query is a separate transmission route through the ecosystem. Measuring
# them apart is the point — a capability that spreads through one route and not
# the others is telling you something about the route, not the capability.
ROUTES = [
    ("skills", "claude skills in:name,description,readme"),
    ("mcp", "topic:mcp-server"),
    ("agent-skills", "topic:agent-skills"),
    ("plugins", "claude code plugin in:name,description"),
]


class GithubSkills:
    name = "github_skills"

    def __init__(self, store, per_page: int = 50):
        self.store = store
        self.per_page = per_page
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def sense(self) -> int:
        seen = 0
        # A locus that appears on several routes is one observation, not several.
        # Recording it twice inside one beat would fabricate a time series out of
        # a single snapshot — the exact error the daily() collapse also guards.
        recorded: set[str] = set()
        for route, query in ROUTES:
            q = urllib.parse.urlencode(
                {"q": query, "sort": "stars", "order": "desc", "per_page": self.per_page})
            try:
                data = fetch_json(f"{SEARCH}?{q}", token=self.token)
            except ConnectionError as e:
                self.store.event("sense", f"github route {route} unreachable: {e}",
                                 subject=self.name)
                continue

            for repo in data.get("items", []):
                if repo["full_name"] in recorded:
                    continue
                recorded.add(repo["full_name"])
                self.store.observe(
                    source=self.name,
                    locus=repo["full_name"],
                    name=repo["name"],
                    version=repo.get("pushed_at"),
                    signal=float(repo.get("stargazers_count") or 0),
                    payload={
                        "route": route,
                        "forks": repo.get("forks_count"),
                        "watchers": repo.get("watchers_count"),
                        "open_issues": repo.get("open_issues_count"),
                        "created_at": repo.get("created_at"),
                        "pushed_at": repo.get("pushed_at"),
                        "license": (repo.get("license") or {}).get("spdx_id"),
                        "description": (repo.get("description") or "")[:600],
                        "topics": repo.get("topics", []),
                    },
                )
                seen += 1

        self.store.event("sense", f"github: {seen} loci observed across {len(ROUTES)} routes",
                         subject=self.name, detail={"count": seen})
        self.store.commit()
        return seen
