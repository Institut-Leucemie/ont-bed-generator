"""Per-strand extension, clamping to chromosome bounds, per-strand merging."""
from __future__ import annotations

from collections import defaultdict

from .model import DEFAULT_FLANK, Locus


def build_extended(
    loci: list[Locus],
    sizes: dict[str, int],
    flank: int = DEFAULT_FLANK,
) -> list[tuple]:
    """Two BED6 intervals per locus (+ / -), extended then clamped.

    "+" strand : [ start - flank - Left ,  end ]
    "-" strand : [ start          ,  end + flank + Right ]
    then clamped to [0, chrom_size] (equivalent to `bedtools slop -b 0`).
    """
    out: list[tuple] = []
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


def merge_stranded(intervals: list[tuple], rank: dict[str, int]) -> list[tuple]:
    """Merge per (chrom, strand): overlapping or book-ended (distance 0).

    names = sorted union joined by commas;
    score = minimum of the Extended_region flags;
    strand = preserved.
    Final sort: (genome order, start, end, strand).
    """
    groups: dict[tuple, list] = defaultdict(list)
    for iv in intervals:
        groups[(iv[0], iv[5])].append(iv)

    merged: list[tuple] = []
    for (chrom, strand), ivs in groups.items():
        ivs.sort(key=lambda x: (x[1], x[2]))
        cs = ce = None
        names: set[str] = set()
        score = 0
        for _c, s, e, name, sc, _st in ivs:
            if cs is None:
                cs, ce, names, score = s, e, {name}, sc
            elif s <= ce:
                ce = max(ce, e)
                names.add(name)
                score = min(score, sc)
            else:
                merged.append((chrom, cs, ce, ",".join(sorted(names)), score, strand))
                cs, ce, names, score = s, e, {name}, sc
        if cs is not None:
            merged.append((chrom, cs, ce, ",".join(sorted(names)), score, strand))

    merged.sort(key=lambda x: (rank.get(x[0], 1 << 30), x[1], x[2], x[5]))
    return merged
