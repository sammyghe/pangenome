"""Knowledge scaffolding — and the sleep that builds it.

A ten-terabyte store of everything that ever happened is not intelligence. What
matters is not how much is kept but what structure was extracted before the raw
material was allowed to die:

    episode -> pattern -> abstraction -> skill

    day 1    "Supplier X delivered late."
    day 20   "Supplier X often delivers late."
    day 50   "Suppliers in this category have high variance."
    day 100  "Require a delivery buffer for this supplier class."

The hundred conversations are not the asset. The last line is, and it is roughly
forty bytes. So the organism forgets aggressively, on an Ebbinghaus retention
curve where rehearsal extends strength — but only forgets raw episodes that have
already been *consumed* into a higher tier. Structure first, then amnesia.

Consolidation runs during sleep, which is not the same thing as being switched
off. Sleep here does four jobs, none of which touch the outside world:

    REHEARSE     recurrence strengthens; everything else decays
    PROMOTE      episodes -> patterns -> abstractions -> skills
    ASSOCIATE    find A-C links via a shared B that were never seen together
    FORGET       drop consumed episodes below retention threshold

The ASSOCIATE step is Swanson's ABC discovery model, the one that found the
fish-oil/Raynaud connection by noticing that two literatures shared a middle term
and had never cited each other. It is the mechanism behind "three unrelated
things I saw today are actually related", and it only works if something replays
the day offline.
"""

from __future__ import annotations

import json
import math
import time

EPISODE = "episode"
PATTERN = "pattern"
ABSTRACTION = "abstraction"
SKILL = "skill"

DAY = 86400.0

# How much recurrence each promotion demands.
#
# Support is counted in DISTINCT DAYS, not in episodes. Three hundred
# observations inside a single heartbeat are one scene, not three hundred
# occurrences — the same error that made the first epidemiology fit report an
# R0 of three billion. Seeing a thousand agent repositories in one afternoon
# teaches you one thing, not a thousand things, and a scaffold that cannot tell
# those apart is a warehouse with a promotion ceremony attached.
PATTERN_DAYS = 3           # distinct days a signature must recur to become a pattern
ABSTRACTION_SUPPORT = 2    # patterns sharing a concept -> an abstraction
SKILL_SIGNATURES = 2       # distinct pattern lineages behind an actionable rule

# A concept present in nearly every pattern generalises nothing — it is a
# stopword for this organism. Abstraction requires discriminative power.
ABSTRACTION_MAX_PREVALENCE = 0.5
CHARACTERISTIC_CONCEPTS = 8   # per pattern, by distinctiveness

RETENTION_FLOOR = 0.35     # below this, a consumed episode is dropped


