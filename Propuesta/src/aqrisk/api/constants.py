from __future__ import annotations


HEALTH_ROUTE = "/health"
METADATA_ROUTE = "/api/v1/metadata"
SCENARIOS_ROUTE = "/api/v1/scenarios"
HISTORY_ROUTE = "/api/v1/history"
LOCATIONS_ROUTE = "/api/v1/locations"
SENSORS_ROUTE_SUFFIX = "/sensors"
EVALUATE_ROUTE = "/api/v1/evaluate"

DEFAULT_HISTORY_LIMIT = 25
DEFAULT_LOCATION_ISO = "EC"
DEFAULT_LOCATION_LIMIT = 20
DEFAULT_LOCATION_COORDINATES = "-2.15968,-79.89807"
DEFAULT_LOCATION_RADIUS = 30000

JSON_ERROR_INVALID = "JSON inválido"
JSON_ERROR_ROUTE_NOT_FOUND = "Ruta no encontrada"

MODEL_SUPPORTED_PARAMETERS = ("pm25", "pm10", "co", "no2", "o3", "so2")
MODEL_CONTEXT_PARAMETERS = ("temperature", "humidity")
MODEL_LAYERS = (
    "consolidacion_normativa",
    "variables_auxiliares",
    "inferencia_difusa_principal",
    "ajuste_contextual",
    "alertamiento_salida",
)
API_MODES = ("mock", "openaq")
