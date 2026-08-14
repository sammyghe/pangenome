"""The organism. One loop, eight beats, then it dies until the next heartbeat.

The whole architecture exists to make this loop cheap enough to run forever on
free infrastructure, and honest enough that nothing enters the genome unchecked.

    WAKE      load the chromosome. Verify the constitution is unmodified.
    SENSE     pull the public registries. Read-only, allowlisted, no auth needed.
    DIAGNOSE  fit growth curves. Which capabilities are in outbreak right now.
    DESIRE    emit an autoinducer per wanted capability. Density, not decision.
    ACQUIRE   for quorate wants only: mint, screen, quarantine, integrate dormant.
    EXPRESS   CI/Cro per prophage. Almost everything stays lysogenic. That is why
              this is affordable.
    IDENTIFY  recompute the consensus genome across the swarm. Report diversity.
    RECORD    append to the store, write STATE.md, exit.

Note what is *not* here: there is no idle process, no server, no always-on
runtime. The organism is dormant between heartbeats and costs nothing while
dormant, which is the lysogenic answer to "how does it stay alive for ten years
on nothing". Its body is a git repository. Its metabolism is a scheduled runner.
Its memory is a commit.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from . import epidemiology
from .chromosome import Chromosome, GENOME_DIR
from .crispr import Crispr
from .lysogeny import LYTIC, LYSOGENIC, Prophage
from .plasmid import Plasmid
from .quasispecies import Swarm
from .quorum import Medium
from .store import Store

# how many outbreak loci the organism may try to acquire per heartbeat
ACQUISITION_BUDGET = 8
# autoinducer concentration at which a want becomes an action
QUORUM_THRESHOLD = 3.0


class Organism:
    def __init__(self, store: Store | None = None, chromosome: Chromosome | None = None):
        self.store = store or Store()
        self.chromosome = chromosome or Chromosome()
        if not self.chromosome.alive:
            raise RuntimeError("no chromosome — run `pangenome germinate` first")
        self.crispr = Crispr(self.store)
        self.medium = Medium(self.store)
        self.name = self.chromosome.name
        from .pilus import Pilus
        self.pilus = Pilus(self)
        self.prophages: dict[str, Prophage] = {}

    # ---- beat 1 ----------------------------------------------------------
    def wake(self) -> dict:
        c = Path(__file__).resolve().parent.parent / "CONSTITUTION.md"
        current = hashlib.sha256(c.read_bytes()).hexdigest() if c.exists() else ""
        recorded = self.chromosome.data.get("constitution_sha256", "")
        drift = bool(recorded) and current != recorded
        if drift:
            # Not fatal — the steward is allowed to amend it. But it is logged
            # loudly, because a silently rewritten constitution is the failure
            # mode that makes every other guarantee here worthless.
            self.store.event("tick", "CONSTITUTION CHANGED since germination",
                             detail={"was": recorded[:16], "now": current[:16]})
        for row in self.store.plasmids():
            self.prophages[row["pid"]] = Prophage(row["pid"], state=row["state"])
        return {"constitution_drift": drift, "prophages": len(self.prophages)}

    # ---- beat 2 ----------------------------------------------------------
    def sense(self) -> dict:
        from .observers import OBSERVERS
        counts, failures = {}, 0
        for cls in OBSERVERS:
            try:
                counts[cls.name] = cls(self.store).sense()
            except Exception as e:                      # an organ can fail
                failures += 1
                counts[cls.name] = 0
                self.store.event("sense", f"{cls.name} failed: {type(e).__name__}: {e}")
        self.store.commit()
        self.stress = failures / max(1, len(OBSERVERS))
        return counts

    # ---- beat 3 ----------------------------------------------------------
    def diagnose(self) -> list[dict]:
        return epidemiology.outbreak_table(self.store)

    # ---- beat 4 ----------------------------------------------------------
    def desire(self, table: list[dict]) -> list[dict]:
        """Emit an autoinducer per wanted capability. No decision is taken here.

        The signal's strength depends on the quality of the evidence:

          fitted outbreak   strong  — the organism watched it grow itself
          since-inception   weak    — inherited from the locus's own history

        Because autoinducers accumulate across heartbeats and decay between
        them, a weak signal only reaches quorum if it is re-emitted day after
        day. That is the mechanism doing what it is for: the organism is
        structurally incapable of acquiring anything on the strength of a single
        snapshot, and nobody had to write a rule saying "wait a few days".
        """
        have = {json.loads(r["manifest"])["origin"] for r in self.store.plasmids()}
        wants = []
        for row in table:
            if row["locus"] in have:
                continue
            if row["phase"] in ("outbreak", "decelerating") and row["R0"]:
                strength = min(2.0, max(0.2, row["R0"] - 1.0))
            elif row["lifetime_r"] and row["lifetime_r"] > 0.002:
                strength = min(0.6, row["lifetime_r"] * 60)
            else:
                continue
            self.medium.emit(f"want:{row['locus']}", self.name, strength)
            wants.append(row)
        return wants[: ACQUISITION_BUDGET * 4]

    # ---- beat 5 ----------------------------------------------------------
    def acquire(self, wants: list[dict]) -> dict:
        """Only act on quorate species. Below quorum the organism has noticed
        something once; above it, the ecosystem is telling it the same thing from
        many directions, which is the only evidence available that a capability
        is real rather than a spike."""
        admitted, refused, waiting = 0, 0, 0

        # A host with no signing key can sense, measure and record, but cannot
        # mint. That is the intended posture for the public scheduled runner:
        # the always-online instance holds no signing authority, so compromising
        # it cannot widen what the organism will trust. Growing the genome is
        # reserved to an instance holding root.key.
        if not self.chromosome.can_sign:
            self.store.event("acquire", "no signing key on this host — "
                                        "sensing only, genome unchanged")
            self.store.commit()
            return {"admitted": 0, "refused": 0, "below_quorum": len(wants),
                    "read_only": True}

        for row in wants:
            if admitted >= ACQUISITION_BUDGET:
                break
            gate = self.medium.response(f"want:{row['locus']}", QUORUM_THRESHOLD)
            if gate < 0.5:
                waiting += 1
                continue

            payload, meta = self._payload_for(row["source"], row["locus"])
            if payload is None:
                continue
            p = Plasmid.mint(
                self.chromosome,
                name=row["locus"], version=str(meta.get("version") or "observed"),
                kind="mcp_server" if row["source"] == "mcp_registry" else "skill",
                origin=row["locus"], payload=payload,
                summary=(meta.get("description") or "")[:280],
                needs_network=row["source"] == "mcp_registry",
                needs_exec=row["source"] == "mcp_registry",
            )
            v = self.pilus.receive(p)
            if v.admit:
                admitted += 1
                self.prophages[p.pid] = Prophage(p.pid, state=LYSOGENIC)
            else:
                refused += 1
        return {"admitted": admitted, "refused": refused, "below_quorum": waiting}

    def _payload_for(self, source: str, locus: str) -> tuple[bytes | None, dict]:
        rows = self.store.q(
            "SELECT version, payload FROM observations WHERE source=? AND locus=?"
            " ORDER BY seen_at DESC LIMIT 1", (source, locus))
        if not rows:
            return None, {}
        meta = json.loads(rows[0]["payload"])
        meta["version"] = rows[0]["version"]
        body = json.dumps({"locus": locus, "source": source, **meta},
                          indent=2, sort_keys=True)
        return body.encode("utf-8"), meta

    # ---- beat 6 ----------------------------------------------------------
    def express(self) -> dict:
        """Almost everything should stay dormant. If this number climbs, the
        organism is becoming expensive and something is wrong upstream."""
        lytic = 0
        for pid, ph in self.prophages.items():
            demand = self.medium.concentration(f"use:{pid}")
            state = ph.decide(demand=demand, stress=getattr(self, "stress", 0.0))
            if state != LYTIC:
                state = LYSOGENIC if state != "excised" else state
            self.store.set_state(pid, state)
            if state == LYTIC:
                lytic += 1
        self.store.commit()
        return {"lytic": lytic, "lysogenic": len(self.prophages) - lytic,
                "cost_units": lytic}

    # ---- beat 7 ----------------------------------------------------------
    def identify(self) -> dict:
        swarm = Swarm(self.name)
        for row in self.store.plasmids():
            m = json.loads(row["manifest"])
            swarm.add(row["pid"], {
                "kind": m["kind"],
                "needs_network": m.get("needs_network", False),
                "needs_exec": m.get("needs_exec", False),
            }, fitness=row["fitness"] + row["wins"])
        # observed mutation rate: fraction of watched loci that changed version
        # since the previous heartbeat
        mu = self._mutation_rate()
        return swarm.report(genome_length=3, mu=mu)

    def _mutation_rate(self) -> float:
        rows = self.store.q(
            "SELECT source, locus, COUNT(DISTINCT version) v, COUNT(*) n"
            " FROM observations WHERE version IS NOT NULL GROUP BY source, locus")
        if not rows:
            return 0.0
        return sum((r["v"] - 1) / max(1, r["n"] - 1) for r in rows) / len(rows)

    # ---- beat 8 ----------------------------------------------------------
    def heartbeat(self) -> dict:
        t0 = time.time()
        report = {"at": t0, "organism": self.name}
        report["wake"] = self.wake()
        report["sense"] = self.sense()
        table = self.diagnose()
        report["watching"] = len(table)
        report["fittable"] = sum(1 for r in table if r["phase"] != "no-history")
        fitted = [r for r in table if r["phase"] == "outbreak"]
        # Before the organism has its own longitudinal series there is nothing to
        # fit, so the table falls back to since-inception growth — labelled as
        # such, never presented as an R0.
        report["outbreaks"] = (fitted or sorted(
            [r for r in table if r["lifetime_r"]],
            key=lambda r: -r["lifetime_r"]))[:10]
        wants = self.desire(table)
        report["wants"] = len(wants)
        report["acquire"] = self.acquire(wants)
        report["express"] = self.express()
        report["identity"] = self.identify()
        report["seconds"] = round(time.time() - t0, 2)

        self.store.event("tick", "heartbeat complete", detail={
            k: report[k] for k in ("sense", "watching", "wants", "acquire", "express")})
        self.store.commit()
        self._write_state(report)
        return report

    def _write_state(self, r: dict) -> None:
        GENOME_DIR.mkdir(parents=True, exist_ok=True)
        (GENOME_DIR / "last_heartbeat.json").write_text(
            json.dumps(r, indent=2, default=str) + "\n")
        ident = r["identity"]
        lines = [
            f"# {self.name} — state",
            "",
            f"heartbeat: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(r['at']))}"
            f"  ({r['seconds']}s)",
            "",
            "## body",
            f"- capabilities in genome: {ident['variants']}",
            f"- expressed (costing): {r['express']['lytic']}",
            f"- dormant (free): {r['express']['lysogenic']}",
            f"- swarm diversity: {ident['diversity_nats']} nats — {ident['status']}",
            f"- observed mutation rate: {ident['observed_mu']} "
            f"(error threshold {ident['error_threshold']})",
            "",
            "## senses",
            *[f"- {k}: {v} loci" for k, v in r["sense"].items()],
            f"- watching {r['watching']} loci with enough history to fit",
            "",
            f"- {r['fittable']} of them have enough distinct days to fit a rate",
            "",
            "## fastest-spreading right now",
            "",
            "`R0` is a fitted reproduction number and appears only once this "
            "organism has watched a locus across several days. `lifetime r` is "
            "mean growth since the locus was created — available immediately, "
            "and a different quantity. Never compare them.",
            "",
            "| locus | R0 | lifetime r | signal | phase | fit r2 |",
            "|---|---:|---:|---:|---|---:|",
            *[f"| `{o['locus']}` | {o['R0'] or '—'} | {o['lifetime_r'] or '—'} | "
              f"{o['signal'] or '—'} | {o['phase']} | {o['fit_r2'] or '—'} |"
              for o in r["outbreaks"]],
            "",
            "## immune system",
            f"- admitted this beat: {r['acquire']['admitted']}",
            f"- refused this beat: {r['acquire']['refused']}",
            f"- below quorum (waiting): {r['acquire']['below_quorum']}",
            f"- spacers held: {len(self.store.q('SELECT 1 FROM spacers'))}",
            "",
            "_Generated by the organism. Do not edit — it is overwritten every heartbeat._",
        ]
        (GENOME_DIR / "STATE.md").write_text("\n".join(lines) + "\n")
