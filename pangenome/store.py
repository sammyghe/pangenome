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

CREATE TABLE IF NOT EXISTS autoinducers (     -- the quorum medium
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         REAL NOT NULL,
    species    TEXT NOT NULL,
    emitter    TEXT NOT NULL,
    amount     REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ai_species ON autoinducers(species, at);
"""


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
