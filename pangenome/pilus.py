"""The pilus — the conjugation protocol.

Conjugation is the part biology got right and the agent ecosystem has not built.
A donor extends a physical bridge, the plasmid crosses, and — the detail that
matters — the recipient's restriction system inspects the arriving DNA *before*
it can be expressed. Transfer and admission are two separate steps with a gate
between them. In the current skill and MCP ecosystem they are one step: acquiring
a package is installing it, with the host agent's full privileges, unsandboxed
and unverified.

So this is the missing standard: how a capability packet transfers, verifies and
integrates between agents that were never designed together.

    ADVERTISE   donor publishes {pid, manifest digest, blast radius}. No payload.
    REQUEST     recipient asks only for pids it lacks, minus its CRISPR array.
    TRANSFER    payload crosses. Still not admitted.
    SCREEN      integrity -> spacers -> provenance -> restriction sites -> radius.
    QUARANTINE  the packet's declared shape is checked against its actual
                content. No code from the packet is run — not sandboxed, not
                run at all. Nothing arriving from outside executes with host
                authority. Ever. There is no flag for it.
    INTEGRATE   admitted DORMANT (lysogenic), not active. Acquisition is not
                expression. This is what keeps acquisition cheap enough to be
                aggressive about.

One direction only. See safety.py: the organism pulls, it never pushes. `donate`
exists so a population can be simulated inside a single process, and is refused
across a network boundary by construction — there is no network path out.
"""

from __future__ import annotations

from dataclasses import dataclass

from .crispr import Crispr, Verdict
from .lysogeny import LYSOGENIC, EXCISED
from .plasmid import Plasmid, canonical


@dataclass
class Advert:
    pid: str
    name: str
    kind: str
    manifest_digest: str
    blast_radius: int


class Quarantine:
    """Where a packet is exercised without host authority.

    Deliberately conservative: this runs *no* code from the packet. It checks the
    packet's declared shape against its actual content, which is the class of
    failure that catches mislabelled and repackaged capabilities — the dominant
    real-world case. Executing untrusted payloads safely needs process-level
    isolation, so the honest thing is to not pretend to do it here.
    """

    @staticmethod
    def trial(p: Plasmid) -> tuple[bool, str]:
        text = p.payload.decode("utf-8", errors="ignore")
        if not text.strip():
            return False, "empty payload"
        if len(p.payload) > 512_000:
            return False, "payload exceeds 500KB — capability packets are documents, not archives"
        declared_exec = p.manifest.needs_exec
        looks_exec = any(m in text for m in ("subprocess.", "os.system", "child_process",
                                             "eval(", "exec(", "#!/bin/"))
        if looks_exec and not declared_exec:
            return False, "payload executes but the manifest does not declare needs_exec"
        declared_net = p.manifest.needs_network
        looks_net = any(m in text for m in ("http://", "https://", "requests.", "fetch(",
                                            "urllib", "axios"))
        if looks_net and not declared_net and p.manifest.kind in ("skill", "sop"):
            return False, "payload reaches the network but the manifest does not declare it"
        return True, "shape matches manifest"


class Pilus:
    def __init__(self, host):
        self.host = host                 # an Organism
        self.crispr: Crispr = host.crispr

    # -- donor side (in-process only) --------------------------------------
    def advertise(self) -> list[Advert]:
        out = []
        for row in self.host.store.plasmids():
            if row["state"] == EXCISED:
                continue
            import json
            m = json.loads(row["manifest"])
            out.append(Advert(pid=row["pid"], name=m["name"], kind=m["kind"],
                              manifest_digest=row["pid"], blast_radius=sum([
                                  m.get("needs_network", False),
                                  m.get("needs_filesystem", False),
                                  m.get("needs_secrets", False),
                                  m.get("needs_exec", False)])))
        return out

    # -- recipient side ----------------------------------------------------
    def wants(self, adverts: list[Advert]) -> list[str]:
        """What to ask for. Cheap filter, before any payload moves."""
        have = {r["pid"] for r in self.host.store.plasmids()}
        return [a.pid for a in adverts
                if a.pid not in have and a.blast_radius < 4]

    def receive(self, p: Plasmid) -> Verdict:
        """The gate. Nothing enters the genome except through here."""
        v = self.crispr.screen(p, self.host.chromosome)
        if not v.admit:
            # Only remember what actually harmed us. Refusing a stranger is not
            # an injury, and a spacer is permanent.
            if v.severity >= 0.7:
                self.crispr.acquire_spacer(p.payload, p.manifest.origin, v.reason, v.severity)
            self.host.store.event("reject", v.reason, subject=p.pid,
                                  detail={"name": p.manifest.name, "hits": v.hits})
            self.host.store.commit()
            return v

        ok, why = Quarantine.trial(p)
        if not ok:
            self.crispr.acquire_spacer(p.payload, p.manifest.origin,
                                       f"quarantine: {why}", 0.8)
            self.host.store.event("reject", f"quarantine: {why}", subject=p.pid,
                                  detail={"name": p.manifest.name})
            self.host.store.commit()
            return Verdict(False, f"quarantine: {why}", 0.8)

        # admitted — dormant, not running
        self.host.store.put_plasmid(p.pid, p.manifest.to_dict(), LYSOGENIC)
        self.host.store.event(
            "integrate",
            f"admitted lysogenic: {p.manifest.name}@{p.manifest.version}",
            subject=p.pid,
            detail={"kind": p.manifest.kind, "origin": p.manifest.origin,
                    "blast_radius": p.manifest.blast_radius,
                    "hops": len(p.provenance.chain)})
        self.host.store.commit()
        return Verdict(True, "integrated lysogenic", 0.0, v.hits)

    # -- transfer ----------------------------------------------------------
    def conjugate(self, donor: "Pilus", pids: list[str],
                  bank: dict[str, Plasmid]) -> dict[str, Verdict]:
        """Move plasmids donor -> self. In-process only.

        `bank` is the donor's payload store. There is no serialisation over a
        socket here and there will not be one: an outbound transfer path is the
        single thing this project will not build.
        """
        results = {}
        for pid in pids:
            p = bank.get(pid)
            if p is None:
                continue
            # counter-sign the hop so the chain records the route it took
            hop_sig = donor.host.chromosome.sign(canonical(p.manifest.to_dict()))
            p.provenance.append(donor.host.chromosome.root_pubkey, hop_sig,
                                note=f"conjugated from {donor.host.name}")
            results[pid] = self.receive(p)
        return results
