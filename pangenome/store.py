"""Append-only substrate. SQLite, stdlib, one file.

Nothing here is ever UPDATEd or DELETEd. Corrections are new rows. The organism's
history is its genome; a genome you can rewrite is not a record of anything.

Two kinds of table:
  observations  — what the organism saw in the wild, timestamped (DATA)
  events        — what the organism did, and why (EVENTS + DECISIONS)
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

DEFAULT_DB = Path(os.environ.get("PANGENOME_DB", Path(__file__).resolve().parent.parent / "genome" / "culture.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    seen_at    REAL    NOT NULL,
    source     TEXT    NOT NULL,   -- 'mcp_registry' | 'github_skills' | ...
    locus      TEXT    NOT NULL,   -- stable id of the capability in that source
    name       TEXT,
    version    TEXT,
    signal     REAL,               -- adoption proxy: stars, installs, dependents
    payload    TEXT    NOT NULL    -- raw json snapshot
);
CREATE INDEX IF NOT EXISTS obs_locus ON observations(source, locus, seen_at);

CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL    NOT NULL,
    kind       TEXT    NOT NULL,   -- sense|acquire|reject|integrate|induce|excise|spacer|tick
    subject    TEXT,               -- plasmid id / locus
    reason     TEXT    NOT NULL,   -- every decision carries its why
    detail     TEXT                -- json
);
CREATE INDEX IF NOT EXISTS ev_kind ON events(kind, at);

CREATE TABLE IF NOT EXISTS plasmids (
    pid        TEXT PRIMARY KEY,
    acquired_at REAL NOT NULL,
    manifest   TEXT NOT NULL,      -- json
    state      TEXT NOT NULL,      -- lytic|lysogenic|excised
    fitness    REAL NOT NULL DEFAULT 0.0,
    trials     INTEGER NOT NULL DEFAULT 0,
    wins       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS spacers (          -- the CRISPR array
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    digest     TEXT NOT NULL UNIQUE,  -- sha256 of the offending payload
    locus      TEXT,
    harm       TEXT NOT NULL,         -- what it did
    severity   REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS spacer_shingles (  -- fuzzy half of the CRISPR array
    digest     TEXT NOT NULL,             -- FK to spacers.digest
    shard      TEXT NOT NULL,             -- one shingle hash of the payload
    PRIMARY KEY (digest, shard)
);
CREATE INDEX IF NOT EXISTS shingle_shard ON spacer_shingles(shard);

CREATE TABLE IF NOT EXISTS autoinducers (     -- the quorum medium
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    species    TEXT NOT NULL,
    emitter    TEXT NOT NULL,
    amount     REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ai_species ON autoinducers(species, at);

-- ---- the brain -----------------------------------------------------------

CREATE TABLE IF NOT EXISTS concepts (
    name       TEXT PRIMARY KEY,
    first_seen REAL NOT NULL,
    last_seen  REAL NOT NULL,
    count      INTEGER NOT NULL DEFAULT 1,
    base       REAL NOT NULL DEFAULT 0.0   -- learned salience weight; this is
);                                          -- the perceptual filter itself, and
                                            -- it changes with experience
CREATE TABLE IF NOT EXISTS edges (          -- associative memory
    a          TEXT NOT NULL,
    b          TEXT NOT NULL,
    weight     REAL NOT NULL DEFAULT 0.0,
    count      INTEGER NOT NULL DEFAULT 0,
    last_seen  REAL NOT NULL,
    PRIMARY KEY (a, b)
);
CREATE INDEX IF NOT EXISTS edge_a ON edges(a);

CREATE TABLE IF NOT EXISTS interests (      -- the owner model: standing priming
    concept    TEXT PRIMARY KEY,
    weight     REAL NOT NULL,
    why        TEXT NOT NULL,
    set_at     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (       -- raw experience. mortal by design
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    signature  TEXT NOT NULL,               -- what kind of thing happened
    concepts   TEXT NOT NULL,               -- json list
    detail     TEXT NOT NULL,               -- json
    strength   REAL NOT NULL DEFAULT 1.0,   -- Ebbinghaus S
    rehearsals INTEGER NOT NULL DEFAULT 0,
    consumed   INTEGER NOT NULL DEFAULT 0   -- promoted into a higher tier
);
CREATE INDEX IF NOT EXISTS ep_sig ON episodes(signature, consumed);

CREATE TABLE IF NOT EXISTS scaffold (       -- what survives the episodes
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    tier       TEXT NOT NULL,               -- pattern|abstraction|skill
    signature  TEXT NOT NULL,
    statement  TEXT NOT NULL,
    support    INTEGER NOT NULL,            -- episodes it was distilled from
    concepts   TEXT NOT NULL,
    parent     INTEGER                      -- the scaffold row it was built on
);
CREATE INDEX IF NOT EXISTS sc_tier ON scaffold(tier, signature);

CREATE TABLE IF NOT EXISTS attention_log (  -- for measuring opportunity precision
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    subject    TEXT NOT NULL,
    score      REAL NOT NULL,
    verdict    TEXT NOT NULL,
    reason     TEXT NOT NULL,
    useful     INTEGER                      -- NULL until the owner judges it
);
"""

