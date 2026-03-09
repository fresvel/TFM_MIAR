# Pipeline por fases (SRL)

Este documento organiza la ejecucion SRL por fases usando los artefactos actuales.

## Fase 01 - Identificacion y screening inicial

- Entradas:
  - `articles.csv`
- Salidas:
  - `articles_screened.csv`
- Regla:
  - Clasificar por P/I/Co y decidir recuperacion.

## Fase 02 - Recuperacion de texto completo

- Entradas:
  - `articles_screened.csv` (registros a recuperar)
  - `get_pdfs.py`
- Salidas:
  - `downloads.csv`
  - `descargados/*.pdf`
- Nota:
  - El script no debe escribirse sobre archivos canonicos sin respaldo previo.

## Fase 03 - Elegibilidad full text

- Entradas:
  - `articles_full_text.csv`
  - `ExclusionReasons.md` (catalogo oficial)
  - `descargados/*.pdf`
- Salidas:
  - `articles_full_text.csv` actualizado con decision final y razon unica.

## Fase 04 - Evaluacion de calidad (Kitchenham)

- Entradas:
  - `articles_full_text.csv` (solo Include)
  - `descargados/*.pdf`
- Salidas:
  - `articles_quality_assessment.csv`
  - `qa_scores_summary.csv`
  - `qa_scores_summary.md`

## Fase 05 - Extraccion de datos

- Entradas:
  - `articles_full_text.csv` (Include)
  - `catalogo_controlado_extraccion_v1.md`
  - `descargados/*.pdf`
- Salidas:
  - `articles_data_extraction.csv`
  - `analisis_preliminar_full_text.md`

## Fase 06 - Integracion con informe y reproducibilidad

- Entradas:
  - `metodologías/*.tex`
  - `other_files/*template*`
  - `other_files/auditoria_*.md`
- Salidas:
  - Bloques metodologicos en informe
  - Paquete reproducible (Zenodo) cuando aplique

## Control transversal obligatorio

- Ejecutar antes de pasar a Analisis/Sintesis:
  - `python scripts/validar_consistencia_srl.py`
- Criterio de pase:
  - Include (full text) = filas extraccion = filas QA.

