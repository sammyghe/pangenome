"""The official MCP registry — the clearest view of the accessory genome.

Every entry here is executable third-party code that agents load with the host's
privileges. In population terms it is a plasmid pool with no restriction system:
listings carry no signature the consuming agent verifies, and installation is
routinely a one-line fetch-and-run.

The organism reads it the way an epidemiologist reads a case line list: who is
present, at what version, on what date. The version field is the important one —
a version bump is a replication event, and replication events are what let you
measure a generation interval at all.
"""

from __future__ import annotations

from ..safety import fetch_json

BASE = "https://registry.modelcontextprotocol.io/v0/servers"


class McpRegistry:
    name = "mcp_registry"

    def __init__(self, store, page_limit: int = 5, page_size: int = 100):
        self.store = store
        self.page_limit = page_limit
        self.page_size = page_size

    def sense(self) -> int:
        seen = 0
        cursor = None
        # Pagination can repeat a locus across pages. One beat, one observation.
        recorded: set[str] = set()
        for _ in range(self.page_limit):
            url = f"{BASE}?limit={self.page_size}"
            if cursor:
                url += f"&cursor={cursor}"
            try:
                data = fetch_json(url)
            except ConnectionError as e:
                self.store.event("sense", f"mcp registry unreachable: {e}",
                                 subject=self.name)
                break

            servers = data.get("servers") or data.get("data") or []
            for entry in servers:
                s = entry.get("server", entry)
                locus = s.get("name") or s.get("id")
                if not locus or locus in recorded:
                    continue
                recorded.add(locus)
                meta = entry.get("_meta", {}) or {}
                official = meta.get("io.modelcontextprotocol.registry/official", {}) or {}
                # No install-count is published, so presence-with-version is the
                # honest proxy: cumulative distinct versions observed is a lower
                # bound on replication events for that locus.
                self.store.observe(
                    source=self.name,
                    locus=locus,
                    name=s.get("title") or locus.split("/")[-1],
                    version=s.get("version"),
                    signal=float(self._version_ordinal(locus, s.get("version"))),
                    payload={
                        "description": (s.get("description") or "")[:600],
                        "repository": s.get("repository", {}),
                        "packages": [p.get("registryType") for p in s.get("packages", [])],
                        "remotes": [r.get("type") for r in s.get("remotes", [])],
                        "status": official.get("status") or s.get("status"),
                        "published_at": official.get("publishedAt"),
                    },
                )
                seen += 1

            cursor = (data.get("metadata") or {}).get("nextCursor") or \
                     (data.get("metadata") or {}).get("next_cursor")
            if not cursor:
                break

        self.store.event("sense", f"mcp registry: {seen} loci observed", subject=self.name,
                         detail={"count": seen})
        self.store.commit()
        return seen

    def _version_ordinal(self, locus: str, version: str | None) -> int:
        """Cumulative distinct versions seen for this locus — a replication count."""
        if not version:
            return 1
        rows = self.store.q(
            "SELECT DISTINCT version FROM observations WHERE source=? AND locus=?"
            " AND version IS NOT NULL",
            (self.name, locus))
        known = {r["version"] for r in rows}
        known.add(version)
        return len(known)
