"""Data structures and constants."""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_FLANK = 10000


@dataclass
class GeneSpec:
    """One genelist row (cleaned symbol plus extension parameters)."""
    symbol: str
    extended: int
    left: int
    right: int
    raw_symbol: str


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
    extended: int
    left: int
    right: int


@dataclass
class Resolution:
    """Result of symbol -> loci resolution, with diagnostics."""
    loci: list[Locus]
    ambiguous: list[tuple[str, list[str]]]   # (symbol, [GeneID...])
    invalid: list[str]
