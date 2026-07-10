"""Canonical karyotypic ordering of chromosome names.

Organism-agnostic: numbered autosomes first in numeric order (chr1, chr2, ...,
chr9, chr10, ...), then sex chromosomes (X, Y; also Z, W for other clades), then
the mitochondrion (M / MT), then any remaining contigs alphabetically. No
hard-coded per-organism list, so it works for human, mouse, etc.
"""
from __future__ import annotations


def chrom_sort_key(chrom: str) -> tuple[int, int, str]:
    """Sort key placing chromosome names in canonical karyotypic order."""
    name = chrom[3:] if chrom.lower().startswith("chr") else chrom
    if name.isdigit():
        return (0, int(name), "")
    special = {"X": 0, "Y": 1, "Z": 2, "W": 3, "M": 4, "MT": 4}
    rank = special.get(name.upper())
    if rank is not None:
        return (1, rank, "")
    return (2, 0, name)
