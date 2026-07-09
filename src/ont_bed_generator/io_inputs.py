"""Input readers: genome sizes, genelist, GFF, external Entrez table."""
from __future__ import annotations

import gzip
from collections import defaultdict
from typing import IO

from .model import GeneSpec, GffGene


def _open(path: str) -> IO[str]:
    """Open a text file, transparently handling gzip-compressed (.gz) input."""
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path)


def read_genome(path: str) -> tuple[dict[str, int], dict[str, int]]:
    """Return (sizes, rank). `rank` = order of appearance = BED sort order."""
    sizes: dict[str, int] = {}
    rank: dict[str, int] = {}
    with _open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            p = line.split("\t")
            chrom, size = p[0], int(p[1])
            if chrom not in sizes:
                rank[chrom] = len(rank)
            sizes[chrom] = size
    if not sizes:
        raise ValueError(f"empty/unreadable genome file: {path}")
    return sizes, rank


def _field_int(fields: list[str], i: int) -> int:
    """Parse an integer from a TSV field, defaulting to 0 when absent/empty."""
    if len(fields) > i and fields[i].strip():
        try:
            return int(fields[i].strip())
        except ValueError:
            return 0
    return 0


def read_genelist(path: str) -> list[GeneSpec]:
    """Read the genelist TSV. The Chromosome column is intentionally ignored."""
    specs: list[GeneSpec] = []
    with _open(path) as fh:
        fh.readline()  # header
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            f = line.split("\t")
            raw = f[1] if len(f) > 1 else ""
            symbol = raw.strip()   # chomp whitespace/tabs (Excel habit), not a rename
            if not symbol:
                continue
            specs.append(
                GeneSpec(symbol, _field_int(f, 2), _field_int(f, 3), _field_int(f, 4), raw)
            )
    return specs


def _attrs(s: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for field in s.rstrip(";").split(";"):
        if "=" in field:
            k, _, v = field.partition("=")
            d[k.strip()] = v.strip()
    return d


class GffIndex:
    """Index of GFF `gene` features, keyed on Entrez (GeneID)."""

    def __init__(self) -> None:
        self.by_geneid: dict[str, list[GffGene]] = defaultdict(list)
        self.name_to_geneids: dict[str, set[str]] = defaultdict(set)
        self.geneid_name: dict[str, str] = {}

    @classmethod
    def load(cls, path: str) -> GffIndex:
        idx = cls()
        with _open(path) as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                c = line.rstrip("\n").split("\t")
                if len(c) < 9 or c[2] != "gene":
                    continue
                a = _attrs(c[8])
                entrez = None
                for tok in a.get("Dbxref", "").split(","):
                    if tok.startswith("GeneID:"):
                        entrez = tok.split(":", 1)[1]
                        break
                name = a.get("Name") or a.get("gene") or ""
                g = GffGene(c[0], int(c[3]), int(c[4]), c[6], entrez, name)
                # Without a GeneID, fall back to a synthetic key so nothing is lost.
                key = entrez if entrez is not None else f"NONAME:{name}:{c[0]}:{c[3]}"
                idx.by_geneid[key].append(g)
                idx.geneid_name.setdefault(key, name)
                if name:
                    idx.name_to_geneids[name].add(key)
        return idx


def read_entrez_map(path: str) -> dict[str, str]:
    """External SYMBOL<TAB>ENTREZID table (e.g. an org.Hs.eg.db export)."""
    m: dict[str, str] = {}
    with _open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            p = line.split("\t")
            if len(p) >= 2 and p[0].strip() and p[1].strip():
                m[p[0].strip()] = p[1].strip()
    return m
