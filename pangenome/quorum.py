"""Quorum sensing — coordination without a coordinator, and without messages.

Every decentralised agent framework still passes explicit messages *about the
decision*: proposals, votes, DAG-routed task descriptions, Byzantine-robust
ballots. There is always a protocol layer where agents talk about what to do.

Bacteria do not do this. Each cell secretes a small autoinducer molecule at a
constant rate and reads only the ambient concentration. When concentration
crosses threshold, every cell switches behaviour at once. No leader. No vote. No
proposal. No agent ever learns what any other agent decided — density *is* the
signal, and the medium does the computation.

Two properties fall out that voting does not give you:

  - cost is O(1) per agent regardless of population size
  - it degrades continuously: half a quorum produces half an effect, not a
    failed election

Autoinducers decay. That matters more than it looks: without decay the medium
integrates forever and every threshold eventually trips. Decay is what makes the
signal mean "right now" instead of "at some point in history".
"""

from __future__ import annotations

import math
import time

# half-life of a signal in the medium, seconds
DEFAULT_HALF_LIFE = 6 * 3600


class Medium:
    """The shared extracellular space. Agents write; nobody addresses anybody."""

    def __init__(self, store, half_life: float = DEFAULT_HALF_LIFE):
        self.store = store
        self.half_life = half_life

    def emit(self, species: str, emitter: str, amount: float = 1.0) -> None:
        self.store.emit(species, emitter, amount)

    def concentration(self, species: str, now: float | None = None) -> float:
        """Exponentially decayed sum over everything ever emitted."""
        now = now or time.time()
        rows = self.store.q(
            "SELECT at, amount FROM autoinducers WHERE species=?", (species,))
        lam = math.log(2) / self.half_life
        return sum(r["amount"] * math.exp(-lam * max(0.0, now - r["at"])) for r in rows)

    def quorate(self, species: str, threshold: float) -> bool:
        return self.concentration(species) >= threshold

    def response(self, species: str, threshold: float, hill: int = 4) -> float:
        """Graded 0..1 response. Cooperative binding makes the switch sharp
        without making it brittle — the thing a hard threshold gets wrong."""
        c = self.concentration(species)
        if c <= 0:
            return 0.0
        return (c ** hill) / (threshold ** hill + c ** hill)

    def census(self, species: str, window: float = 24 * 3600) -> int:
        """How many distinct emitters are contributing right now. This is the
        population size estimate the cell never has to be told."""
        cutoff = time.time() - window
        rows = self.store.q(
            "SELECT DISTINCT emitter FROM autoinducers WHERE species=? AND at>=?",
            (species, cutoff))
        return len(rows)
