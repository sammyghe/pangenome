"""Lysogeny — the third state between running and dead.

Every agent framework in existence assumes continuous operation, and cost is the
binding constraint for anyone outside a funded lab. Lambda phage solved this in
deep time: on entry it makes a decision. Replicate now and burst the host
(lysis), or integrate into the host genome, go silent, and cost nothing for
years until a stress signal induces it (lysogeny). HIV and herpes do the same.

So a capability here has three states, not two:

    LYTIC       active. Consuming budget. Doing work.
    LYSOGENIC   integrated. Zero cost. Present in the genome, not expressed.
    EXCISED     removed. Kept in the record, never re-acquired without cause.

The switch is the CI/Cro bistable circuit: two mutually repressing regulators
with cooperative positive autoregulation on CI. CI high -> lysogeny. Cro high ->
lysis. Between them is a genuine bistable region, which is the point: the
organism does not flap between running and dormant on noise.

Lambda takes the decision on multiplicity of infection — lysis at low MOI,
lysogeny at high MOI. The analogue is exact and useful: when demand for a
capability is scarce, express it and use it; when the same demand is arriving
from many directions at once, the host is saturated, so integrate and wait.
"""

from __future__ import annotations

from dataclasses import dataclass

LYTIC = "lytic"
LYSOGENIC = "lysogenic"
EXCISED = "excised"


@dataclass
class Switch:
    """CI/Cro. Hill-cooperative mutual repression, solved to steady state.

    Not a metaphor with numbers bolted on: the two nullclines genuinely
    intersect three times over part of the parameter range, and the middle
    intersection is unstable. That is where hysteresis comes from, and
    hysteresis is the whole reason to use this rather than a threshold.
    """
    n: int = 2          # Hill coefficient for Cro repression
    m: int = 3          # cooperativity of CI positive autoregulation
    k: float = 0.5      # repression constant
    decay: float = 1.0

    def step(self, ci: float, cro: float, stress: float, dt: float = 0.1) -> tuple[float, float]:
        # CI: repressed by Cro, cooperatively autoactivated by itself,
        #     destroyed by stress (RecA-mediated CI cleavage — the SOS response)
        d_ci = (1.0 / (1.0 + (cro / self.k) ** self.n)
                + 2.0 * (ci ** self.m) / (1.0 + ci ** self.m)
                - self.decay * ci
                - 3.0 * stress * ci)
        # Cro: repressed by CI, no autoactivation
        d_cro = (1.5 / (1.0 + (ci / self.k) ** self.n)
                 - self.decay * cro)
        return max(0.0, ci + d_ci * dt), max(0.0, cro + d_cro * dt)

    def settle(self, ci: float, cro: float, stress: float, steps: int = 400) -> tuple[float, float]:
        for _ in range(steps):
            ci, cro = self.step(ci, cro, stress)
        return ci, cro


class Prophage:
    """One capability's dormancy controller."""

    def __init__(self, pid: str, state: str = LYSOGENIC, ci: float = 1.5, cro: float = 0.0):
        self.pid = pid
        self.state = state
        self.ci = ci
        self.cro = cro
        self.switch = Switch()

    def decide(self, *, demand: float, stress: float) -> str:
        """demand = multiplicity of requests for this capability this beat.
        stress = host-level distress (budget burn, failure rate, deadline).

        High MOI  -> integrate and wait. The host is saturated; adding an active
                     process makes it worse.
        Low MOI + stress -> induce. Something needs doing and nothing else is
                     doing it.
        """
        if self.state == EXCISED:
            return EXCISED

        moi = max(0.0, demand)
        # High MOI pushes CI up (lysogeny); stress cleaves CI (induction).
        seed_ci = self.ci + 0.4 * moi
        seed_cro = self.cro + (0.6 if moi < 1.0 else 0.0)
        self.ci, self.cro = self.switch.settle(seed_ci, seed_cro, stress)

        self.state = LYTIC if self.cro > self.ci else LYSOGENIC
        return self.state

    @property
    def cost_this_beat(self) -> float:
        """The entire point. A lysogenic capability is free."""
        return 1.0 if self.state == LYTIC else 0.0
