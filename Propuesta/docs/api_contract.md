# Contrato HTTP inicial del prototipo

## Base

- URL local esperada: `http://localhost:8010`
- Formato de intercambio: `application/json`

## 1. `GET /health`

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "aqrisk-api"
}
```

## 2. `GET /api/v1/metadata`

Propósito:
- informar al frontend sobre modos disponibles;
- exponer configuración por defecto;
- publicar la estructura del modelo para paneles de explicabilidad.

Respuesta esperada:

```json
{
  "modes": ["mock", "openaq"],
  "default_config": {
    "mode": "mock",
    "location_id": null,
    "lookback_hours": 24,
    "min_coverage": 80.0
  },
  "model": {
    "normative_basis": "EPA/AQS AQI Breakpoints",
    "supported_parameters": ["pm25", "pm10", "co", "no2", "o3", "so2"],
    "context_parameters": ["temperature", "humidity"],
    "main_rule_count": 54,
    "context_rule_count": 9,
    "layers": [
      "consolidacion_normativa",
      "variables_auxiliares",
      "inferencia_difusa_principal",
      "ajuste_contextual",
      "alertamiento_salida"
    ],
    "membership_curves": {}
  }
}
```

## 3. `POST /api/v1/evaluate`

Propósito:
- ejecutar el módulo con una configuración seleccionada desde el frontend.

Cuerpo esperado:

```json
{
  "mode": "mock",
  "location_id": 3175328,
  "lookback_hours": 24,
  "min_coverage": 80.0
}
```

Campos:
- `mode`: `mock` u `openaq`
- `location_id`: obligatorio cuando `mode=openaq`
- `lookback_hours`: ventana de análisis
- `min_coverage`: umbral mínimo de cobertura

Respuesta esperada:

```json
{
  "snapshot": {},
  "aqi": {},
  "concurrence_score": 0,
  "persistence_score": 0,
  "fuzzy": {},
  "context_adjustments": [],
  "alert": {},
  "explainability": {}
}
```

## 4. Errores

## 5. `GET /api/v1/locations`

Propósito:
- ofrecer al frontend un catálogo inicial de ubicaciones OpenAQ para selección rápida.

Parámetros admitidos:
- `iso`
- `limit`
- `coordinates`
- `radius`

## 6. `GET /api/v1/locations/{id}/sensors`

Propósito:
- recuperar los sensores disponibles para una ubicación.

## 7. `GET /api/v1/history`

Propósito:
- listar corridas recientes registradas localmente por el backend.

## 8. `GET /api/v1/scenarios`

Propósito:
- listar escenarios de evaluación reproducibles del modo `mock`.

Uso:
- permite ejecutar casos controlados desde el frontend sin depender de una estación viva.

Respuesta esperada:

```json
{
  "error": "mensaje de error"
}
```

Código HTTP:
- `400` solicitud inválida
- `500` fallo interno del pipeline
