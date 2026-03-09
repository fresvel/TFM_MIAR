# CODEBOOK - SLR Extraction and Quality Assessment

## Core datasets
- `articles_data_extraction.csv`
- `articles_quality_assessment.csv`
- `slr_results_consolidated.xlsx`

## Key field groups (articles_data_extraction.csv)
- Bibliographic metadata: `Article_ID`, `Title`, `Year`, `Venue`, `DOI_or_URL`.
- D1 (data/variables): `D1_*` fields.
- D2 (fuzzy approach/design): `D2_*` fields.
- D3 (platform/implementation): `D3_*` fields.
- Evaluation results: `Eval_*` fields.
- Traceability: `Evidence_D1_pages`, `Evidence_D2_pages`, `Evidence_D3_pages`, `Evidence_Eval_pages`.
- Quality linkage: `QA_Quality_band`, `QA_Score_percent`, `Sensitivity_set`.

## Key field groups (articles_quality_assessment.csv)
- Study metadata and full-text evidence references.
- Typification and instrument fields: `QA_Study_approach`, `QA_Quant_subtype`, `QA_Instrument_Version`, `QA_Scale_Allowed`.
- Item-level checklist scores: `QA_I01_*` to `QA_I30_*`.
- Consolidated outputs: raw score, percent score, quality band.

## Scale conventions
- Quality scale: `Yes`, `Partial`, `No`, `Unclear`, `N/A`.
- Score mapping: `Yes=1`, `Partial=0.5`, `Unclear=0.25`, `No=0`.
- `N/A` is excluded from denominator.

## Evidence format
- `p.X` or `p.X-p.Y`
- Multiple references separated by `; `
