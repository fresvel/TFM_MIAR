# Contrato HTTP

## Base de uso

- URL local esperada desde navegador y pruebas manuales: `http://localhost:18010`
- puerto interno del backend dentro del contenedor: `8010`
- formato de intercambio: `application/json`

La API es intencionalmente pequeña. Su función es exponer el núcleo del prototipo sin reimplementar lógica de negocio en la capa HTTP.

## Endpoints

### `GET /health`

Verifica disponibilidad del backend.

Respuesta:

```json
{
  "status": "ok",
  "service": "aqrisk-api"
}
```

### `GET /api/v1/metadata`

Entrega la configuración por defecto y la estructura pública del modelo para consumo del frontend.

Respuesta resumida:

```json
{
  "modes": ["mock", "openaq"],
  "default_config": {
    "mode": "mock",
    "location_id": null,
    "lookback_hours": 24,
    "min_coverage": 80,
    "scenario_id": "urban_escalation"
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
    ]
  }
}
```

### `GET /api/v1/locations`

Consulta un conjunto de ubicaciones OpenAQ para selección rápida en el frontend.

Parámetros admitidos:

- `iso`
- `limit`
- `coordinates`
- `radius`

### `GET /api/v1/locations/{id}/sensors`

Devuelve sensores resumidos para una ubicación concreta.

### `GET /api/v1/scenarios`

Devuelve los escenarios controlados disponibles en modo `mock`.

### `GET /api/v1/history`

Lista corridas persistidas en el histórico local.

### `POST /api/v1/evaluate`

Ejecuta una corrida del prototipo.

Cuerpo esperado:

```json
{
  "mode": "mock",
  "location_id": null,
  "lookback_hours": 24,
  "min_coverage": 80,
  "scenario_id": "diffuse_overlap"
}
```

Reglas de uso:

- `mode` debe ser `mock` u `openaq`;
- `location_id` es obligatorio cuando `mode=openaq`;
- `scenario_id` se usa en modo `mock`;
- `lookback_hours` y `min_coverage` modulan la evaluación.

Respuesta resumida:

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

## Errores

La API devuelve un payload uniforme de error:

```json
{
  "error": "mensaje de error"
}
```

Códigos esperados:

- `400`: solicitud inválida o error controlado de entrada;
- `404`: ruta inexistente;
- `500`: error interno no controlado.
