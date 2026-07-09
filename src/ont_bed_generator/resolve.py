"""Resolve official gene symbols to loci, using the GFF Entrez key.

Policy: official HGNC symbols only (verifiable via
https://www.genenames.org/tools/multi-symbol-checker/). No synonym fallback,
no renaming. A symbol that is not found is reported, never guessed.
"""
from __future__ import annotations

from .io_inputs import GffIndex
from .model import GeneSpec, Locus, Resolution


def resolve(
    specs: list[GeneSpec],
    gff: GffIndex,
    entrez_map: dict[str, str] | None = None,
) -> Resolution:
    loci: list[Locus] = []
    ambiguous: list[tuple[str, list[str]]] = []
    invalid: list[str] = []
    seen: set[tuple] = set()

    for spec in specs:
        # External table first, then GFF Name=, otherwise invalid.
        if entrez_map is not None and spec.symbol in entrez_map:
            geneids = {entrez_map[spec.symbol]}
        elif spec.symbol in gff.name_to_geneids:
            geneids = set(gff.name_to_geneids[spec.symbol])
        else:
            invalid.append(spec.symbol)
            continue

        # A Name mapping to several distinct GeneIDs is ambiguous (e.g. tRNAs).
        if len(geneids) > 1:
            ambiguous.append((spec.symbol, sorted(geneids)))
            continue

        gid = next(iter(geneids))
        recs = gff.by_geneid.get(gid, [])
        if not recs:
            invalid.append(spec.symbol)
            continue

        # Collect by GeneID: handles PAR genes (chrX+chrY) and IG/TCR loci.
        for g in recs:
            start0 = g.start1 - 1
            out_name = g.name or spec.symbol
            key = (g.chrom, start0, g.end, out_name)
            if key in seen:
                continue
            seen.add(key)
            loci.append(
                Locus(g.chrom, start0, g.end, out_name,
                      spec.extended, spec.left, spec.right)
            )

    return Resolution(loci, ambiguous, invalid)