class Scaffold:
    def __init__(self, store, field=None):
        self.store = store
        self.field = field           # AttentionField, for co-occurrence learning

    # -- intake ------------------------------------------------------------
    def remember(self, signature: str, concepts: list[str], detail: dict,
                 strength: float = 1.0) -> int:
        cur = self.store.db.execute(
            "INSERT INTO episodes(at,signature,concepts,detail,strength)"
            " VALUES (?,?,?,?,?)",
            (time.time(), signature, json.dumps(sorted(concepts)),
             json.dumps(detail), strength))
        if self.field:
            self.field.learn(concepts, strength)
        return cur.lastrowid

    # -- forgetting --------------------------------------------------------
    @staticmethod
    def retention(age_days: float, strength: float, rehearsals: int) -> float:
        """Ebbinghaus: R = exp(-t/S), with S extended by each rehearsal.

        The curve is the point. A thing seen once and never again is gone in
        days; a thing seen weekly survives for years without anyone deciding it
        was important.
        """
        S = max(0.5, strength * (1.0 + 1.6 * rehearsals))
        return math.exp(-age_days / S)

    # -- sleep -------------------------------------------------------------
    def consolidate(self, now: float | None = None) -> dict:
        now = now or time.time()
        out = {"rehearsed": 0, "patterns": 0, "abstractions": 0,
               "skills": 0, "hypotheses": 0, "forgotten": 0}

        out["rehearsed"] = self._rehearse()
        out["patterns"] = self._promote_patterns()
        out["abstractions"] = self._promote_abstractions()
        out["skills"] = self._promote_skills()
        out["hypotheses"] = len(self.associate())
        out["forgotten"] = self._forget(now)

        self.store.event("sleep", "consolidation complete", detail=out)
        self.store.commit()
        return out

    def _rehearse(self) -> int:
        """Recurrence is the only vote. Nothing is marked important by hand."""
        rows = self.store.q(
            "SELECT signature, COUNT(*) n FROM episodes WHERE consumed=0"
            " GROUP BY signature HAVING n > 1")
        n = 0
        for r in rows:
            self.store.db.execute(
                "UPDATE episodes SET rehearsals = rehearsals + 1"
                " WHERE signature=? AND consumed=0", (r["signature"],))
            n += r["n"]
        return n

    def _characteristic(self, signature: str, eps: list) -> list[str]:
        """The concepts that make this signature *itself*, not the ones it shares
        with everything. Frequency inside the signature over frequency overall —
        tf-idf's argument, and the reason 'agent' is not a distinguishing feature
        of an organism that only ever looks at agent repositories.
        """
        local: dict[str, int] = {}
        for e in eps:
            for c in json.loads(e["concepts"]):
                local[c] = local.get(c, 0) + 1
        n_local = len(eps) or 1
        globals_ = {r["name"]: r["count"] for r in self.store.q(
            "SELECT name, count FROM concepts")}
        n_global = sum(globals_.values()) or 1
        scored = [((cnt / n_local) / max(1e-9, globals_.get(c, 1) / n_global), c)
                  for c, cnt in local.items()]
        scored.sort(reverse=True)
        return sorted(c for _, c in scored[:CHARACTERISTIC_CONCEPTS])

    def _promote_patterns(self) -> int:
        rows = self.store.q(
            "SELECT signature, COUNT(DISTINCT CAST(at/86400 AS INTEGER)) d,"
            " COUNT(*) n FROM episodes WHERE consumed=0"
            " GROUP BY signature HAVING d >= ?", (PATTERN_DAYS,))
        made = 0
        for r in rows:
            sig = r["signature"]
            eps = self.store.q(
                "SELECT id, concepts, detail FROM episodes"
                " WHERE signature=? AND consumed=0", (sig,))
            concepts = self._characteristic(sig, eps)
            if self._exists(PATTERN, sig):
                self.store.db.execute(
                    "UPDATE scaffold SET support = support + ? WHERE tier=? AND signature=?",
                    (len(eps), PATTERN, sig))
            else:
                self._write(PATTERN, sig,
                            f"{sig} recurs ({len(eps)} occurrences observed)",
                            len(eps), concepts)
                made += 1
            # consumed, not deleted — forgetting is a separate decision made on
            # the retention curve, so a still-fresh episode stays available
            self.store.db.execute(
                "UPDATE episodes SET consumed=1 WHERE signature=? AND consumed=0", (sig,))
        return made

    def _promote_abstractions(self) -> int:
        """Generalise across patterns that share a concept.

        Deliberately mechanical: the shared concept IS the generalisation. It
        does not invent a category name it cannot justify from the evidence.
        """
        pats = self.store.q("SELECT * FROM scaffold WHERE tier=?", (PATTERN,))
        by_concept: dict[str, list] = {}
        for p in pats:
            for c in json.loads(p["concepts"]):
                by_concept.setdefault(c, []).append(p)
        made = 0
        for concept, group in by_concept.items():
            if len(group) < ABSTRACTION_SUPPORT or self._exists(ABSTRACTION, concept):
                continue
            # Prevalence is only meaningful once there is a population to be
            # prevalent *within*. With three patterns, "appears in all of them"
            # is not evidence of a stopword, it is a sample of three.
            if len(pats) >= 4 and len(group) / len(pats) > ABSTRACTION_MAX_PREVALENCE:
                continue
            self._write(ABSTRACTION, concept,
                        f"'{concept}' generalises across {len(group)} of "
                        f"{len(pats)} patterns: "
                        f"{', '.join(sorted(p['signature'] for p in group)[:4])}",
                        len(group), [concept], parent=group[0]["id"])
            made += 1
        return made

    def _promote_skills(self) -> int:
        """The only tier that changes behaviour rather than describing it.

        So it demands the most, and it demands it in the right currency:
        independent lineages, not repetition. An abstraction resting on one
        pattern seen a thousand times is one observation; the same abstraction
        holding across two unrelated patterns is a rule.
        """
        made = 0
        for a in self.store.q("SELECT * FROM scaffold WHERE tier=?", (ABSTRACTION,)):
            if a["support"] < SKILL_SIGNATURES or self._exists(SKILL, a["signature"]):
                continue
            self._write(SKILL, a["signature"],
                        f"When '{a['signature']}' is in play, apply the rule held "
                        f"across {a['support']} independent patterns.",
                        a["support"], json.loads(a["concepts"]), parent=a["id"])
            made += 1
        return made

    def associate(self, min_shared: float = 0.0) -> list[dict]:
        """Swanson ABC: A-B strong, B-C strong, A-C never observed together.

        The hypotheses are candidates, not conclusions, and they are stored as
        such. An organism that reported these as findings would be a confabulation
        engine; one that never generates them can only ever know what it was told.
        """
        edges = self.store.q("SELECT a,b,weight FROM edges WHERE weight > 0")
        adj: dict[str, dict[str, float]] = {}
        seen = set()
        for e in edges:
            adj.setdefault(e["a"], {})[e["b"]] = e["weight"]
            adj.setdefault(e["b"], {})[e["a"]] = e["weight"]
            seen.add((e["a"], e["b"]))

        out = []
        for b, ns in adj.items():
            strong = sorted(ns.items(), key=lambda kv: -kv[1])[:6]
            for i, (a, wa) in enumerate(strong):
                for c, wc in strong[i + 1:]:
                    pair = tuple(sorted((a, c)))
                    if pair in seen or wa <= min_shared or wc <= min_shared:
                        continue
                    out.append({"a": a, "via": b, "c": c,
                                "score": round(min(wa, wc), 3)})
        out.sort(key=lambda h: -h["score"])
        out = out[:20]
        for h in out:
            self.store.event("hypothesis",
                             f"{h['a']} — {h['c']} may connect via {h['via']}",
                             subject=f"{h['a']}|{h['c']}", detail=h)
        return out

    def _forget(self, now: float) -> int:
        """Only consumed episodes die. Structure is extracted before amnesia."""
        rows = self.store.q(
            "SELECT id, at, strength, rehearsals FROM episodes WHERE consumed=1")
        doomed = [r["id"] for r in rows
                  if self.retention((now - r["at"]) / DAY, r["strength"],
                                    r["rehearsals"]) < RETENTION_FLOOR]
        for i in doomed:
            self.store.db.execute("DELETE FROM episodes WHERE id=?", (i,))
        return len(doomed)

    # -- the metric that matters -------------------------------------------
    def learning_ratio(self, window_days: float = 30.0) -> dict:
        """Learning-to-learning: structure produced per unit of experience.

        Not "how much did it learn" but "how much better did it get at turning
        experience into capability". 100 episodes yielding 10 skills this month
        and 40 next month is the thing worth optimising, and it is the one number
        that distinguishes a developing organism from an accumulating database.
        """
        cutoff = time.time() - window_days * DAY
        eps = self.store.q(
            "SELECT COUNT(*) n FROM episodes WHERE at >= ?", (cutoff,))[0]["n"]
        consumed = self.store.q(
            "SELECT COALESCE(SUM(support),0) s FROM scaffold WHERE at >= ?",
            (cutoff,))[0]["s"]
        struct = self.store.q(
            "SELECT COUNT(*) n FROM scaffold WHERE at >= ?", (cutoff,))[0]["n"]
        base = max(eps, consumed, 1)
        return {"window_days": window_days, "episodes": eps,
                "structures_formed": struct,
                "ratio": round(struct / base, 4),
                "bytes_per_structure": None}

    def summary(self) -> dict:
        tiers = {r["tier"]: r["n"] for r in self.store.q(
            "SELECT tier, COUNT(*) n FROM scaffold GROUP BY tier")}
        live = self.store.q(
            "SELECT COUNT(*) n FROM episodes WHERE consumed=0")[0]["n"]
        return {"live_episodes": live,
                "patterns": tiers.get(PATTERN, 0),
                "abstractions": tiers.get(ABSTRACTION, 0),
                "skills": tiers.get(SKILL, 0)}

    # -- helpers -----------------------------------------------------------
    def _exists(self, tier: str, signature: str) -> bool:
        return bool(self.store.q(
            "SELECT 1 FROM scaffold WHERE tier=? AND signature=?", (tier, signature)))

    def _write(self, tier: str, signature: str, statement: str, support: int,
               concepts: list[str], parent: int | None = None) -> None:
        self.store.db.execute(
            "INSERT INTO scaffold(at,tier,signature,statement,support,concepts,parent)"
            " VALUES (?,?,?,?,?,?,?)",
            (time.time(), tier, signature, statement, support,
             json.dumps(sorted(concepts)), parent))
