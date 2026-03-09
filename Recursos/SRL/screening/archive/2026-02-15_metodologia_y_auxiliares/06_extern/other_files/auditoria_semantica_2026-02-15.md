# Auditoria Semantica y de Veracidad (2026-02-15)

## Objetivo
Validar coherencia semantica, consistencia metodologica y veracidad de `articles_data_extraction.csv` contra evidencia de `descargados/*.pdf`.

## Cobertura
- Estudios auditados: 19/19
- Campos auditados:
  - D1/D2/D3/Eval (columnas categoricas y de valor)
  - Paginas de evidencia (`Evidence_*_pages`)
  - Alineacion con `articles_full_text.csv` (solo `Include`)

## Resultado global
- Estado: **Aprobado**
- Inconsistencias criticas: **0**
- Inconsistencias mayores: **0**
- Observaciones menores: **2**

## Verificaciones y resultado

### 1) Coherencia estructural
- 19 filas, 48 columnas, IDs unicos, sin duplicados.
- Alineacion con `articles_full_text.csv`:
  - `FT_Final_decision=Include`: 19
  - En extraccion: 19
  - Diferencias: 0

### 2) Consistencia de catalogo controlado (campos categoricos nucleares)
- Primera pasada: 4 inconsistencias de token.
- Correccion aplicada:
  - `MCU_Arduino` -> `Other:MCU_Arduino` en `D3_Communication_and_tech` para A135, A136, A138, A165.
- Segunda pasada: 0 inconsistencias.

### 3) Consistencia de evidencia
- Formato de paginas validado (`p.X` / `p.X-p.Y` con `;`): OK 100%.
- Rangos de paginas contra longitud real de cada PDF: OK 100%.

### 4) Veracidad por contraste con texto completo
- Se contrastaron columnas clave con paginas de evidencia.
- No se detectaron contradicciones factuales directas.
- Cobertura automatica por coincidencia de terminos: ~80%.
  - El ~20% restante corresponde mayormente a etiquetas de modelado (`Other:*`) o sinonimos no literales en el texto, no a errores de contenido.

## Observaciones menores
1. `A142`: el articulo reporta internamente 576 y 573 reglas en distintas secciones; se mantiene 576 por consistencia con la seccion de diseno principal.
2. Algunas etiquetas de arquitectura son de normalizacion metodologica (`Other:*`) y no citas textuales literales.

## Conclusiones
- La matriz de extraccion es consistente y verificable para sintesis.
- Las correcciones aplicadas fueron de normalizacion semantica (sin alterar hallazgos).
- La calidad actual es suficiente para pasar a fase de sintesis y analisis de sensibilidad.
