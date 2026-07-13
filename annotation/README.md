# T2T-CHM13v2.0 gene annotation asset for ont-bed-generator

`T2T-CHM13v2.0_genes.chr.gff3.gz` — a **gene-feature-only**, **`chr`-named** GFF3
derived from the official NCBI RefSeq annotation of T2T-CHM13v2.0, with one
documented addition (the chrX pseudoautosomal copy of *P2RY8*).

It is the annotation input for `ont-bed-generator --gff`. Everything below is
reproducible with `build_gene_gff.sh`; nothing is hand-edited except the single,
sourced line described in step 3.

> **The pre-built asset is archived on Zenodo:**
> [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21341240.svg)](https://doi.org/10.5281/zenodo.21341240)
> Download it there, or rebuild it byte-for-byte with `build_gene_gff.sh`.

## Source

| | |
|---|---|
| Assembly | T2T-CHM13v2.0 (`GCF_009914755.1`) |
| Annotation release | NCBI RefSeq `RS_2025_08` |
| GFF | `.../GCF_009914755.1_T2T-CHM13v2.0_genomic.gff.gz` |
| Assembly report | `.../GCF_009914755.1_T2T-CHM13v2.0_assembly_report.txt` |

Base URL: `https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/914/755/GCF_009914755.1_T2T-CHM13v2.0`

## Production chain (`build_gene_gff.sh`)

1. **Contig map.** Build a `RefSeq-accession -> chr` table from the official
   `assembly_report.txt` (column *RefSeq-Accn* -> column *UCSC-style-name*). No
   hard-coded list: the mapping is read from NCBI's own file.
2. **Filter + rename.** Keep only `gene` features (column 3 == `gene`; the only
   thing ont-bed-generator reads) and rename column 1 from the RefSeq accession
   to the `chr` name using the map. Comment/header lines are dropped. This turns
   the ~78 MB full annotation into a ~2 MB gene-only file (41 561 genes).
3. **PAR patch — one added line, fully sourced.** The NCBI `genomic.gff` build
   annotates *P2RY8* only on chrY, although *P2RY8* is a **PAR1 gene** and is
   therefore present on both sex chromosomes (its neighbour *CRLF2*, also PAR1,
   *is* annotated on both by NCBI). We add the missing chrX copy:

   ```
   chrX  NCBI_RefSeq_curated_NM_178129.5_PAR1  gene  1304499  1338509  .  -  .  \
     ID=gene-P2RY8-chrX-PAR1;Dbxref=GeneID:286530;Name=P2RY8;gene_biotype=protein_coding
   ```

   - **Coordinates are not invented.** They are the alignment of NCBI's curated
     transcript `NM_178129.5` to chrX of hs1, as distributed by UCSC
     (`chrX:1304499-1338509`). Confirmed against HGNC (symbol `P2RY8` <-> `ENSG`
     <-> Entrez `286530`) and against the PAR1 gene lists.
   - **Same `GeneID:286530` as the chrY copy**, so ont-bed-generator groups both
     loci under one gene and resolves *P2RY8* to **both** chrX and chrY (it is
     *not* flagged ambiguous — same mechanism as *CRLF2*).
   - The `source` column records the provenance so the line is auditable in-file.

4. **Compress.** `gzip` the result. Feature order is irrelevant —
   ont-bed-generator sorts karyotypically itself.

## Get the asset

Either download the archived build from Zenodo
([10.5281/zenodo.21341240](https://doi.org/10.5281/zenodo.21341240)), or
regenerate it:

```bash
bash build_gene_gff.sh          # -> T2T-CHM13v2.0_genes.chr.gff3.gz
```

Both routes yield the same file for a given NCBI release.

## Verification (performed on this asset)

- 41 562 lines, **all** `gene` features (0 non-gene).
- `P2RY8` present on chrX (1304499-1338509) **and** chrY (1325951-1401516).
- `ont-bed-generator` resolves both `P2RY8` and `CRLF2` to two loci each, with
  **no** invalid and **no** ambiguous symbols.

## Scope & limitations

- Only *P2RY8* is patched. *CRLF2* needs no patch (NCBI annotates it on both X
  and Y natively). No other PAR1 gene in the target panels required a chrX/chrY
  copy; audit the PAR1 gene list against this file if your panel adds one.
- PAR-gene annotation is **inconsistent across all sources** (NCBI, UCSC,
  Ensembl each differ and each is incomplete for PAR1). This asset takes the
  NCBI annotation as the traceable base and adds the single, biologically
  required, NCBI-sourced chrX *P2RY8* copy — rather than switching to a source
  with its own, different PAR gaps.
- Tied to NCBI release `RS_2025_08`. Regenerate (and deposit a new Zenodo
  version) when NCBI publishes a new annotation release — ideally after the
  upstream *P2RY8* chrX omission is fixed, at which point step 3 becomes
  unnecessary.

## Citation

If you use this asset, please cite the Zenodo record:
**DOI [10.5281/zenodo.21341240](https://doi.org/10.5281/zenodo.21341240)**.
It derives from the NCBI RefSeq annotation of T2T-CHM13v2.0 (`GCF_009914755.1`,
release RS_2025_08); please also credit NCBI RefSeq as the primary source.
