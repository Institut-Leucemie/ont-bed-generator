"""ont_bed_generator — BED file generation for Oxford Nanopore adaptive sampling.

Standalone reimplementation (standard library only) of the Galaxy workflow
"Adaptative ONT BED file generation".
"""
from __future__ import annotations

from .intervals import build_extended, merge_stranded
from .io_inputs import GffIndex, read_entrez_map, read_genelist, read_genome
from .io_outputs import write_bed, write_targets
from .model import DEFAULT_FLANK, GeneSpec, GffGene, Locus, Resolution
from .resolve import resolve

# Version is derived from git tags by hatch-vcs (see pyproject.toml).
try:
    from ._version import __version__
except Exception:  # pragma: no cover - source tree without a build/tag
    __version__ = "0+unknown"

__all__ = [
    "GeneSpec", "GffGene", "Locus", "Resolution", "DEFAULT_FLANK",
    "read_genome", "read_genelist", "read_entrez_map", "GffIndex",
    "resolve", "build_extended", "merge_stranded",
    "write_targets", "write_bed", "__version__",
]
