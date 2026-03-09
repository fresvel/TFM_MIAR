# Trazabilidad Informe <-> SRL

Objetivo: mantener alineados los bloques metodologicos del informe con los artefactos SRL.

## Mapa de trazabilidad

| Bloque en Informe | Archivo Informe | Fuente SRL principal | Verificacion minima |
|---|---|---|---|
| Seleccion de articulos (PRISMA) | `Informe/secciones/02_cuerpo/05_desarrollo.tex` | `articles_screened.csv`, `articles_full_text.csv`, `downloads.csv` | Conteos por fase y razones de exclusion consistentes |
| Criterios I/E | `Informe/assets/tablas/criterios_ie.tex` | `metodologías/metodologia_seleccion_estudios.tex`, `ExclusionReasons.md` | Criterios D1-D3 y transversal sin contradiccion |
| Evaluacion de calidad (Kitchenham) | `Informe/secciones/02_cuerpo/05_desarrollo.tex` | `articles_quality_assessment.csv`, `qa_scores_summary.csv`, `metodologías/metodologia_evaluacion_calidad.tex` | Escala, formula y bandas consistentes |
| Checklist de calidad (anexo) | `Informe/secciones/03_finales/03_anexos_i.tex` | `metodologías/anexo_checklist_calidad.tex` | Etiqueta `tab:anexo_checklist_calidad` resolviendo |
| Extraccion de datos | `Informe/secciones/02_cuerpo/05_desarrollo.tex` | `articles_data_extraction.csv`, `catalogo_controlado_extraccion_v1.md`, `metodologías/metodologia_extraccion_datos.tex` | 48 columnas, 19 estudios incluidos, evidencia por pagina |
| Matriz conceptual de extraccion | `Informe/assets/tablas/extracción_de_datos.tex` | `metodologías/matriz_extraccion_actualizada.tex` | Estructura y campos representativos alineados |
| Diccionario operativo (anexo) | `Informe/secciones/03_finales/03_anexos_i.tex` | `metodologías/anexo_diccionario_extraccion.tex` | Etiqueta `ane:anexo_diccionario_extraccion` resolviendo |

## Reglas operativas

- Si cambian conteos o clasificaciones en CSV, actualizar primero SRL y luego redaccion del informe.
- No introducir nuevos identificadores de estudio fuera del esquema `A###`.
- Verificar siempre que `Include` en full text = filas en extraccion = filas en QA.
