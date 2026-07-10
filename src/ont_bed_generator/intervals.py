"""Per-strand extension, clamping to chromosome bounds, per-strand merging."""
from __future__ import annotations

from collections import defaultdict

from .model import DEFAULT_FLANK, BedRow, Locus
from .ordering import chrom_sort_key


def build_extended(
    loci: list[Locus],
    sizes: dict[str, int],
    flank: int = DEFAULT_FLANK,
) -> list[BedRow]:
    """Two BED6 intervals per locus (+ / -), extended then clamped.

    "+" strand : [ start - flank - Left ,  end ]
    "-" strand : [ start          ,  end + flank + Right ]
    then clamped to [0, chrom_size] (equivalent to `bedtools slop -b 0`).
    """
    out: list[BedRow] = []
    for lo in loci:
        size = sizes.get(lo.chrom)
        if size is None:
            raise ValueError(f"chromosome missing from genome file: {lo.chrom}")

        def clamp(x: int, _s: int = size) -> int:
            return max(0, min(x, _s))

        out.append((lo.chrom, clamp(lo.start - flank - lo.left),
                    clamp(lo.end), lo.name, lo.extended, "+"))
        out.append((lo.chrom, clamp(lo.start),
                    clamp(lo.end + flank + lo.right), lo.name, lo.extended, "-"))
    return out


def merge_stranded(intervals: list[BedRow]) -> list[BedRow]:
    """Merge per (chrom, strand): overlapping or book-ended (distance 0).

    names = sorted union joined by commas;
    score = minimum of the Extended_region flags;
    strand = preserved.
    Final sort: canonical karyotypic order, then start, end, strand.
    """
    groups: dict[tuple[str, str], list[BedRow]] = defaultdict(list)
    for iv in intervals:
        groups[(iv[0], iv[5])].append(iv)

    merged: list[BedRow] = []
    for (chrom, strand), ivs in groups.items():
        ivs.sort(key=lambda x: (x[1], x[2]))
        start = end = 0
        names: set[str] = set()
        score = 0
        has_open = False
        for _c, s, e, name, sc, _st in ivs:
            if not has_open:
                start, end, names, score, has_open = s, e, {name}, sc, True
            elif s <= end:
                end = max(end, e)
                names.add(name)
                score = min(score, sc)
            else:
                merged.append((chrom, start, end, ",".join(sorted(names)), score, strand))
                start, end, names, score = s, e, {name}, sc
        if has_open:
            merged.append((chrom, start, end, ",".join(sorted(names)), score, strand))

    merged.sort(key=lambda x: (chrom_sort_key(x[0]), x[1], x[2], x[5]))
    return merged
