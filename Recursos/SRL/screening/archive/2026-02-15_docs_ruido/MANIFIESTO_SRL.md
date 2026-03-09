# Manifiesto SRL (baseline operativo)

Fecha de baseline: 2026-02-15

## 1) Fuente unica por artefacto

- Screening inicial:
  - `articles.csv`
  - `articles_screened.csv`
- Recuperacion full text:
  - `downloads.csv`
  - `articles_full_text.csv`
- Evaluacion de calidad:
  - `articles_quality_assessment.csv`
  - `qa_scores_summary.csv`
  - `qa_scores_summary.md`
- Extraccion:
  - `articles_data_extraction.csv`
  - `catalogo_controlado_extraccion_v1.md`
- Evidencia primaria:
  - `descargados/*.pdf`
- Metodologia en formato TeX:
  - `metodologías/*.tex`
- Auditoria y paquete reproducible:
  - `other_files/auditoria_*.md`
  - `other_files/*zenodo*`
  - `other_files/*template*`
- Historial y auxiliares:
  - `archive/<fecha>_auxiliares/`

## 2) Regla de cambios

- No editar simultaneamente `articles_data_extraction.csv` y `articles_quality_assessment.csv`
  sin volver a ejecutar verificacion de consistencia.
- Cualquier ajuste de taxonomia/codificacion debe reflejarse en
  `catalogo_controlado_extraccion_v1.md`.
- Los conteos de Include/Exclude en `articles_full_text.csv` son la base oficial para
  metodologia y resultados de seleccion.

## 3) Criterio de consistencia con Informe

- Las referencias metodologicas del informe deben apuntar a etiquetas y tablas existentes.
- Las afirmaciones numericas (n de estudios, bandas de calidad, etc.) deben salir de CSV.
- Antes de avanzar a Analisis y Sintesis, ejecutar:
  - `python Recursos/SRL/screening/scripts/validar_consistencia_srl.py`
