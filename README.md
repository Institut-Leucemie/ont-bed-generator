# ont-bed-generator

Generate **BED** files for **Oxford Nanopore adaptive sampling** from a gene
list and a RefSeq GFF3. Standalone reimplementation (Python standard library
only, **no runtime dependencies**) of the Galaxy workflow "Adaptative ONT BED
file generation" (which replaced BED-Craft).

Given a list of target genes and a GFF3 annotation, the tool produces:

- `targets.bed` — the raw locus of each gene (BED6);
- `merged-extended.bed` — two intervals per locus (`+` / `-` strands),
  extended, clamped to chromosome bounds, then merged per strand.

## Installation

```bash
# from source
git clone https://github.com/CHANGE-ME/ont-bed-generator.git
cd ont-bed-generator
pip install .
```

Conda development environment (includes `bedtools`, used only by the parity
test):

```bash
conda env create -f environment.yml   # or: mamba/micromamba env create -f environment.yml
conda activate ont-bed-generator
```

## Usage

```bash
ont-bed-generator \
    --genelist genelist.tsv \
    --gff annotation.genes.gff3 \
    --genome hs1.len \
    --out-targets targets.bed \
    --out-merged  merged-extended.bed
# or: python -m ont_bed_generator --genelist ... --gff ... --genome ...
```

### Inputs

1. **genelist TSV** — columns `Chromosome | Gene | Extended_region |
   Left_extension_size_pb | Right_extension_size_pb | Comment`.
   The `Chromosome` column is **ignored**: coordinates come from the GFF.
   Symbols must be **official HGNC symbols** (check them with the
   [multi-symbol checker](https://www.genenames.org/tools/multi-symbol-checker/)).
2. **GFF3** — `gene` features only, carrying `Name=` and `Dbxref=GeneID:`
   (e.g. T2T-CHM13v2.0 / hs1).
3. **genome sizes** — `chrom<TAB>size`, one line per chromosome, **in the
   desired sort order**. Used for telomere clamping and BED sort order.
   ```bash
   curl -sO https://hgdownload.soe.ucsc.edu/goldenPath/hs1/bigZips/hs1.chrom.sizes
   ```

### Symbol resolution

Official symbol → GeneID (GFF `Name=`, or external `--entrez-map`) → collect
**all** loci carrying that GeneID. The Entrez key handles pseudoautosomal
regions (one GeneID on chrX and chrY yields two loci) and IG/TCR loci. A symbol
that is not found, or that maps to several GeneIDs, is **reported** (on stderr),
never guessed. `--strict` returns a non-zero exit code if any symbol is invalid
or ambiguous.

## Development

```bash
pip install -e '.[dev]'
pytest            # unit tests (+ bedtools parity if bedtools is present)
ruff check .
mypy
```

Versioning is driven by git tags (`hatch-vcs`): a release is
`git tag vX.Y.Z && git push --tags`.

## Intentional differences from the original Galaxy workflow

- The workflow patched non-official symbols (`MKL1→MKLN1`, a bug — MKLN1 is a
  different gene; `LYL→LYL1`). Here **no patching**: such symbols are reported
  for correction at the source.
- The Galaxy output contained a missing merge (`bedtools merge` on
  genome-order-sorted input without `-g`). This tool performs the correct merge.

## License

MIT — see [LICENSE](LICENSE).
