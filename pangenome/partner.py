"""The brain socket — where a model plugs into the organism.

This is the adapter that turns the deterministic body into a usable partner.
Design rules, stated because they are load-bearing:

1. THE AUTONOMOUS LOOP STAYS MODEL-FREE. The heartbeat never calls a model.
   Everything that runs unattended is deterministic Python, which is why it can
   run forever on a free cron and why its records are auditable. The model is
   only ever invoked HERE, in an owner-present, interactive command.

2. THE MODEL IS A GUEST, NOT AN ORGAN. It receives a briefing assembled from
   the organism's state (interests, skills, what was noticed, what is spreading)
   and the owner's message. It never receives credentials, never receives
   capability payloads, and nothing it says is executed. Its reply is text.

3. EVERY CONVERSATION FEEDS THE ORGANISM. The exchange is recorded as an
   episode, its concepts strengthen the associative graph, and concepts the
   owner keeps raising are surfaced as interest suggestions. This is the "grows
   with you" loop: talk to it about your business for a week and its attention
   field reshapes around your business — whichever model happens to be plugged
   in that day.

4. THE BRAIN IS REPLACEABLE. Adapter interface is one function: text in, text
   out. Gemini free tier is the default because it costs nothing; swap the
   endpoint and the organism does not notice. The organism's value is the state
   AROUND the socket, which is the entire thesis.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request

from .salience import AttentionField, concepts_of
from .scaffold import Scaffold
from .store import Store

GEMINI = ("https://generativelanguage.googleapis.com/v1beta/models/"
          "{model}:generateContent")

SYSTEM = """You are the voice of {name}, a personal AI organism owned by {steward}.
You are not a general assistant: you speak from this organism's accumulated
state, which is given below. Be concise and concrete. When the briefing contains
something relevant the owner did not ask about, say so in one line — that is
your job. When the organism's state contains nothing relevant, say so plainly
instead of inventing.

