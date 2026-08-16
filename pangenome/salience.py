"""Developmental attention — what the organism *notices*, as opposed to what it sees.

Two people walk down the same street. The car dealer sees cars; the clothes
designer sees clothes. The photons are identical. What differs is which
concepts were already active enough that the input crossed threshold.

Every agent architecture today does:

    page -> DOM/screenshot -> model -> answer to the question asked

which is perfectly literal. Ask it for deodorant prices and it returns deodorant
prices, in a shop that happens to be selling sunglasses 30% under the wholesale
price its owner pays. A person would have said something.

So this module sits between perception and reasoning:

    WORLD -> perception -> ATTENTION FIELD -> reasoning -> action

The mechanism is spreading activation over an associative concept graph
(Collins & Loftus; the activation equation is ACT-R shaped). Standing owner
interests are a *tonic* pre-activation — this is priming, and it is why the same
page scores differently for two organisms. The current goal is a *phasic*
pre-activation on top.

Three things make a thing salient, and they are genuinely different:

    ACTIVATION  it connects to what I know and care about
    NOVELTY     I have hardly seen this before
    SURPRISE    I have seen this often, and this instance is off-distribution

Surprise is the one that catches "sunglasses, but cheap". Novelty alone would
miss it, because sunglasses are the *least* novel thing in that organism's world.

And the filter itself develops: concepts that have led to useful discoveries have
their base weight raised, so the organism's perception specialises over time
rather than staying fixed at whatever its owner first declared.
"""

from __future__ import annotations

import json
import math
import re
import time

# --- verdicts, cheapest response first --------------------------------------
IGNORE = "ignore"
NOTICE = "notice"           # logged, not stored
REMEMBER = "remember"       # written to episodic memory
INVESTIGATE = "investigate" # worth spending a model call on
INTERRUPT = "interrupt"     # worth breaking the current task for

# Attention is a scarce resource allocated across a scene, not a score compared
# to a constant. So a verdict needs BOTH an absolute floor and a relative margin:
# the thing must matter, and it must stand out from everything else in view.
#
# This is scene-relative z-score normalisation — in the spirit, not the
# mathematics, of the Reynolds–Heeger normalisation model of visual attention.
# Reynolds–Heeger is *divisive* (a unit's response is divided by the pooled
# activity of its neighbours); the margin below is *subtractive* (a score in
# standard deviations above the scene mean). Same intent — a response defined
# against its context rather than a constant — different arithmetic, and the
# module says so rather than borrowing the equation's authority.
#
# It fixes the failure mode a fixed threshold cannot:
# a page where everything is mildly relevant should produce no interruption at
# all, and a page where one item towers over the rest should produce one even if
# its absolute score is modest. Tuning a constant can only ever get one of those
# two cases right.
FLOOR = {NOTICE: 0.20, REMEMBER: 0.35, INVESTIGATE: 0.45, INTERRUPT: 0.60}
MARGIN = {NOTICE: 0.0, REMEMBER: 0.5, INVESTIGATE: 1.0, INTERRUPT: 2.0}  # in SDs

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "you", "your", "are",
    "was", "will", "can", "has", "have", "not", "but", "all", "new", "our",
    "its", "use", "using", "used", "get", "set", "how", "what", "when", "into",
    "via", "per", "out", "one", "two", "any", "more", "most", "than", "then",
    "server", "client", "tool", "tools", "api", "app", "based", "simple",
}

TOKEN = re.compile(r"[a-z][a-z0-9\-]{2,}")


def concepts_of(text: str, extra: list[str] | None = None) -> list[str]:
    """Crude but deliberate: a cheap first pass that never calls a model.

    The expensive model only ever sees things that already crossed threshold.
    That is the point — a perception layer that costs a model call per observation
    cannot run over five hundred items on a page.
    """
    found = {t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS}
    return sorted(found | set(extra or []))


