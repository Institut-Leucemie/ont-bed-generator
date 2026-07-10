"""I/O tests: transparent gzip support across the readers."""
from __future__ import annotations

import gzip

from ont_bed_generator import GffIndex, read_genelist, read_genome


def _gzip_copy(src, dst):
    with open(src, "rb") as fh_in, gzip.open(dst, "wb") as fh_out:
        fh_out.write(fh_in.read())


def test_gzipped_gff_matches_plain(tmp_path, gff_path):
    gz = tmp_path / "mini.gff3.gz"
    _gzip_copy(gff_path, gz)
    plain = GffIndex.load(str(gff_path))
    zipped = GffIndex.load(str(gz))
    assert set(zipped.by_geneid) == set(plain.by_geneid)
    assert zipped.name_to_geneids == plain.name_to_geneids


def test_gzipped_genome_matches_plain(tmp_path, genome_path):
    gz = tmp_path / "mini.len.gz"
    _gzip_copy(genome_path, gz)
    assert read_genome(str(gz)) == read_genome(str(genome_path))


def test_read_genelist_derives_extended_flag(tmp_path):
    p = tmp_path / "gl.tsv"
    p.write_text(
        "Gene\tLeft_extension_bp\tRight_extension_bp\n"
        "PLAIN\t0\t0\n"
        "LEFTONLY\t500\t0\n"
        "BOTH\t100\t200\n"
    )
    specs = {s.symbol: s for s in read_genelist(str(p))}
    assert specs["PLAIN"].extended == 0
    assert specs["LEFTONLY"].extended == 1
    assert specs["LEFTONLY"].left == 500
    assert specs["BOTH"].extended == 1
    assert specs["BOTH"].right == 200


def test_read_genelist_without_header_and_bare_gene(tmp_path):
    p = tmp_path / "gl.tsv"
    p.write_text("MYCN\n")   # no header, single column
    specs = read_genelist(str(p))
    assert len(specs) == 1
    assert specs[0].symbol == "MYCN"
    assert (specs[0].left, specs[0].right, specs[0].extended) == (0, 0, 0)
