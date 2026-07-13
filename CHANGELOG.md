# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]
### Added
- Transparent gzip (`.gz`) support for all input files (genome, genelist, GFF,
  Entrez map).

### Changed
- **Breaking:** simplified the genelist format to three columns
  `Gene | Left_extension_bp | Right_extension_bp` (dropped the Chromosome,
  Extended_region and Comment columns). The extended-region flag is now derived
  (a gene is extended iff Left or Right is non-zero); a header row is
  auto-detected. Existing six-column lists must be converted.
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

## [0.2.0] - 2026-07-12

### Added
- Structural invariant tests: merged intervals never overlap within a
  `(chromosome, strand)` group, every interval stays within `[0, chrom_size]`,
  and per-strand merging is idempotent.

### Changed
- **Breaking — genelist format** is now `Gene | Left_extension_bp |
  Right_extension_bp` with an auto-detected header. The Chromosome,
  Extended_region and Comment columns were dropped; the extended-region flag is
  now derived (a gene is extended iff Left or Right is non-zero).
- Output BEDs are sorted in canonical karyotypic order, independent of the
  genome file's line order; `read_genome` now returns chromosome sizes only.
- `GffIndex.by_geneid` renamed to `geneid_to_features`.
- (internal) Split-line variable unified to `fields` across the readers.

### Removed
- Dead internal state: `GffGene.strand` and the never-read `geneid_name` index.
