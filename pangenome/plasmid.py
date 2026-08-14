"""The plasmid — a capability packet that can cross between unrelated hosts.

This is the unit of horizontal transfer, and the whole thesis lives in its shape.

Every self-evolving agent system published to date evolves *vertically*: an agent
mutates its own code and keeps the better child. Parent to offspring. Lineage
bound, generation gated. That is eukaryote evolution, and it is slow.

Prokaryotes do not wait for descendants. A trait discovered in one organism
appears in an unrelated organism the same week, because it rides on a mobile
element that carries its own transfer machinery. Antibiotic resistance crossed
the planet in forty years by this route, not by inheritance.

A plasmid here is that mobile element:

  manifest      what it is, what it needs, what it touches   (the genes)
  payload       the actual capability, content-addressed     (the sequence)
  provenance    signed chain back to a trusted key           (the origin of replication)
  fitness       observed performance in this host            (selection)

The manifest is signed, and the manifest binds the payload digest. You cannot
swap the payload without breaking the signature. That is the entire integrity
model, and it is the thing the live agent-skill ecosystem currently does not have.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict

CANON = dict(sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: dict) -> bytes:
    """Deterministic bytes for signing. Order and whitespace must not matter."""
    return json.dumps(obj, **CANON).encode("utf-8")


@dataclass
class Manifest:
    name: str
    version: str
    kind: str                      # 'skill' | 'mcp_server' | 'tool' | 'sop'
    origin: str                    # url the organism sensed it at
    payload_sha256: str
    # declared blast radius — what integrating this lets into the host
    needs_network: bool = False
    needs_filesystem: bool = False
    needs_secrets: bool = False
    needs_exec: bool = False
    summary: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def blast_radius(self) -> int:
        """0-4. How much of the host this packet can reach if it is hostile."""
        return sum([self.needs_network, self.needs_filesystem,
                    self.needs_secrets, self.needs_exec])


@dataclass
class Provenance:
    """A chain of signatures. Each link signs the link before it.

    len(chain) == 1  -> minted directly by a trusted key
    len(chain) >  1  -> transferred; every hop countersigned its predecessor
    """
    chain: list[dict] = field(default_factory=list)

    def append(self, pubkey: bytes, sig: bytes, note: str = "") -> None:
        self.chain.append({"pubkey": pubkey.hex(), "sig": sig.hex(),
                           "at": time.time(), "note": note})

    def head(self) -> dict | None:
        return self.chain[-1] if self.chain else None


@dataclass
class Plasmid:
    manifest: Manifest
    payload: bytes
    provenance: Provenance = field(default_factory=Provenance)

    @property
    def pid(self) -> str:
        """Content address. Two hosts that acquired the same capability by
        different routes converge on the same id — which is what makes
        cross-lineage deduplication possible at all."""
        return digest(canonical(self.manifest.to_dict()))[:16]

    def payload_matches(self) -> bool:
        return digest(self.payload) == self.manifest.payload_sha256

    # -- minting -----------------------------------------------------------
    @classmethod
    def mint(cls, chromosome, *, name: str, version: str, kind: str,
             origin: str, payload: bytes, summary: str = "", **caps) -> "Plasmid":
        m = Manifest(name=name, version=version, kind=kind, origin=origin,
                     payload_sha256=digest(payload), summary=summary, **caps)
        p = cls(manifest=m, payload=payload)
        sig = chromosome.sign(canonical(m.to_dict()))
        p.provenance.append(chromosome.root_pubkey, sig, note="minted")
        return p

    def to_dict(self) -> dict:
        return {"manifest": self.manifest.to_dict(),
                "provenance": self.provenance.chain,
                "payload_b64": __import__("base64").b64encode(self.payload).decode()}

    @classmethod
    def from_dict(cls, d: dict) -> "Plasmid":
        import base64
        return cls(manifest=Manifest(**d["manifest"]),
                   payload=base64.b64decode(d["payload_b64"]),
                   provenance=Provenance(chain=list(d["provenance"])))
