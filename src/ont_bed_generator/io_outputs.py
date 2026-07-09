"""Output BED writers."""
from __future__ import annotations

from .model import Locus


def write_targets(loci: list[Locus], rank: dict[str, int], path: str) -> int:
    """targets.bed: (chrom, start, end, Name, 0, .), deduplicated, sorted."""
    seen: set[tuple] = set()
    rows: list[tuple] = []
    for lo in loci:
        key = (lo.chrom, lo.start, lo.end, lo.name)
        if key in seen:
            continue
        seen.add(key)
        rows.append((lo.chrom, lo.start, lo.end, lo.name, 0, "."))
    rows.sort(key=lambda x: (rank.get(x[0], 1 << 30), x[1], x[2], x[3]))
    with open(path, "w") as fh:
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    return len(rows)


def write_bed(rows: list[tuple], path: str) -> int:
    """Write a list of already-ordered BED tuples."""
    with open(path, "w") as fh:
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    return len(rows)
