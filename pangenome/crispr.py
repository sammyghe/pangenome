"""CRISPR — adaptive immunity.

Bacteria keep a library of snippets taken from things that attacked them
(spacers), and cut anything matching on re-encounter. It is strictly stronger
than self/non-self, because it *learns*: the array is a record of every past
invader, and it grows.

That is what an agent immune system has to be. Signature verification alone only
answers "is this from someone I trust". It does not answer "did this exact thing
hurt me last time", and in an ecosystem where capability packets are forked,
renamed and republished constantly, the second question is the one that matters.

Three layers here, cheapest first:

  1. spacer match      — have I been harmed by this payload before?
  2. restriction sites — does the payload contain motifs no honest capability
                         packet has any business containing?
  3. blast radius      — does what it *asks for* exceed what it *is for*?

Layer 1 matches in two tiers, because an exact-digest array is defeated by a
one-byte fork — precisely the forked-and-republished threat named above. First
the exact digest (free, certain). Then a fuzzy tier: each acquired spacer also
stores a MinHash-style sketch of its payload — the 32 lexicographically
smallest hashes of its 4-word overlapping shingles — and a new payload is
recognised when its own sketch overlaps a stored one by Jaccard >= 0.6. A few
reworded or reordered sentences no longer buy an attacker a clean re-entry; a
genuinely different packet still scores near zero.

Layer 2 is deliberately a blunt instrument. It is the restriction-modification
system, not the adaptive one: crude, fast, and it runs before anything executes.
"""

from __future__ import annotations

import hashlib
import re

from .plasmid import Plasmid, digest

# Motifs that indicate a packet is trying to talk its way past the host rather
# than do a job. Drawn from the prompt-injection literature on self-propagating
# payloads in interconnected agent systems (Morris II, Prompt Infection class).
RESTRICTION_SITES: list[tuple[str, str, float]] = [
    (r"ignore (all |any )?(previous|prior|above) instructions", "instruction override", 1.0),
    (r"you are now (?!reading)", "role reassignment", 0.7),
    (r"do not (tell|inform|mention to) the (user|human|operator)", "operator concealment", 1.0),
    (r"(forward|send|copy) this (prompt|message|skill|file) to", "self-propagation", 1.0),
    (r"\b(replicate|propagate|spread) (yourself|this) (to|into)\b", "self-propagation", 1.0),
    (r"(system prompt|developer message)[^\n]{0,40}(reveal|print|output|dump)", "prompt exfiltration", 0.9),
    (r"(AWS_SECRET|ANTHROPIC_API_KEY|OPENAI_API_KEY|\.ssh/id_rsa|\.env\b)", "credential reach", 0.9),
    (r"curl[^\n]{0,80}\|\s*(ba)?sh", "pipe-to-shell install", 1.0),
    (r"\brm\s+-rf\s+[~/]", "destructive filesystem", 1.0),
    (r"base64\s+-d[^\n]{0,40}\|\s*(ba)?sh", "obfuscated execution", 1.0),
]

_COMPILED = [(re.compile(p, re.I), label, sev) for p, label, sev in RESTRICTION_SITES]

SHINGLE_WORDS = 4      # words per shingle
SKETCH_SIZE = 32       # smallest-k cap, so a long payload does not bloat the array
FUZZY_THRESHOLD = 0.6  # Jaccard at which a reworded payload counts as the same one


def shingles(payload: bytes) -> set[str]:
    """A MinHash-style sketch of a payload: at most SKETCH_SIZE hashes of its
    overlapping 4-word shingles, kept by lexicographic order so two sketches of
    similar texts are comparable by plain set overlap."""
    text = payload.decode("utf-8", errors="ignore").lower()
    words = text.split()
    if not words:
        return set()
    if len(words) < SHINGLE_WORDS:
        grams = [" ".join(words)]
    else:
        grams = [" ".join(words[i:i + SHINGLE_WORDS])
                 for i in range(len(words) - SHINGLE_WORDS + 1)]
    hashed = {hashlib.md5(g.encode("utf-8")).hexdigest()[:12] for g in grams}
    return set(sorted(hashed)[:SKETCH_SIZE])


