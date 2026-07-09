"""Tests for symbol -> loci resolution."""
from __future__ import annotations

from ont_bed_generator import GffIndex, read_genelist, resolve


def test_par_gene_gives_two_loci(genelist_path, gff_path):
    specs = read_genelist(str(genelist_path))
    gff = GffIndex.load(str(gff_path))
    res = resolve(specs, gff)

    parg = [lo for lo in res.loci if lo.name == "PARG"]
    assert {lo.chrom for lo in parg} == {"chrX", "chrY"}, \
        "a PAR gene (same GeneID on X and Y) must yield two loci"


def test_trailing_space_is_chomped(genelist_path, gff_path):
    # 'GENEA ' (Excel whitespace) must resolve as 'GENEA'
    specs = read_genelist(str(genelist_path))
    gff = GffIndex.load(str(gff_path))
    res = resolve(specs, gff)
    assert any(lo.name == "GENEA" for lo in res.loci)


def test_ambiguous_symbol_is_flagged_not_guessed(genelist_path, gff_path):
    specs = read_genelist(str(genelist_path))
    gff = GffIndex.load(str(gff_path))
    res = resolve(specs, gff)
    amb = dict(res.ambiguous)
    assert "DUP" in amb
    assert set(amb["DUP"]) == {"3", "4"}
    assert not any(lo.name == "DUP" for lo in res.loci), \
        "an ambiguous symbol must never be placed"


def test_invalid_symbol_is_reported(genelist_path, gff_path):
    specs = read_genelist(str(genelist_path))
    gff = GffIndex.load(str(gff_path))
    res = resolve(specs, gff)
    assert "NOPE" in res.invalid


def test_entrez_map_takes_priority(gff_path):
    from ont_bed_generator import GeneSpec
    gff = GffIndex.load(str(gff_path))
    # force PARG to target GeneID 1 (GENEA) via the external table
    res = resolve([GeneSpec("PARG", 0, 0, 0, "PARG")], gff, entrez_map={"PARG": "1"})
    assert [lo.chrom for lo in res.loci] == ["chr1"]
    assert res.loci[0].name == "GENEA"
