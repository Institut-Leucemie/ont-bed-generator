"""Command-line interface."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .intervals import build_extended, merge_stranded
from .io_inputs import GffIndex, read_entrez_map, read_genelist, read_genome
from .io_outputs import write_bed, write_targets
from .model import DEFAULT_FLANK
from .resolve import resolve


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="ont-bed-generator",
        description="Generate targets.bed and merged-extended.bed for ONT adaptive sampling.")
    ap.add_argument("--genelist", required=True, help="genelist TSV")
    ap.add_argument("--gff", required=True,
                    help="GFF3, gene features (Name= + Dbxref=GeneID:)")
    ap.add_argument("--genome", required=True,
                    help="chrom<TAB>size, in the desired sort order")
    ap.add_argument("--out-targets", default="targets.bed")
    ap.add_argument("--out-merged", default="merged-extended.bed")
    ap.add_argument("--flank", type=int, default=DEFAULT_FLANK,
                    help=f"default per-strand flank (default {DEFAULT_FLANK})")
    ap.add_argument("--entrez-map",
                    help="external SYMBOL<TAB>ENTREZID table (takes priority)")
    ap.add_argument("--strict", action="store_true",
                    help="exit with code 1 if any symbol is invalid/ambiguous")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        sizes, rank = read_genome(args.genome)
        specs = read_genelist(args.genelist)
        gff = GffIndex.load(args.gff)
        entrez_map = read_entrez_map(args.entrez_map) if args.entrez_map else None
    except (OSError, ValueError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    res = resolve(specs, gff, entrez_map)

    n_targets = write_targets(res.loci, rank, args.out_targets)
    merged = merge_stranded(build_extended(res.loci, sizes, args.flank), rank)
    n_merged = write_bed(merged, args.out_merged)

    e = sys.stderr
    print(f"[ok] {len(specs)} input symbols", file=e)
    print(f"[ok] {n_targets} loci -> {args.out_targets}", file=e)
    print(f"[ok] {n_merged} merged intervals -> {args.out_merged}", file=e)
    if res.ambiguous:
        print(f"[ambiguous] {len(res.ambiguous)} symbol(s) mapping to multiple "
              f"GeneIDs (dropped):", file=e)
        for sym, gids in res.ambiguous:
            print(f"    {sym} -> GeneID {', '.join(gids)}", file=e)
    if res.invalid:
        print(f"[invalid] {len(res.invalid)} symbol(s) not found "
              f"(fix them in the source genelist):", file=e)
        for sym in res.invalid:
            print(f"    {sym}", file=e)

    if args.strict and (res.invalid or res.ambiguous):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
