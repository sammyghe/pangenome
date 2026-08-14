"""pangenome — a prokaryotic architecture for LLM agent ecosystems.

The core genome does not move. The accessory genome does.
"""

__version__ = "0.1.0"

from .chromosome import Chromosome
from .organism import Organism
from .plasmid import Plasmid, Manifest
from .store import Store

__all__ = ["Chromosome", "Organism", "Plasmid", "Manifest", "Store", "__version__"]
