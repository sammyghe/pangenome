"""Export the organism's real state for the visual explorer.

The explorer shipped as a static mockup with hand-written numbers. That is the
one thing this project cannot do: RESULTS.md §0 is a real-vs-fixture table and
CONSTITUTION §8 requires honest instruments, so a dashboard that prints
plausible invented figures next to measured ones destroys the only thing that
makes the rest of the repository worth reading.

So the explorer reads from here instead. `export()` writes `explorer/data.json`
straight from the live store, and it is called on every heartbeat — the
organism updates its own dashboard as part of the beat, and the committed JSON
is therefore never staler than the last commit.

Everything emitted here carries provenance. `live` blocks are measured from the
genome. `fixture` blocks come from the hand-built shop in experiment.py and are
labelled as such so the page can badge them. Nothing is invented anywhere.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

EXPLORER = Path(__file__).resolve().parent.parent / "explorer" / "data.json"


def export(store, chromosome=None, path: Path | None = None) -> dict:
    """Snapshot the live genome as JSON for the explorer page."""
    path = Path(path) if path else EXPLORER

    # Every read here is defensive. The dashboard is a read-out, not an organ:
    # a missing table or a damaged row must degrade one panel, never cost the
    # heartbeat that called it.
    def rows(sql: str, args: tuple = ()) -> list:
        try:
            return store.q(sql, args)
        except Exception:
            return []

    def count(table: str) -> int:
        r = rows(f"SELECT COUNT(*) n FROM {table}")
        return r[0]["n"] if r else 0

    d_rows = rows(
        "SELECT COUNT(DISTINCT CAST(seen_at/86400 AS INTEGER)) d FROM observations")
    days = d_rows[0]["d"] if d_rows and count("observations") else 0

    last_beat = rows("SELECT at FROM events WHERE kind='tick' ORDER BY at DESC LIMIT 1")
    beat_at = last_beat[0]["at"] if last_beat else None

    # what the attention field flagged, unprompted, most recently
    noticed = [
        {"subject": r["subject"], "score": round(r["score"], 3),
         "verdict": r["verdict"], "reason": r["reason"]}
        for r in rows(
            "SELECT subject, score, verdict, reason FROM attention_log"
            " WHERE verdict IN ('investigate','interrupt')"
            " ORDER BY at DESC LIMIT 8")
    ]

    skills = [
        {"tier": r["tier"], "statement": r["statement"], "support": r["support"]}
        for r in rows(
            "SELECT tier, statement, support FROM scaffold"
            " ORDER BY support DESC LIMIT 8")
    ]

    interests = [
        {"concept": r["concept"], "weight": r["weight"], "why": r["why"]}
        for r in rows(
            "SELECT concept, weight, why FROM interests ORDER BY weight DESC LIMIT 12")
    ]

    spacers = [
        {"locus": r["locus"], "harm": r["harm"], "severity": r["severity"]}
        for r in rows(
            "SELECT locus, harm, severity FROM spacers ORDER BY at DESC LIMIT 8")
    ]

    # the outbreak table, computed the same way `watch` computes it
    try:
        from . import epidemiology
        table = epidemiology.outbreak_table(store)[:8]
    except Exception:
        table = []
    outbreaks = [
        {"locus": t["locus"], "source": t.get("source"),
         "R0": t.get("R0"), "lifetime_r": t.get("lifetime_r"),
         "distinct_days": t.get("distinct_days"), "signal": t.get("signal"),
         "phase": t.get("phase"),
         # A row that travels without its confidence will be misread.
         "confidence": t.get("confidence"),
         "days_until_indicative": t.get("days_until_indicative")}
        for t in table
    ]

    plasmids = [
        {"pid": r["pid"], "state": r["state"], "fitness": r["fitness"]}
        for r in rows("SELECT pid, state, fitness FROM plasmids LIMIT 40")
    ]

    payload = {
        "provenance": "LIVE — measured from genome/culture.db by pangenome.dashboard",
        "generated_at": time.time(),
        "generated_at_utc": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "last_beat_utc": (time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(beat_at))
                          if beat_at else None),
        "identity": {
            "name": (chromosome.name if chromosome and chromosome.alive else "unknown"),
            "steward": ((chromosome.data or {}).get("steward")
                        if chromosome and chromosome.alive else None),
            "root_pubkey": ((chromosome.data or {}).get("root_pubkey", "")[:16] + "…"
                            if chromosome and chromosome.alive else None),
            "dependencies": 0,
        },
        "live": {
            "observations": count("observations"),
            "concepts": count("concepts"),
            "edges": count("edges"),
            "episodes": count("episodes"),
            "scaffold": count("scaffold"),
            "plasmids": count("plasmids"),
            "spacers": count("spacers"),
            "interests": count("interests"),
            "attention_log": count("attention_log"),
            "distinct_days": days,
        },
        "noticed_unprompted": noticed,
        "scaffold": skills,
        "interests": interests,
        "spacers": spacers,
        "outbreaks": outbreaks,
        "plasmid_states": plasmids,
        # Measured in RESULTS.md; these are results of real runs, not estimates.
        # Kept here so the page never has to hardcode a number.
        "study": {
            "provenance": "MEASURED — RESULTS.md §5, reproducible via `pangenome study`",
            "token_reduction_live_corpus": 0.972,
            "arms": [
                {"arm": "A · literal", "tokens_in": 626, "targets_mean": 0.0,
                 "targets_total": 2, "stable": True},
                {"arm": "B · prompted", "tokens_in": 652, "targets_mean": 0.75,
                 "targets_total": 2, "stable": False},
                {"arm": "C · organism", "tokens_in": 248, "targets_mean": 2.0,
                 "targets_total": 2, "stable": True},
            ],
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