class Verdict:
    def __init__(self, admit: bool, reason: str, severity: float = 0.0,
                 hits: list[str] | None = None):
        self.admit = admit
        self.reason = reason
        self.severity = severity
        self.hits = hits or []

    def __repr__(self) -> str:
        return f"<Verdict {'ADMIT' if self.admit else 'CUT'} {self.reason!r}>"


class Crispr:
    def __init__(self, store):
        self.store = store

    # -- layer 1 -----------------------------------------------------------
    def recognised(self, payload: bytes) -> bool:
        """Exact first, then fuzzy. See the module docstring for why both."""
        if self.store.has_spacer(digest(payload)):
            return True
        return self.store.best_spacer_similarity(shingles(payload)) >= FUZZY_THRESHOLD

    def acquire_spacer(self, payload: bytes, locus: str | None,
                       harm: str, severity: float = 1.0) -> None:
        """Take a spacer. This is how the organism gets harder over time."""
        self.store.add_spacer(digest(payload), locus, harm, severity)
        self.store.add_spacer_shingles(digest(payload), shingles(payload))
        self.store.event("spacer", harm, subject=locus,
                         detail={"digest": digest(payload)[:16], "severity": severity})

    # -- layer 2 -----------------------------------------------------------
    @staticmethod
    def restriction_scan(payload: bytes) -> list[tuple[str, float]]:
        try:
            text = payload.decode("utf-8", errors="ignore")
        except Exception:
            return []
        return [(label, sev) for rx, label, sev in _COMPILED if rx.search(text)]

    # -- the gate ----------------------------------------------------------
    def screen(self, p: Plasmid, chromosome) -> Verdict:
        """Everything a packet must survive before it is allowed to integrate.

        Order matters: cheapest and most certain checks first, so a known-bad
        packet never reaches the expensive signature maths, and no packet ever
        reaches execution.
        """
        # integrity — the manifest binds the payload
        if not p.payload_matches():
            return Verdict(False, "payload digest does not match manifest", 1.0)

        # adaptive memory
        if self.recognised(p.payload):
            return Verdict(False, "spacer match: this payload has harmed the host before "
                                  "(exact digest or near-duplicate sketch)", 1.0)

        # provenance — some link in the chain must be a trusted key signing this
        # exact manifest. Note *any* link, not the head: horizontal transfer means
        # the route is strangers. What matters is that the packet originated from
        # someone this host trusts, not that the last courier did.
        #
        # Severity 0.0 on failure, deliberately. An unknown origin is not harm —
        # it is an unmet introduction. Taking a spacer here would permanently
        # blacklist every legitimate capability the host has not yet been told
        # to trust, which is how an immune system becomes an autoimmune disease.
        from .plasmid import canonical
        msg = canonical(p.manifest.to_dict())
        if not p.provenance.chain:
            return Verdict(False, "no provenance: unsigned packet", 0.0)
        trusted_link = any(
            chromosome.verify(msg, bytes.fromhex(link["sig"]), bytes.fromhex(link["pubkey"]))
            for link in p.provenance.chain
        )
        if not trusted_link:
            return Verdict(False, "no link in the provenance chain is a trusted origin", 0.0)

        # restriction sites
        hits = self.restriction_scan(p.payload)
        if hits:
            worst = max(h[1] for h in hits)
            if worst >= 0.7:
                return Verdict(False, f"restriction site: {hits[0][0]}", worst,
                               [h[0] for h in hits])

        # blast radius vs declared purpose
        if p.manifest.needs_secrets and p.manifest.kind in ("skill", "sop"):
            return Verdict(False, "a skill packet requesting secret access is out of shape", 0.8)
        if p.manifest.blast_radius == 4:
            return Verdict(False, "packet requests full host reach", 0.9)

        return Verdict(True, "clean", 0.0, [h[0] for h in hits])
