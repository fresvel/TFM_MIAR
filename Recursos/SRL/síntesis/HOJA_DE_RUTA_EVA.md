 Ajuste de hoja de ruta (sin redundancia)

  1. Fase 1/5: Delimitar alcance de “desempeño transversal”.

  - Paso 1/2: Mantener como núcleo Eval_*.
  - Paso 2/2: Usar D1–D3 solo para explicar heterogeneidad del rendimiento.

  2. Fase 2/5: Tablas base de desempeño.

  - Paso 1/3: Métricas reportadas (frecuencia y familias).
  - Paso 2/3: Comparabilidad experimental (comparador, mejora, split, tamaño).
  - Paso 3/3: Trazabilidad mínima con Evidence_Eval_pages.

  3. Fase 3/5: Cruces transversales D1–D3 -> Eval (sin repetir D1/D2/D3 descriptivo).

  - Paso 1/4: D1_Data_source_type (origen de datos) vs patrón de métricas/comparador.
  - Paso 2/4: D1_Target_output_airpollution_class vs tipo de métrica (clasificación/regresión).
  - Paso 3/4: D2_Fuzzy_approach_type_norm y/o D2_Inference_purpose_norm vs comparabilidad.
  - Paso 4/4: D3_Processing_mode_norm y D3_Platform_architecture_norm vs split/mejora reportada.

  4. Fase 4/5: Redacción de resultados de desempeño.

  - Paso 1/2: Hallazgos consistentes.
  - Paso 2/2: Límites de comparabilidad (NR, splits incompletos, comparadores internos).

  5. Fase 5/5: Calidad y sensibilidad (apartado siguiente).

  - Paso 1/2: QA_Quality_band y QA_Score_percent.
  - Paso 2/2: Sensitivity_set.
  - Esto va mejor fuera del bloque de desempeño, como ya está planteado.
  
  
   Hoja de Ruta — Resultados de desempeño (D1–D3 transversal)

  Fase 1 — Alineación del bloque transversal

  - [x] Definir estructura en 3 niveles (métricas, comparabilidad, trazabilidad)
  - [x] Tener tablas base en informe (eval_metricas_frecuentes, eval_comparabilidad_configuracion,
    eval_trazabilidad_minima)
  - [ ] Incorporar explícitamente “origen de datos” como eje transversal dentro del bloque de
    comparabilidad

  Fase 2 — Normalización analítica de columnas Eval_*

  - [ ] Estandarizar taxonomía de métricas (Accuracy, RMSE, MAE, MAPE, R2, MSE y variantes Other:*)
  - [ ] Clasificar Eval_Comparator_values en categorías comparables (multi-modelo, baseline interno,
    cualitativo, NR)
  - [ ] Clasificar Eval_Improvement_reported (cuantificada, cualitativa, NR)
  - [ ] Clasificar Eval_Data_split_values (Train/Test, Train/Test+validación-CV, otro, NR)
  - [ ] Marcar completitud/NR para Eval_Dataset_size_values y Eval_Reported_values

  Fase 3 — Integración de “origen de datos” (tu pedido)

  - [ ] Integrar D1_Data_source_type en la tabla de comparabilidad o en tabla adicional específica
  - [ ] Cruce mínimo recomendado: D1_Data_source_type × Eval_Data_split_values (rigurosidad
    experimental)
  - [ ] Cruce mínimo recomendado: D1_Data_source_type × familia de métricas reportadas
  - [ ] Redactar lectura crítica: no solo frecuencia, también impacto del origen en comparabilidad

  Fase 4 — Trazabilidad y evidencia

  - [ ] Ampliar eval_trazabilidad_minima para incluir 1 campo más de contexto (recomendado:
    D1_Data_source_type)
  - [ ] Mantener Evidence_Eval_pages en todas las afirmaciones críticas
  - [ ] Asegurar consistencia artículo → métrica/reportado → comparador/esquema → evidencia

  Fase 5 — Redacción de resultados

  - [ ] Párrafo 1: métricas dominantes y heterogeneidad real
  - [ ] Párrafo 2: comparabilidad experimental (comparadores, mejora, partición, tamaño)
  - [ ] Párrafo 3: efecto de origen de datos sobre robustez y transferibilidad
  - [ ] Cierre: límites de comparabilidad y criterio metodológico para interpretar mejoras

  Fase 6 — Criterio de cierre del bloque

  - [ ] Confirmar que toda afirmación de desempeño tenga respaldo en Eval_* + Evidence_Eval_pages
  - [ ] Confirmar que el eje “origen de datos” quedó explícito y no solo implícito

