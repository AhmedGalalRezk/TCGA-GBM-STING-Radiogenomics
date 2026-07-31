# TCGA-GBM STING Radiogenomics

Code accompanying the radiogenomic study:

**MRI Radiomic Correlates of STING Transcriptional Activity in Glioblastoma**

This repository contains the analysis code used to investigate associations between MRI radiomic phenotypes and predefined STING-related transcriptional programs in glioblastoma.

## Study overview

Preoperative multiparametric MRI from the BraTS–TCGA-GBM imaging resource was integrated with matched TCGA transcriptomic data.

Radiomic features were extracted from:

- enhancing tumor
- nonenhancing tumor
- tumor core
- whole tumor

across:

- T1-weighted MRI
- contrast-enhanced T1-weighted MRI
- T2-weighted MRI
- FLAIR MRI

The radiomic representation was constructed and reduced without reference to molecular outcomes before testing associations with STING transcriptional programs.

## Repository structure

```text
notebooks/
├── 02_Load_TCGA.ipynb
├── 03_TCGA_TCIA_Feasibility.ipynb
└── 05_TCGA_STING_Imaging_Discovery.ipynb

scripts/
└── 01_download_tcga_gbm_expression.py
