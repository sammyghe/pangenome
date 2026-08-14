"""The core genome — the part that does not move.

A bacterial pan-genome splits in two:

  core genome       present in every strain. Slow. Vertical. Essential.
  accessory genome  present in some strains. Fast. Horizontal. Optional.

This module is the core. It holds exactly one thing that cannot be acquired,
traded, mutated, or voted on: the root identity. Everything else in the organism
is accessory and therefore disposable.

This is the answer to the tension between horizontal gene transfer and root
authority. You do not enforce lineage genetically — a plasmid does not care who
its parent was. You enforce it *cryptographically*: the root key signs, and the
integration gate refuses anything whose provenance chain does not terminate at a
key the chromosome trusts. Lineage is a signature, not an ancestry.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from . import ed25519

GENOME_DIR = Path(os.environ.get("PANGENOME_HOME", Path(__file__).resolve().parent.parent / "genome"))
ROOT_SECRET = GENOME_DIR / "root.key"          # never commit this
CHROMOSOME = GENOME_DIR / "chromosome.json"    # public, committed


class Chromosome:
    """Root identity + the trust set that gates every integration."""

    def __init__(self, path: Path = CHROMOSOME):
        self.path = Path(path)
        self._sk: bytes | None = None
        self.data = json.loads(self.path.read_text()) if self.path.exists() else None

    # -- lifecycle ---------------------------------------------------------
    @classmethod
    def germinate(cls, name: str, steward: str, force: bool = False) -> "Chromosome":
        """Create the organism. Runs once, ever."""
        GENOME_DIR.mkdir(parents=True, exist_ok=True)
        if CHROMOSOME.exists() and not force:
            raise RuntimeError("chromosome already exists — an organism germinates once")
        sk, pk = ed25519.keygen()
        ROOT_SECRET.write_bytes(sk)
        try:
            os.chmod(ROOT_SECRET, 0o600)
        except OSError:
            pass  # windows
        CHROMOSOME.write_text(json.dumps({
            "name": name,
            "steward": steward,
            "root_pubkey": pk.hex(),
            "trusted": [pk.hex()],
            "constitution_sha256": _constitution_digest(),
            "schema": 1,
        }, indent=2) + "\n")
        return cls()

    @classmethod
    def ephemeral(cls, name: str, trusted: list[bytes] | None = None) -> "Chromosome":
        """An in-memory chromosome for simulation. Never touches disk, so a
        population of hundreds can be instantiated without leaving key material
        anywhere."""
        sk, pk = ed25519.keygen()
        c = cls.__new__(cls)
        c.path = None
        c._sk = sk
        c.data = {
            "name": name,
            "steward": "simulation",
            "root_pubkey": pk.hex(),
            "trusted": [pk.hex()] + [t.hex() for t in (trusted or [])],
            "constitution_sha256": "",
            "schema": 1,
        }
        return c

    # -- identity ----------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self.data is not None

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def root_pubkey(self) -> bytes:
        return bytes.fromhex(self.data["root_pubkey"])

    @property
    def trusted(self) -> set[bytes]:
        return {bytes.fromhex(h) for h in self.data["trusted"]}

    @property
    def can_sign(self) -> bool:
        return (getattr(self, "_sk", None) is not None
                or ROOT_SECRET.exists()
                or bool(os.environ.get("PANGENOME_ROOT_KEY")))

    def _secret(self) -> bytes:
        if getattr(self, "_sk", None) is not None:
            return self._sk
        env = os.environ.get("PANGENOME_ROOT_KEY")
        if env:
            return bytes.fromhex(env.strip())
        if not ROOT_SECRET.exists():
            raise RuntimeError(
                "root.key is absent — this instance can verify but cannot sign."
            )
        return ROOT_SECRET.read_bytes()

    # -- crypto ------------------------------------------------------------
    def sign(self, payload: bytes) -> bytes:
        return ed25519.sign(payload, self._secret(), self.root_pubkey)

    def verify(self, payload: bytes, sig: bytes, pubkey: bytes) -> bool:
        """Signature must be valid AND the signer must be in the trust set.

        Both halves matter. A valid signature from an untrusted key is exactly
        what a hostile capability packet looks like.
        """
        return pubkey in self.trusted and ed25519.verify(sig, payload, pubkey)

    def trust(self, pubkey: bytes, why: str) -> None:
        """Widen the trust set. The only privileged operation in the system."""
        h = pubkey.hex()
        if h in self.data["trusted"]:
            return
        self.data["trusted"].append(h)
        self.data.setdefault("trust_log", []).append({"key": h, "why": why})
        if self.path is not None:
            self.path.write_text(json.dumps(self.data, indent=2) + "\n")


def _constitution_digest() -> str:
    import hashlib
    c = GENOME_DIR.parent / "CONSTITUTION.md"
    if not c.exists():
        return ""
    return hashlib.sha256(c.read_bytes()).hexdigest()