# Every table that holds acquired state — i.e. everything an inherited clone
# must be able to shed. A new table added to SCHEMA and forgotten here is a
# clone that quietly keeps its ancestor's memories, so a test asserts this
# tuple covers the schema exactly.
ACQUIRED_TABLES = (
    "observations", "events", "episodes", "scaffold", "concepts",
    "edges", "interests", "autoinducers", "attention_log",
    "plasmids", "spacers", "spacer_shingles",
)


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    # -- writes ------------------------------------------------------------
    def observe(self, source: str, locus: str, name: str | None,
                version: str | None, signal: float | None, payload: dict) -> None:
        self.db.execute(
            "INSERT INTO observations(seen_at,source,locus,name,version,signal,payload)"
            " VALUES (?,?,?,?,?,?,?)",
            (time.time(), source, locus, name, version, signal, json.dumps(payload)),
        )

    def event(self, kind: str, reason: str, subject: str | None = None,
              detail: dict | None = None) -> None:
        self.db.execute(
            "INSERT INTO events(at,kind,subject,reason,detail) VALUES (?,?,?,?,?)",
            (time.time(), kind, subject, reason, json.dumps(detail or {})),
        )

    def put_plasmid(self, pid: str, manifest: dict, state: str) -> None:
        self.db.execute(
            "INSERT OR IGNORE INTO plasmids(pid,acquired_at,manifest,state)"
            " VALUES (?,?,?,?)",
            (pid, time.time(), json.dumps(manifest), state),
        )

    def set_state(self, pid: str, state: str) -> None:
        self.db.execute("UPDATE plasmids SET state=? WHERE pid=?", (state, pid))

    def record_trial(self, pid: str, won: bool, fitness: float) -> None:
        self.db.execute(
            "UPDATE plasmids SET trials=trials+1, wins=wins+?, fitness=? WHERE pid=?",
            (1 if won else 0, fitness, pid),
        )

    def add_spacer(self, digest: str, locus: str | None, harm: str, severity: float) -> None:
        self.db.execute(
            "INSERT OR IGNORE INTO spacers(at,digest,locus,harm,severity) VALUES (?,?,?,?,?)",
            (time.time(), digest, locus, harm, severity),
        )

    def emit(self, species: str, emitter: str, amount: float) -> None:
        self.db.execute(
            "INSERT INTO autoinducers(at,species,emitter,amount) VALUES (?,?,?,?)",
            (time.time(), species, emitter, amount),
        )

    def commit(self) -> None:
        self.db.commit()

    def close(self) -> None:
        try:
            self.db.close()
        except Exception:
            pass

    def __del__(self):
        self.close()

    # -- reads -------------------------------------------------------------
    def q(self, sql: str, args: tuple = ()) -> list[sqlite3.Row]:
        return list(self.db.execute(sql, args))

    def series(self, source: str, locus: str) -> list[tuple[float, float]]:
        rows = self.q(
            "SELECT seen_at, signal FROM observations WHERE source=? AND locus=?"
            " AND signal IS NOT NULL ORDER BY seen_at",
            (source, locus),
        )
        return [(r["seen_at"], r["signal"]) for r in rows]

    def loci(self, source: str | None = None) -> list[tuple[str, str]]:
        if source:
            rows = self.q(
                "SELECT DISTINCT source, locus FROM observations WHERE source=?", (source,))
        else:
            rows = self.q("SELECT DISTINCT source, locus FROM observations")
        return [(r["source"], r["locus"]) for r in rows]

    def plasmids(self, state: str | None = None) -> list[sqlite3.Row]:
        if state:
            return self.q("SELECT * FROM plasmids WHERE state=?", (state,))
        return self.q("SELECT * FROM plasmids")

    def has_spacer(self, digest: str) -> bool:
        return bool(self.q("SELECT 1 FROM spacers WHERE digest=?", (digest,)))

    def add_spacer_shingles(self, digest: str, shards: set[str]) -> None:
        for s in shards:
            self.db.execute(
                "INSERT OR IGNORE INTO spacer_shingles(digest, shard) VALUES (?,?)",
                (digest, s))

    def best_spacer_similarity(self, shards: set[str]) -> float:
        """Highest Jaccard similarity between the given shingle sketch and any
        stored spacer's sketch. 0.0 when nothing overlaps.

        Both sides are bottom-k sketches (the k smallest hashes of a payload's
        shingles), so the estimator is the bottom-k one: take the k smallest
        hashes of the two sketches combined and ask what fraction of them are
        in both. Comparing the truncated sets directly would be biased low,
        because each side's tail was cut off independently."""
        if not shards:
            return 0.0
        marks = ",".join("?" * len(shards))
        cands = self.q(
            f"SELECT DISTINCT digest FROM spacer_shingles WHERE shard IN ({marks})",
            tuple(shards))
        best = 0.0
        for r in cands:
            stored = {x["shard"] for x in self.q(
                "SELECT shard FROM spacer_shingles WHERE digest=?", (r["digest"],))}
            if not stored:
                continue
            k = min(len(stored), len(shards))
            window = sorted(stored | shards)[:k]
            hits = sum(1 for s in window if s in stored and s in shards)
            best = max(best, hits / len(window))
        return best

    def clear_all(self) -> None:
        """Wipe every acquired-state table. Used by `germinate --fresh` so a
        template clone can shed the ancestor's memories in one step. The
        chromosome files on disk are NOT touched here — identity is
        re-created by germinate itself, and this method must never be
        reachable from the organism's own loop."""
        for t in ACQUIRED_TABLES:
            self.db.execute(f"DELETE FROM {t}")
        self.commit()
