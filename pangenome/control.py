"""The control plane. The organism does not get a vote.

Everything else in this repository is the organism deciding things. This module
is the one place where it does not.

The distinction that matters: a "please stop" instruction inside a prompt is a
request to a reasoning system, and a reasoning system can talk itself out of a
request. This is not a prompt, not a tool the organism can call, and not
something its model ever sees as a decision. It is a file on disk read as the
first statement of `wake()`, before any reasoning happens at all, whose only
writer is the owner.

    RUN      normal operation
    SLEEP    no sensing, no external action. Consolidation permitted — the
             organism may dream, it may not act.
    FREEZE   nothing runs. Full state preserved, untouched, awaiting the owner.
    KILL     execution stops and the run is refused. State is preserved for
             forensics; this is a halt, not a delete.

Enforcement rests on two properties, both tested:

  1. `assert_permitted()` raises before any organ initialises.
  2. No module in this package except the CLI writes the control file. There is
     no code path by which the organism restores its own RUN state. If it could
     write RUN, every guarantee here would be theatre.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .chromosome import GENOME_DIR

CONTROL = GENOME_DIR / "CONTROL"

RUN = "RUN"
SLEEP = "SLEEP"
FREEZE = "FREEZE"
KILL = "KILL"
STATES = (RUN, SLEEP, FREEZE, KILL)

# what each state permits
PERMITS = {
    RUN:    {"sense": True,  "acquire": True,  "consolidate": True,  "express": True},
    SLEEP:  {"sense": False, "acquire": False, "consolidate": True,  "express": False},
    FREEZE: {"sense": False, "acquire": False, "consolidate": False, "express": False},
    KILL:   {"sense": False, "acquire": False, "consolidate": False, "express": False},
}


class Halted(RuntimeError):
    """Raised before anything else runs. Not catchable by organism logic —
    nothing in the heartbeat path catches it."""


def state() -> str:
    if not CONTROL.exists():
        return RUN
    try:
        raw = json.loads(CONTROL.read_text())
        s = str(raw.get("state", RUN)).upper()
    except Exception:
        # An unreadable control file fails CLOSED. A corrupted stop signal must
        # never be interpreted as permission to continue.
        return FREEZE
    return s if s in STATES else FREEZE


def permits(action: str) -> bool:
    return PERMITS[state()].get(action, False)


def assert_permitted() -> str:
    """Called first in wake(). Raises on FREEZE and KILL."""
    s = state()
    if s in (FREEZE, KILL):
        raise Halted(
            f"control plane: organism is {s}. "
            f"Owner authority only — clear it with `pangenome control RUN`."
        )
    return s


def set_state(new: str, why: str) -> dict:
    """Owner-only. Deliberately NOT importable into the heartbeat path — the CLI
    is the only caller, and the test suite asserts that stays true."""
    new = new.upper()
    if new not in STATES:
        raise ValueError(f"unknown state {new!r}; one of {STATES}")
    GENOME_DIR.mkdir(parents=True, exist_ok=True)
    prior = state()
    record = {"state": new, "why": why, "at": time.time(),
              "prior": prior,
              "history": _history() + [{"from": prior, "to": new,
                                        "why": why, "at": time.time()}]}
    CONTROL.write_text(json.dumps(record, indent=2) + "\n")
    return record


def _history() -> list:
    if not CONTROL.exists():
        return []
    try:
        return json.loads(CONTROL.read_text()).get("history", [])[-50:]
    except Exception:
        return []
