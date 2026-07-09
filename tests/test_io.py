"""I/O tests: transparent gzip support across the readers."""
from __future__ import annotations

import gzip

from ont_bed_generator import GffIndex, read_genome


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
