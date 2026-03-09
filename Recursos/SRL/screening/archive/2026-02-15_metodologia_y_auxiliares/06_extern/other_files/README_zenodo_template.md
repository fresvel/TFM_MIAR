# Replication Package - SLR Air Quality and Fuzzy Inference

## Description
This repository provides the core data products used in the SLR workflow:
- final data extraction matrix,
- item-level quality assessment checklist,
- consolidated review results.

## Files
- `data/articles_data_extraction.csv`: final extraction matrix used for synthesis.
- `data/articles_quality_assessment.csv`: quality checklist scores and page-level evidence.
- `data/slr_results_consolidated.xlsx`: consolidated process results.
- `docs/CODEBOOK.md`: variable dictionary and coding conventions.

## Coding conventions
- `NR`: not reported in the source study.
- `NA`: not applicable to the study/subtype.
- `Other:<text>`: value outside controlled catalog, explicitly specified.
- Evidence pages format: `p.X` or `p.X-p.Y`, multi-value with `; `.

## Reproducibility notes
This package corresponds to the final screened and included set of primary studies.

## Citation
Please cite the Zenodo record DOI associated with this package.
