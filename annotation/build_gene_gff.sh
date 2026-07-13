#!/usr/bin/env bash
# Produce the gene-only, chr-named, PAR-patched GFF3 asset consumed by
# ont-bed-generator, from the official NCBI RefSeq T2T-CHM13v2.0 annotation.
set -euo pipefail

BASE="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/914/755/GCF_009914755.1_T2T-CHM13v2.0"
GFF_URL="$BASE/GCF_009914755.1_T2T-CHM13v2.0_genomic.gff.gz"
REPORT_URL="$BASE/GCF_009914755.1_T2T-CHM13v2.0_assembly_report.txt"
OUT="T2T-CHM13v2.0_genes.chr.gff3.gz"

# 1) accession -> chr map, from the official assembly report
curl -s "$REPORT_URL" | tr -d '\r' \
  | awk -F'\t' '!/^#/ && $7!="na"{print $7"\t"$10}' > map.tsv

# 2) keep only 'gene' features + rename column 1 (accession -> chr); drop comments
curl -s "$GFF_URL" | zcat \
  | awk -F'\t' -v OFS='\t' '
      NR==FNR { m[$1]=$2; next }
      /^#/    { next }
      $3=="gene" { if ($1 in m) $1=m[$1]; print }
    ' map.tsv - > genes.chr.gff3

# 3) append the chrX PAR1 copy of P2RY8 (absent from the NCBI annotation build).
#    Coordinates = NCBI curated transcript NM_178129.5 aligned to chrX (hs1),
#    same GeneID:286530 as the chrY copy -> ont-bed resolves both loci, not ambiguous.
STRAND=$(awk -F'\t' 'index($9,"Name=P2RY8;"){print $7; exit}' genes.chr.gff3)
printf 'chrX\tNCBI_RefSeq_curated_NM_178129.5_PAR1\tgene\t1304499\t1338509\t.\t%s\t.\tID=gene-P2RY8-chrX-PAR1;Dbxref=GeneID:286530;Name=P2RY8;gene_biotype=protein_coding\n' "$STRAND" >> genes.chr.gff3

# 4) compress (order is irrelevant; ont-bed-generator sorts karyotypically itself)
gzip -c genes.chr.gff3 > "$OUT"
echo "written: $OUT"
