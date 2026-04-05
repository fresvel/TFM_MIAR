# Plan de capturas del frontend

## Objetivo

Definir un conjunto mínimo de capturas para documentar el prototipo web en la memoria del TFM y en presentaciones derivadas.

## Condiciones previas

- Levantar el stack con `docker compose up -d --build`.
- Confirmar que la API responde en `http://localhost:18010/health`.
- Confirmar que el frontend responde en `http://localhost:18080`.
- Ejecutar al menos una corrida `mock` y una corrida `openaq`.

## Capturas recomendadas

### 1. Vista general del dashboard

- Sección: `Dashboard`
- Entrada recomendada: escenario `urban_escalation`
- Elementos visibles:
  - bloque de control de entrada
  - resumen de la corrida actual
  - tarjetas de AQI global, categoría base, riesgo final y cobertura
  - al menos una gráfica de serie temporal y la gráfica de subíndices

Uso:
- presentar la interfaz general del sistema
- mostrar la integración entre selección de entrada y salida del artefacto

### 2. Vista de trazabilidad

- Sección: `Trazabilidad`
- Entrada recomendada: corrida con varios contaminantes soportados
- Elementos visibles:
  - ruta de decisión por capas
  - parámetros soportados y no soportados
  - reglas activadas
  - sensores disponibles

Uso:
- justificar explicabilidad estructural del artefacto
- mostrar qué información queda disponible para auditoría

### 3. Vista de explicabilidad

- Sección: `Explicabilidad`
- Entrada recomendada: escenario `moderate_multicontaminant`
- Elementos visibles:
  - distribución de reglas activadas
  - agregación y defuzzificación
  - funciones de pertenencia de AQI, concurrencia y persistencia
  - lectura explicable del episodio

Uso:
- describir el comportamiento interno del modelo difuso
- respaldar la interpretación del resultado final

### 4. Vista de evaluación e historial

- Sección: `Evaluación`
- Entrada recomendada: una corrida actual y una corrida histórica seleccionada
- Elementos visibles:
  - alerta final
  - ajuste contextual antes y después
  - filtros del historial
  - comparación con corrida histórica

Uso:
- mostrar evaluación del artefacto
- demostrar persistencia local y capacidad de comparación entre episodios

### 5. Vista con OpenAQ real

- Sección: `Dashboard` o `Evaluación`
- Entrada recomendada: `location_id=3175328`
- Elementos visibles:
  - resumen de la corrida actual con fuente `OpenAQ`
  - AQI base y riesgo final
  - serie temporal de `pm25`

Uso:
- evidenciar consumo real de la API
- distinguir entre escenarios controlados y datos observados

## Recomendaciones de captura

- Evitar capturas con demasiadas gráficas pequeñas en una sola página.
- Priorizar 4 o 5 figuras con propósito claro.
- Mantener la barra lateral visible al menos en la primera captura.
- En capturas de explicabilidad, dejar visible la terminología de capas y reglas.
- Si la memoria exige figuras separadas, exportar primero a PNG de alta resolución.

## Secuencia sugerida para el informe

1. Vista general del dashboard.
2. Arquitectura explicada por capas en la vista de trazabilidad.
3. Funcionamiento interno del modelo en la vista de explicabilidad.
4. Validación y comparación en la vista de evaluación.
