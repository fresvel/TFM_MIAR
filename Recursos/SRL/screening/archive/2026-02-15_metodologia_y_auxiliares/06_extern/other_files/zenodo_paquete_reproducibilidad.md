# Paquete Zenodo y Data Availability (recomendacion)

## Recomendacion editorial
Para este trabajo conviene publicar **un unico deposito consolidado** en Zenodo con **un solo DOI principal** (replication package), en lugar de crear un DOI por archivo. Desde la perspectiva de articulo cientifico, esto mejora trazabilidad, reduce ruido de citacion y facilita revision por pares.

## Que incluir en el deposito
Incluir al menos estos tres artefactos, con nombres estables:

1. `articles_data_extraction.csv` (matriz final de extraccion)
2. `articles_quality_assessment.csv` (checklist aplicado + evidencia por item)
3. `slr_results_consolidated.xlsx` (consolidado de resultados del proceso; opcionalmente tambien en CSV)

Archivos de soporte recomendados:
- `README.md` (descripcion del contenido y flujo de uso)
- `CODEBOOK.md` (diccionario de variables/campos)
- `LICENSE` (p.ej., CC BY 4.0)
- `CITATION.cff` (metadatos de citacion)

## Estructura sugerida del deposito
```
zenodo_srl_package/
  README.md
  CODEBOOK.md
  LICENSE
  CITATION.cff
  data/
    articles_data_extraction.csv
    articles_quality_assessment.csv
    slr_results_consolidated.xlsx
  docs/
    catalogo_controlado_extraccion_v1.md
    auditoria_extraccion_2026-02-15.md
    auditoria_semantica_2026-02-15.md
```

## Texto sugerido para seccion Data Availability (ingles)
`The data supporting this study are openly available in Zenodo at https://doi.org/10.5281/zenodo.XXXXXXX. The repository contains the final data extraction matrix (articles_data_extraction.csv), the quality assessment checklist and item-level evidence (articles_quality_assessment.csv), and the consolidated review results file (slr_results_consolidated.xlsx), together with documentation files (README and CODEBOOK).`

## Texto sugerido para seccion Disponibilidad de datos (espanol)
`Los datos que respaldan este estudio están disponibles de forma abierta en Zenodo: https://doi.org/10.5281/zenodo.XXXXXXX. El repositorio incluye la matriz final de extracción de datos (articles_data_extraction.csv), el checklist de evaluación de calidad con evidencia por ítem (articles_quality_assessment.csv) y el consolidado de resultados del proceso (slr_results_consolidated.xlsx), junto con archivos de documentación (README y CODEBOOK).`

## Como citar en el manuscrito
- En metodologia (calidad/extraccion): mencionar que los instrumentos y matrices estan archivados en el paquete reproducible.
- En Data Availability: incluir solo el DOI principal del paquete.
- En anexos (si el journal lo permite): listar nombres de archivo, sin multiplicar DOIs.
