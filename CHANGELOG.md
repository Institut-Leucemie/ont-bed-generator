# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [0.4.1] - 2026-10-01

Documentation and maintenance release. No change to the package code or CLI.

### Changed
- README: installation from PyPI (`pip install ont-bed-generator`) is now the
  documented default; installation from source is kept as an alternative.
- README: the release procedure is described as it actually runs — an annotated
  tag publishes to TestPyPI, a GitHub Release on that tag publishes to PyPI.
- Release workflow: GitHub actions moved to their Node.js 24 versions
  (`checkout@v6`, `setup-python@v6`, `upload-artifact@v6`,
  `download-artifact@v7`), removing the Node.js 20 deprecation warnings.

### Fixed
- Leftover `CHANGE-ME` placeholder in the repository URL of `README.md` and
  `CITATION.cff`, now `Institut-Leucemie`.
- Changelog: versions listed newest first; 0.1.0 dated; the gzip entry moved
  from `[Unreleased]` to 0.1.0, where it shipped; the other `[Unreleased]`
  entries removed as duplicates of 0.2.0.

## [0.4.0] - 2026-07-14

### Added
- **Automated PyPI publishing workflow** (`.github/workflows/release.yml`).

## [0.3.0] - 2026-07-13

### Added
- **Annotation dataset build pipeline** (`annotation/`). A scripted, reproducible
  chain (`build_gene_gff.sh`) that derives a gene-feature-only, `chr`-named GFF3
  for T2T-CHM13v2.0 from the official NCBI RefSeq release (RS_2025_08): it keeps
  only `gene` features, renames RefSeq accessions to `chr` names via the
  assembly report, and restores the pseudoautosomal chrX copy of *P2RY8*
  (absent from the NCBI build) from the curated `NM_178129.5` coordinates under
  the shared `GeneID:286530`, so *P2RY8* resolves on both chrX and chrY like
  *CRLF2*. The built asset is archived on Zenodo
  (DOI [10.5281/zenodo.21341240](https://doi.org/10.5281/zenodo.21341240)); the
  pipeline and its documentation live in `annotation/`. No change to the package
  code or CLI.

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

## [0.1.0] - 2026-07-09

### Added
- Generation of `targets.bed` and `merged-extended.bed`.
- Symbol resolution restricted to official HGNC symbols via the Entrez key
  (GFF `Name=`), handling pseudoautosomal regions and IG/TCR loci.
- Reporting of invalid / ambiguous symbols (`--strict`).
- Unit tests + optional `bedtools merge` parity test.
- Transparent gzip (`.gz`) support for all input files (genome, genelist, GFF,
  Entrez map).
