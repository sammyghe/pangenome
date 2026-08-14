"""Quasispecies — what identity means once code forks and recombines.

Current answers to "is this still the same agent" are "same weights" or "same
memory file". Both break the moment a capability is forked, edited and merged
back, which in the live agent-skill ecosystem is the normal case, not the edge
case.

RNA viruses do not have this problem, because they never had a single genome to
lose. A viral population is a mutant swarm: a cloud of variants distributed
around a consensus sequence, replicating at the edge of the error threshold.
Identity is the *distribution*, not any member of it. No individual sequence is
the virus.

Two hard constraints come with that, and they are the useful part:

  ERROR THRESHOLD   above a critical mutation rate the consensus dissolves and
                    information is lost — error catastrophe. Below it, the swarm
                    cannot explore. Adaptability has a ceiling set by genome
                    length: roughly mu_max ~ 1/L per replication.

  CONSENSUS IS THIN Erwin's caution applies: a consensus sequence is a minimal
                    and often insufficient description of the population. So the
                    organism reports the swarm's *diversity* alongside its
                    consensus, and treats low diversity as a fragility warning
                    rather than as health.
"""

from __future__ import annotations

import math
from collections import Counter


class Swarm:
    """A population of variants of one capability, with fitness weights."""

    def __init__(self, name: str):
        self.name = name
        self.variants: dict[str, tuple[dict, float]] = {}   # pid -> (traits, fitness)

    def add(self, pid: str, traits: dict, fitness: float = 0.0) -> None:
        self.variants[pid] = (traits, max(0.0, fitness))

    # -- identity ----------------------------------------------------------
    def consensus(self) -> dict:
        """Fitness-weighted majority per trait. This is the organism's answer to
        'what is this capability', and no single variant has to be it."""
        out: dict = {}
        keys = {k for traits, _ in self.variants.values() for k in traits}
        for k in keys:
            votes: Counter = Counter()
            for traits, fit in self.variants.values():
                if k in traits:
                    votes[_hashable(traits[k])] += fit + 1e-9
            if votes:
                out[k] = votes.most_common(1)[0][0]
        return out

    def master(self) -> str | None:
        """The single fittest sequence. Present for comparison only — the whole
        point of the frame is that this is not the identity."""
        if not self.variants:
            return None
        return max(self.variants.items(), key=lambda kv: kv[1][1])[0]

    # -- health ------------------------------------------------------------
    def shannon(self) -> float:
        """Diversity of the swarm in nats. Zero means one variant owns it, which
        is the state right before an environment shift kills the lineage."""
        total = sum(f for _, f in self.variants.values()) or 1e-9
        h = 0.0
        for _, f in self.variants.values():
            p = (f + 1e-12) / total
            h -= p * math.log(p)
        return h

    def error_threshold(self, genome_length: int) -> float:
        """Eigen's bound: sustainable per-site mutation rate ~ 1/L.

        Above this the consensus is not maintained and the population melts.
        For an agent this reads: if a capability is described by L meaningful
        fields, you may mutate about 1/L of them per generation before the
        capability stops being itself.
        """
        return 1.0 / max(1, genome_length)

    def melting(self, observed_mutation_rate: float, genome_length: int) -> bool:
        return observed_mutation_rate > self.error_threshold(genome_length)

    def report(self, genome_length: int, mu: float) -> dict:
        return {
            "name": self.name,
            "variants": len(self.variants),
            "consensus": self.consensus(),
            "master": self.master(),
            "diversity_nats": round(self.shannon(), 4),
            "error_threshold": round(self.error_threshold(genome_length), 4),
            "observed_mu": round(mu, 4),
            "status": "MELTING" if self.melting(mu, genome_length)
                      else ("BRITTLE" if self.shannon() < 0.2 and len(self.variants) > 1
                            else "STABLE"),
        }


def _hashable(v):
    if isinstance(v, (list, tuple)):
        return tuple(_hashable(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _hashable(x)) for k, x in v.items()))
    return v
