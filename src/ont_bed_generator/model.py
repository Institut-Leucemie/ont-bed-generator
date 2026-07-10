"""Data structures and constants."""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_FLANK = 10000

# A BED6 row: (chrom, start, end, name, score, strand).
BedRow = tuple[str, int, int, str, int, str]


@dataclass
class GeneSpec:
    """One genelist row: symbol plus per-side extension sizes (bp)."""
    symbol: str
    left: int
    right: int

    @property
    def extended(self) -> int:
        """Derived flag: a region is 'extended' if it has a custom L/R size."""
        return 1 if (self.left or self.right) else 0


@dataclass
class GffGene:
    """A GFF `gene` feature (1-based, inclusive coordinates)."""
    chrom: str
    start1: int
    end: int
    strand: str
    entrez: str | None
    name: str


@dataclass
class Locus:
    """A resolved locus in BED coordinates (0-based, half-open)."""
    chrom: str
    start: int
    end: int
    name: str          # canonical GFF Name=
    left: int
    right: int

    @property
    def extended(self) -> int:
        """Derived flag: a region is 'extended' if it has a custom L/R size."""
        return 1 if (self.left or self.right) else 0


@dataclass
class Resolution:
    """Result of symbol -> loci resolution, with diagnostics."""
    loci: list[Locus]
    ambiguous: list[tuple[str, list[str]]]   # (symbol, [GeneID...])
    invalid: list[str]
