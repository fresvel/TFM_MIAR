# SRL package for Zenodo

This package contains the final datasets used by the SRL methodology and synthesis.
Only final results are included.

## Folder structure

- `01_screening/articles_screened.csv`: title/abstract screening and retrieval status.
- `02_elegibilidad/articles_full_text.csv`: full-text eligibility decisions and exclusion reasons.
- `03_calidad/articles_quality_assessment.csv`: item-level quality assessment, evidence, and aggregate scores.
- `04_extraccion/articles_data_extraction.csv`: final base extraction matrix (50 columns) used as the primary source for synthesis.
- `04_extraccion/catalogo_controlado_extraccion_v1.md`: controlled coding catalog used during extraction.
- `05_synthesis_derivatives/`: derived analytical artifacts used to support synthesis, kept separate from the base extraction matrix.

## Naming note

Some folder names remain in Spanish (`elegibilidad`, `calidad`, `extraccion`) to preserve direct traceability with the report methodology and the working SRL pipeline. The package documentation is written in English, but canonical dataset paths are intentionally kept unchanged.

## Traceability with the report methodology

The methodology section of the report references these exact in-package paths:

- `01_screening/articles_screened.csv`
- `02_elegibilidad/articles_full_text.csv`
- `03_calidad/articles_quality_assessment.csv`
- `04_extraccion/articles_data_extraction.csv`
- `04_extraccion/catalogo_controlado_extraccion_v1.md`

Derived synthesis artifacts are intentionally separated under `05_synthesis_derivatives/` so the manual extraction matrix remains identifiable as the base source. The enriched dataset currently expands the base matrix from 50 to 71 columns.

## Version

- Package version: `v1`
- Intended publication target: Zenodo
