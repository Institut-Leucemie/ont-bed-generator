"""Geometry tests: extension, clamping, merging, and optional bedtools parity."""
from __future__ import annotations

import shutil
import subprocess

import pytest

from ont_bed_generator import (
    GffIndex,
    build_extended,
    merge_stranded,
    read_genelist,
    read_genome,
    resolve,
)
from ont_bed_generator.model import Locus


def _pipeline(genelist, gff, genome, flank):
    sizes, rank = read_genome(str(genome))
    specs = read_genelist(str(genelist))
    idx = GffIndex.load(str(gff))
    res = resolve(specs, idx)
    merged = merge_stranded(build_extended(res.loci, sizes, flank), rank)
    return res, merged, rank


def test_clamp_to_chrom_end():
    # locus near the telomere: the "-" extension must be clamped to chrom size
    sizes = {"c": 100}
    loci = [Locus("c", 80, 90, "G", 0, 0, 0)]
    plus, minus = build_extended(loci, sizes, flank=50)
    assert minus[2] == 100, "right extension must be clamped to chrom size"
    assert plus[1] == 30, "80 - 50 = 30, no negative clamp here"


def test_clamp_negative_start_to_zero():
    sizes = {"c": 100}
    loci = [Locus("c", 10, 20, "G", 0, 0, 0)]
    plus, _ = build_extended(loci, sizes, flank=50)
    assert plus[1] == 0, "10 - 50 must be clamped to 0"


def test_strand_specific_merge_expected(genelist_path, gff_path, genome_path):
    _res, merged, _rank = _pipeline(genelist_path, gff_path, genome_path, flank=100)
    expected = [
        ("chr1", 900, 2500, "GENEA,GENEB", 0, "+"),
        ("chr1", 1000, 2600, "GENEA,GENEB", 0, "-"),
        ("chrX", 900, 2000, "PARG", 0, "+"),
        ("chrX", 1000, 2100, "PARG", 0, "-"),
        ("chrY", 1399, 2500, "PARG", 0, "+"),
        ("chrY", 1499, 2600, "PARG", 0, "-"),
    ]
    assert merged == expected


@pytest.mark.skipif(shutil.which("bedtools") is None,
                    reason="bedtools not on PATH")
def test_bedtools_merge_parity(tmp_path, genelist_path, gff_path, genome_path):
    """Pure-Python merge must equal `bedtools merge -s` on lexicographically
    sorted input (the correct reference; cf. the genome-order artifact)."""
    sizes, rank = read_genome(str(genome_path))
    specs = read_genelist(str(genelist_path))
    idx = GffIndex.load(str(gff_path))
    res = resolve(specs, idx)
    ext = build_extended(res.loci, sizes, flank=100)

    pre = tmp_path / "pre.bed"
    with pre.open("w") as fh:
        for r in sorted(ext, key=lambda x: (x[0], x[1], x[2])):
            fh.write("\t".join(map(str, r)) + "\n")

    out = subprocess.run(
        ["bedtools", "merge", "-s", "-d", "0", "-i", str(pre),
         "-c", "4,5,6", "-o", "distinct,min,distinct"],
        capture_output=True, text=True, check=True,
    ).stdout

    bt = set()
    for line in out.splitlines():
        c = line.split("\t")
        bt.add((c[0], int(c[1]), int(c[2]), c[3], int(c[4]), c[5]))

    mine = set(merge_stranded(ext, rank))
    assert mine == bt
