# Hoja de Ruta para Sintesis y Analisis de Resultados (SLR)

## Objetivo
Alinear la sintesis del estado del arte con la pregunta de investigacion principal y con las directrices D1, D2 y D3, usando evidencia trazable del dataset de extraccion.

## Fase 1: Trazabilidad metodologica
1. Definir trazabilidad narrativa: `RQ principal`, `D1`, `D2`, `D3` -> campos del dataset -> salida textual/tabla.
2. Verificar que cada afirmacion de sintesis tenga respaldo en evidencia de pagina (`Evidence_D1_pages`, `Evidence_D2_pages`, `Evidence_D3_pages`, `Evidence_Eval_pages`).

## Fase 2: Perfil del corpus
1. Construir el bloque descriptivo del corpus: volumen por fase (screening, texto completo, incluidos), distribucion temporal, tipo de estudio y contexto.
2. Establecer denominadores explicitos (`n=19` o `n` aplicable) para evitar ambiguedad interpretativa.

## Fase 3: Sintesis por directriz
1. Sintesis D1 (datos y variables): contaminantes, variables ambientales, fuentes, frecuencia y ventana temporal.
2. Sintesis D2 (enfoque difuso): tipo de FIS, rol, diseno de reglas, membresias, defuzzificacion y optimizacion.
3. Sintesis D3 (plataforma/tiempo real): arquitectura, modo de procesamiento, comunicacion, hardware y despliegue.

## Fase 4: Resultado transversal
1. Integrar resultados de desempeno (`Eval_*`): metricas dominantes, comparadores, mejoras reportadas y limites de comparabilidad.
2. Relacionar resultados de evaluacion con D1-D3 para responder la pregunta principal de investigacion.

## Fase 5: Calidad y sensibilidad
1. Incorporar calidad metodologica (`QA_Quality_band`, `QA_Score_percent`) en la interpretacion de hallazgos.
2. Realizar lectura de robustez por subgrupos (alta/media/baja calidad) y documentar sensibilidad de conclusiones.

## Fase 6: Cierre analitico
1. Identificar vacios y limitaciones recurrentes de la evidencia.
2. Derivar implicaciones de diseno para la fase de plataforma (Fase II del trabajo).
3. Redactar conclusiones del estado del arte conectadas explicitamente con la RQ principal.

## Entregables esperados
1. Seccion de estado del arte estructurada por `D1`, `D2`, `D3` y analisis transversal.
2. Tablas/figuras de apoyo con conteos, patrones y heterogeneidad.
3. Bloque de limitaciones, vacios y lineamientos para diseno e implementacion.