ORGANISM STATE
{briefing}
"""


# Tried in order until one answers. A partner that dies when one model's free
# quota runs out is not a partner; the organism outlives any given brain.
FALLBACK_CHAIN = ["gemini-2.5-flash", "gemini-flash-lite-latest",
                  "gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]


class BrainSocket:
    def __init__(self, model: str | None = None):
        self.chain = [model] + FALLBACK_CHAIN if model else list(FALLBACK_CHAIN)
        self.key = os.environ.get("GEMINI_API_KEY")
        self.used: str | None = None

    @property
    def available(self) -> bool:
        return bool(self.key)

    def infer(self, prompt: str) -> str:
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
        last: Exception | None = None
        for model in self.chain:
            req = urllib.request.Request(
                GEMINI.format(model=model) + f"?key={self.key}",
                data=body, method="POST",
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.loads(r.read())
                self.used = model
                parts = data["candidates"][0]["content"].get("parts", [{}])
                return "".join(p.get("text", "") for p in parts)
            except Exception as e:
                last = e
                continue
        raise ConnectionError(f"every brain in the chain refused: {last}")


def briefing(store: Store, field: AttentionField, scaffold: Scaffold,
             message: str) -> str:
    """Assemble what the model gets to know. Small on purpose: the organism's
    whole job is deciding what the expensive brain has to read."""
    lines = []

    interests = store.q("SELECT concept, weight, why FROM interests ORDER BY weight DESC")
    if interests:
        lines.append("Owner's standing interests: " + ", ".join(
            f"{r['concept']}({r['weight']})" for r in interests[:12]))

    sk = store.q("SELECT statement FROM scaffold WHERE tier='skill'"
                 " ORDER BY support DESC LIMIT 6")
    if sk:
        lines.append("Learned rules:")
        lines += [f"  - {r['statement']}" for r in sk]

    noticed = store.q(
        "SELECT subject, score, reason FROM attention_log"
        " WHERE verdict IN ('investigate','interrupt')"
        " ORDER BY at DESC LIMIT 8")
    if noticed:
        lines.append("Recently noticed without being asked:")
        lines += [f"  - {r['subject']} ({r['score']:.2f}) — {r['reason']}"
                  for r in noticed]

    hyp = store.q("SELECT reason FROM events WHERE kind='hypothesis'"
                  " ORDER BY at DESC LIMIT 5")
    if hyp:
        lines.append("Sleep hypotheses (candidates, unverified):")
        lines += [f"  - {r['reason']}" for r in hyp]

    # anything in the live observations that connects to this message
    cs = concepts_of(message)
    if cs:
        f = field.activation(cs)
        rows = store.q("SELECT DISTINCT locus, name FROM observations"
                       " ORDER BY seen_at DESC LIMIT 400")
        scored = []
        for r in rows:
            rc = concepts_of(f"{r['locus']} {r['name'] or ''}")
            s = sum(f.get(c, 0.0) for c in rc)
            if s > 0.3:
                scored.append((s, r["locus"]))
        scored.sort(reverse=True)
        if scored:
            lines.append("Related things the organism has seen in the wild: "
                         + ", ".join(l for _, l in scored[:6]))

    return "\n".join(lines) or "(the organism is young and has little state yet)"


def talk(message: str, model: str | None = None) -> dict:
    """One exchange. The organism learns from it whether or not a brain answers."""
    from .chromosome import Chromosome
    store = Store()
    chrom = Chromosome()
    field = AttentionField(store)
    scaffold = Scaffold(store, field)

    # the organism learns from what its owner talks about — model or no model
    cs = concepts_of(message)
    scaffold.remember("owner:conversation", cs, {"message": message[:400]})
    store.commit()

    name = chrom.name if chrom.alive else "unnamed"
    steward = chrom.data.get("steward", "the owner") if chrom.alive else "the owner"

    socket = BrainSocket(model)
    if not socket.available:
        return {"reply": None, "learned": cs,
                "note": "No GEMINI_API_KEY set. The organism still recorded and "
                        "learned from this message; set a free key from "
                        "aistudio.google.com to get replies."}

    brief = briefing(store, field, scaffold, message)
    prompt = SYSTEM.format(name=name, steward=steward, briefing=brief)
    prompt += f"\nOWNER: {message}\n"
    try:
        reply = socket.infer(prompt)
    except Exception as e:
        return {"reply": None, "learned": cs, "note": f"brain unreachable: {e}"}

    # what the brain said also feeds the graph — weakly, it is a guest
    field.learn(concepts_of(reply), strength=0.3)
    store.commit()

    # suggest interests the owner keeps raising but never declared
    suggestions = _suggest_interests(store)
    return {"reply": reply, "learned": cs, "suggestions": suggestions,
            "brain": socket.used, "briefing_chars": len(brief)}


def _suggest_interests(store: Store, min_mentions: int = 3) -> list[str]:
    """Concepts the owner keeps raising that the organism has ALSO seen in the
    wild. The second condition is the filter that matters: 'could' and 'help'
    recur in every conversation, but only concepts grounded in the observation
    stream can shape attention usefully, because attention runs over that stream.
    """
    declared = {r["concept"] for r in store.q("SELECT concept FROM interests")}
    wild = {r["name"] for r in store.q(
        "SELECT name FROM concepts WHERE count >= 3")}
    rows = store.q(
        "SELECT concepts FROM episodes WHERE signature='owner:conversation'")
    counts: dict[str, int] = {}
    for r in rows:
        for c in json.loads(r["concepts"]):
            counts[c] = counts.get(c, 0) + 1
    # conversational filler that survives the stopword list and happens to also
    # occur in repo descriptions; grounding alone cannot catch these
    generic = {"could", "would", "should", "about", "there", "where", "which",
               "every", "really", "think", "going", "want", "need", "know",
               "look", "looking", "today", "week", "worth"}
    return sorted(c for c, n in counts.items()
                  if n >= min_mentions and c not in declared
                  and c in wild and len(c) >= 5 and c not in generic)[:5]
