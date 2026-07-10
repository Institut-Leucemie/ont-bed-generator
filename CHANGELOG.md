# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]
### Added
- Transparent gzip (`.gz`) support for all input files (genome, genelist, GFF,
  Entrez map).

### Changed
- Output BEDs are now sorted in canonical karyotypic order (chr1..chrN, then
  X, Y, then M/MT, contigs last), organism-agnostic. The genome file's line
  order no longer affects the output; `read_genome` returns sizes only and the
  internal `rank` ordering was removed in favour of `ordering.chrom_sort_key`.

## [0.1.0] - TBD
### Added
- Generation of `targets.bed` and `merged-extended.bed`.
- Symbol resolution restricted to official HGNC symbols via the Entrez key
  (GFF `Name=`), handling pseudoautosomal regions and IG/TCR loci.
- Reporting of invalid / ambiguous symbols (`--strict`).
- Unit tests + optional `bedtools merge` parity test.