class AttentionField:
    def __init__(self, store, hops: int = 2, decay: float = 0.45):
        self.store = store
        self.hops = hops
        self.decay = decay

    # -- the owner model ---------------------------------------------------
    def prime(self, concept: str, weight: float, why: str) -> None:
        """Standing interest. This is what makes two organisms see differently."""
        self.store.db.execute(
            "INSERT INTO interests(concept,weight,why,set_at) VALUES (?,?,?,?)"
            " ON CONFLICT(concept) DO UPDATE SET weight=excluded.weight,"
            " why=excluded.why, set_at=excluded.set_at",
            (concept.lower(), weight, why, time.time()))
        self.store.commit()

    def interests(self) -> dict[str, float]:
        return {r["concept"]: r["weight"]
                for r in self.store.q("SELECT concept, weight FROM interests")}

    # -- associative memory ------------------------------------------------
    def learn(self, concepts: list[str], strength: float = 1.0) -> None:
        """Co-occurrence builds the graph. Nobody declares these edges."""
        now = time.time()
        for c in concepts:
            self.store.db.execute(
                "INSERT INTO concepts(name,first_seen,last_seen,count) VALUES (?,?,?,1)"
                " ON CONFLICT(name) DO UPDATE SET last_seen=?, count=count+1",
                (c, now, now, now))
        for i, a in enumerate(concepts):
            for b in concepts[i + 1:]:
                lo, hi = sorted((a, b))
                self.store.db.execute(
                    "INSERT INTO edges(a,b,weight,count,last_seen) VALUES (?,?,?,1,?)"
                    " ON CONFLICT(a,b) DO UPDATE SET weight=weight+?, count=count+1,"
                    " last_seen=?",
                    (lo, hi, strength, now, strength, now))

    def neighbours(self, concept: str) -> dict[str, float]:
        rows = self.store.q(
            "SELECT a,b,weight FROM edges WHERE a=? OR b=?", (concept, concept))
        out = {}
        for r in rows:
            other = r["b"] if r["a"] == concept else r["a"]
            out[other] = r["weight"]
        total = sum(out.values()) or 1.0
        return {k: v / total for k, v in out.items()}    # normalise fan-out

    # -- spreading activation ----------------------------------------------
    def activation(self, goal: list[str] | None = None) -> dict[str, float]:
        """The field. Tonic (owner interests) + phasic (current goal), spread.

        Fan-out is normalised per source, so a hub concept connected to everything
        does not flood the field. Without that, the most common concept wins every
        time and the organism notices nothing but the obvious.
        """
        field: dict[str, float] = {}
        seeds = dict(self.interests())
        for g in (goal or []):
            seeds[g] = seeds.get(g, 0.0) + 1.0

        frontier = seeds
        for hop in range(self.hops + 1):
            for c, a in frontier.items():
                field[c] = field.get(c, 0.0) + a
            if hop == self.hops:
                break
            nxt: dict[str, float] = {}
            for c, a in frontier.items():
                if a < 0.02:
                    continue
                for n, w in self.neighbours(c).items():
                    nxt[n] = nxt.get(n, 0.0) + a * w * self.decay
            frontier = nxt
        return field

    def category_of(self, concepts: list[str], prefix: str = "market") -> str:
        """Which distribution should this be judged against?

        Surprise is meaningless without the right reference class. "$11 is
        cheap" is only true relative to *sunglasses* — judged against the whole
        shop, an $11 pair of designer sunglasses sits comfortably mid-range and
        vanishes. So the reference class is the organism's strongest standing
        interest present in the item, which means two organisms judge the same
        item against different baselines. That is the point.
        """
        interests = self.interests()
        hits = [(interests[c], c) for c in concepts if c in interests]
        if not hits:
            return f"{prefix}:general"
        return f"{prefix}:{max(hits)[1]}"

    # -- the three signals -------------------------------------------------
    def novelty(self, concept: str) -> float:
        r = self.store.q("SELECT count FROM concepts WHERE name=?", (concept,))
        n = r[0]["count"] if r else 0
        return 1.0 / (1.0 + math.log1p(n))

    def surprise(self, signature: str, value: float | None) -> float:
        """Off-distribution against what this organism has actually seen.

        Deliberately not novelty's opposite: a familiar concept at an unfamiliar
        value is the single most useful thing an organism can notice, and it is
        exactly what a novelty-only filter throws away.
        """
        if value is None:
            return 0.0
        rows = self.store.q(
            "SELECT detail FROM episodes WHERE signature=? ORDER BY at DESC LIMIT 200",
            (signature,))
        vals = []
        for r in rows:
            v = json.loads(r["detail"]).get("value")
            if isinstance(v, (int, float)):
                vals.append(float(v))
        if len(vals) < 5:
            return 0.0
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        sd = math.sqrt(var)
        if sd < 1e-9:
            return 0.0
        z = abs(value - mean) / sd
        return min(1.0, z / 3.0)

    # -- the judgement -----------------------------------------------------
    def appraise(self, subject: str, text: str, *, goal: list[str] | None = None,
                 signature: str = "observation", value: float | None = None,
                 field: dict[str, float] | None = None) -> dict:
        """Score one item on three channels. No verdict — that needs the scene."""
        cs = concepts_of(text, extra=[subject.lower()])
        field = self.activation(goal) if field is None else field

        act = sum(field.get(c, 0.0) for c in cs)
        act = act / (1.0 + act)                      # saturate, so a long page
        nov = max((self.novelty(c) for c in cs), default=0.0)  # cannot win by length
        sur = self.surprise(signature, value)

        base = self.store.q(
            "SELECT AVG(base) b FROM concepts WHERE name IN (%s)"
            % ",".join("?" * len(cs)), tuple(cs)) if cs else []
        learned = (base[0]["b"] or 0.0) if base else 0.0

        score = min(1.0, 0.55 * act + 0.15 * nov + 0.30 * sur + learned)
        return {"subject": subject, "score": round(score, 4), "verdict": IGNORE,
                "signature": signature,
                "reason": self._explain(act, nov, sur, learned), "concepts": cs,
                "activation": round(act, 4), "novelty": round(nov, 4),
                "surprise": round(sur, 4)}

    def scan(self, items: list[tuple], *, goal: list[str] | None = None,
             log: bool = True) -> list[dict]:
        """Appraise a whole scene, then allocate attention competitively.

        `items` are (subject, text, signature, value) tuples. The activation
        field is computed once — it is a property of the organism at this
        moment, not of each item — and verdicts are assigned only after every
        item has been scored, because standing out is a relation, not a property.

        A missing signature is not an error: the reference class is derived
        here by `category_of`, so judging a value against the right baseline is
        a mechanism of the organism rather than a convention the caller has to
        remember.
        """
        field = self.activation(goal)
        out = [self.appraise(s, t, goal=goal,
                             signature=sig or self.category_of(concepts_of(t)),
                             value=v, field=field)
               for s, t, sig, v in items]
        if not out:
            return out

        scores = [a["score"] for a in out]
        mean = sum(scores) / len(scores)
        sd = math.sqrt(sum((s - mean) ** 2 for s in scores) / len(scores))
        sd = max(sd, 0.02)          # a perfectly flat scene must not divide by zero

        for a in out:
            z = (a["score"] - mean) / sd
            a["pop"] = round(z, 3)
            for v in (NOTICE, REMEMBER, INVESTIGATE, INTERRUPT):
                if a["score"] >= FLOOR[v] and z >= MARGIN[v]:
                    a["verdict"] = v
            if log and a["verdict"] != IGNORE:
                self.store.db.execute(
                    "INSERT INTO attention_log(at,subject,score,verdict,reason)"
                    " VALUES (?,?,?,?,?)",
                    (time.time(), a["subject"], a["score"], a["verdict"], a["reason"]))
        if log:
            self.store.commit()
        return out

    @staticmethod
    def _explain(act: float, nov: float, sur: float, learned: float) -> str:
        parts = []
        if act > 0.2:
            parts.append("connects to standing interests")
        if sur > 0.3:
            parts.append("off-distribution value for something familiar")
        if nov > 0.6:
            parts.append("largely unseen before")
        if learned > 0.02:
            parts.append("concepts that paid off previously")
        return "; ".join(parts) or "weak on every channel"

    # -- the filter develops ----------------------------------------------
    def reinforce(self, concepts: list[str], useful: bool, delta: float = 0.04) -> None:
        """Feedback from whether a discovery actually mattered.

        This is the loop that makes attention *developmental* rather than
        configured: what proved worth noticing becomes easier to notice, so the
        organism's perception specialises beyond whatever its owner first declared.
        """
        d = delta if useful else -delta
        for c in concepts:
            self.store.db.execute(
                "UPDATE concepts SET base = MAX(-0.1, MIN(0.25, base + ?)) WHERE name=?",
                (d, c))
        self.store.commit()

    def precision(self) -> dict:
        """Useful discoveries / all unsolicited discoveries.

        The metric that keeps this honest. Too literal is useless; too eager is
        worse, because an organism that interrupts constantly gets switched off.
        """
        rows = self.store.q(
            "SELECT useful, COUNT(*) n FROM attention_log"
            " WHERE verdict IN ('investigate','interrupt') AND useful IS NOT NULL"
            " GROUP BY useful")
        good = sum(r["n"] for r in rows if r["useful"] == 1)
        bad = sum(r["n"] for r in rows if r["useful"] == 0)
        total = good + bad
        return {"judged": total, "useful": good,
                "precision": round(good / total, 3) if total else None}
