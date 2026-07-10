"""Output BED writers."""
from __future__ import annotations

from .model import BedRow, Locus
from .ordering import chrom_sort_key


def write_targets(loci: list[Locus], path: str) -> int:
    """targets.bed: (chrom, start, end, Name, 0, .), deduplicated, sorted."""
    seen: set[tuple[str, int, int, str]] = set()
    rows: list[BedRow] = []
    for lo in loci:
        key = (lo.chrom, lo.start, lo.end, lo.name)
        if key in seen:
            continue
        seen.add(key)
        rows.append((lo.chrom, lo.start, lo.end, lo.name, 0, "."))
    rows.sort(key=lambda x: (chrom_sort_key(x[0]), x[1], x[2], x[3]))
    with open(path, "w") as fh:
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    return len(rows)


def write_bed(rows: list[BedRow], path: str) -> int:
    """Write a list of already-ordered BED tuples."""
    with open(path, "w") as fh:
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    return len(rows)
