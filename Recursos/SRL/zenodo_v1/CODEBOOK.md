# Codebook - SRL final datasets

## 01_screening/articles_screened.csv

Purpose: screening by title/abstract and retrieval traceability.

Typical information:
- bibliographic metadata
- screening decision signals aligned with PICo
- retrieval result/status for full text

## 02_elegibilidad/articles_full_text.csv

Purpose: full-text eligibility decisions.

Typical information:
- full-text inclusion/exclusion decision
- single exclusion reason when excluded
- evidence notes for D1, D2, D3 and transversal criterion

## 03_calidad/articles_quality_assessment.csv

Purpose: quality appraisal with Kitchenham-based checklist.

Typical information:
- study approach and subtype
- QA_I01..QA_I30 item scores with page evidence
- applicable-item counts and weighted aggregate score
- quality band and profile percentages

## 04_extraccion/articles_data_extraction.csv

Purpose: final extraction matrix used for synthesis.

Main groups:
- metadata
- D1 data/variables
- D2 fuzzy approach
- D3 platform and real-time operation
- evaluation results
- synthesis traceability and quality linkage

Current size:
- 19 rows
- 50 columns

## 04_extraccion/catalogo_controlado_extraccion_v1.md

Purpose: controlled vocabulary and normalization rules for extraction coding.

## 05_synthesis_derivatives/01_enriched_dataset/articles_data_extraction_enriched.csv

Purpose: enriched dataset used for synthesis, created from the base extraction matrix plus derived columns.

Derived groups currently included:
- D1 support fields for comparable output classes
- D2 normalized columns and synthesis notes
- D3 normalized columns and synthesis notes
- evaluation normalization fields for comparable units, metric families and protocol

Current size:
- 19 rows
- 71 columns

## 05_synthesis_derivatives/02_normalization/d2/*.csv

Purpose: audit trail for D2 normalization.

Typical information:
- pre-normalization counts
- post-normalization counts
- mapping tables
- variant notes by article

## 05_synthesis_derivatives/02_normalization/d3/*.csv

Purpose: audit trail for D3 normalization.

Typical information:
- pre-normalization counts
- post-normalization counts
- mapping tables
- variant notes by article
