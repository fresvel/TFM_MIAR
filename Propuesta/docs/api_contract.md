# Contrato HTTP

## Propósito

La API expone el núcleo del prototipo sin duplicar lógica de negocio. El backend recibe una configuración de corrida, ejecuta el pipeline y devuelve un payload estructurado que el frontend consume directamente.

## Base de uso

- URL habitual desde navegador y pruebas manuales: `http://localhost:18010`
- puerto interno del backend dentro del contenedor: `8010`
- formato de intercambio: `application/json`
- autenticación: no implementada

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

Entrega configuración por defecto y metadatos públicos del modelo.

Campos principales:

- `modes`: modos soportados, hoy `mock` y `openaq`
- `default_config`: configuración base del backend
- `model.normative_basis`: referencia normativa usada por el módulo
- `model.supported_parameters`: contaminantes criterio soportados
- `model.context_parameters`: entradas contextuales
- `model.main_rule_count`: `54`
- `model.context_rule_count`: `9`
- `model.layers`: capas públicas del artefacto
- `model.membership_curves`: curvas de membresía para `aqi`, `persistence`, `concurrence` y `risk`

Uso principal:

- inicializar el frontend;
- documentar el contrato público del modelo;
- entregar material para paneles de explicabilidad.

### `GET /api/v1/scenarios`

Devuelve escenarios controlados para `mode=mock`.

Respuesta resumida:

```json
{
  "items": [
    {
      "scenario_id": "urban_escalation",
      "name": "Urban Escalation",
      "description": "..."
    }
  ]
}
```

Escenarios actuales:

- `urban_escalation`
- `particulate_pressure`
- `moderate_multicontaminant`
- `diffuse_overlap`

### `GET /api/v1/locations`

Consulta ubicaciones OpenAQ para selección rápida.

Parámetros admitidos:

- `iso`
- `limit`
- `coordinates`
- `radius`

Si no se envían, el backend usa valores por defecto definidos en `api/constants.py`.

### `GET /api/v1/locations/{id}/sensors`

Devuelve sensores resumidos para una ubicación OpenAQ concreta.

Uso principal:

- inspección previa de estaciones;
- trazabilidad del conjunto de sensores publicados;
- apoyo a la selección de casos reales.

### `GET /api/v1/history`

Lista corridas previas persistidas en el histórico local.

Cada elemento incluye:

- `recorded_at`
- `request`
- `summary`

El campo `summary` resume la corrida con:

- fuente;
- ubicación;
- cobertura;
- `AQI` global;
- categoría;
- contaminante dominante;
- salida difusa;
- score;
- ajustes contextuales;
- reglas activadas.

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

Respuesta estructural:

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

Semántica de los bloques:

- `snapshot`: fuente, ubicación, series, observaciones y cobertura;
- `aqi`: subíndices, `AQI` global, categoría, contaminante dominante y parámetros soportados/no soportados;
- `concurrence_score` y `persistence_score`: entradas auxiliares del motor;
- `fuzzy`: score final, etiqueta y reglas activadas;
- `context_adjustments`: reglas contextuales aplicadas o evaluadas;
- `alert`: título, mensaje y cautela;
- `explainability`: salida organizada por capas.

## Explainability

`explainability.layer_outputs` refleja la arquitectura pública del artefacto:

- `consolidacion_normativa`
- `variables_auxiliares`
- `inferencia_difusa_principal`
- `ajuste_contextual`
- `alertamiento_salida`

Este bloque está pensado para el frontend y para la inspección manual. Permite reconstruir la decisión del sistema sin acceder directamente a código Python.

## Errores

La API devuelve un payload uniforme:

```json
{
  "error": "mensaje de error"
}
```

Códigos esperados:

- `400`: entrada inválida, error controlado de ejecución o fallo de precondición;
- `404`: ruta inexistente;
- `500`: error interno no controlado.

Ejemplos habituales:

- JSON inválido;
- `location_id` no convertible a entero;
- falta de `OPENAQ_API_KEY` en `mode=openaq`;
- fallo controlado al consultar `OpenAQ`.
