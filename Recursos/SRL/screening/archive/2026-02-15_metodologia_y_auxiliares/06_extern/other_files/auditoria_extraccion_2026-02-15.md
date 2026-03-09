# Auditoria de Extraccion de Datos (2026-02-15)

## Alcance
- Archivo auditado: `articles_data_extraction.csv`
- Fuente de contraste: PDFs en `descargados/`
- Universo: 19 estudios incluidos en full text

## Resultado ejecutivo
- Estado general: **Aprobado con observaciones menores**
- Hallazgos criticos: **0**
- Hallazgos mayores: **0**
- Hallazgos menores: **2** (ver seccion de observaciones)

## Verificaciones realizadas

### 1) Integridad estructural
- Filas: 19
- Columnas: 48
- IDs unicos: 19
- Duplicados: 0

### 2) Consistencia con elegibilidad full text
- `articles_full_text.csv` (FT_Final_decision=Include): 19
- `articles_data_extraction.csv`: 19
- Faltantes en extraccion respecto a Include: 0
- Extras en extraccion no incluidos: 0

### 3) Completitud de campos criticos
- Campos auditados (D1/D2/D3/Eval + evidencias): completos en 19/19
- Sin celdas vacias en:
  - `D1_Pollutants_inputs`
  - `D2_Fuzzy_approach_type`
  - `D3_Platform_architecture`
  - `Eval_Metrics_reported`
  - `Evidence_D1_pages`
  - `Evidence_D2_pages`
  - `Evidence_D3_pages`
  - `Evidence_Eval_pages`

### 4) Formato y trazabilidad de evidencia
- Formato de paginas (`p.X; p.Y-p.Z`): OK en 100%
- Rangos de pagina vs total de paginas de cada PDF: OK en 100%

### 5) Cumplimiento de catalogo controlado (campos categoricos)
- Reglas validadas sobre campos categoricos nucleares D1/D2/D3/Eval/QA/Sensitivity.
- Inconsistencias detectadas inicialmente: 4
  - Token `MCU_Arduino` en `D3_Communication_and_tech` sin prefijo `Other:`.
- Accion aplicada: normalizado a `Other:MCU_Arduino`.
- Estado post-correccion: **0 inconsistencias**.

### 6) Veracidad (contraste contra texto completo)
- Se verifico presencia de evidencia textual en paginas citadas para:
  - contaminantes/variables (D1)
  - enfoque difuso (D2)
  - plataforma/contexto (D3)
  - metricas reportadas (Eval)
- Resultado: no se detectaron contradicciones factuales directas.
- La evidencia registrada soporta el contenido principal de los campos extraidos.

## Observaciones menores
1. En `A142`, el manuscrito muestra una inconsistencia interna sobre numero de reglas (aparece 576 y tambien 573 en secciones distintas). En la matriz se mantuvo `Rules=576` por coherencia con la seccion de diseno/regla principal.
2. Algunos campos de arquitectura/plataforma son categorizaciones operativas (mapeo al catalogo), no citas literales. No son incorrectos, pero son parcialmente interpretativos y conviene mantenerlos como tales en metodologia.

## Correcciones aplicadas durante la auditoria
1. Normalizacion de separadores de evidencia: `, p.X` -> `; p.X`.
2. Normalizacion de token de catalogo:
   - `MCU_Arduino` -> `Other:MCU_Arduino` en `D3_Communication_and_tech` (A135, A136, A138, A165).

## Conclusiones
- La extraccion es consistente, trazable y metodologicamente util para sintesis.
- No se encontraron errores criticos de veracidad en los 19 estudios incluidos.
- Se recomienda conservar esta version como baseline para la siguiente fase de sintesis y analisis de sensibilidad.
