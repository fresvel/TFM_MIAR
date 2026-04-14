# Guía del repositorio

## Propósito

Este documento funciona como mapa de lectura de `Propuesta/`. Su objetivo es que otro lector pueda ubicar con claridad dónde reside cada responsabilidad del sistema y por dónde conviene iniciar la revisión del código.

## Vista general

- `README.md`: entrada principal al artefacto.
- `docs/`: documentación técnica.
- `src/aqrisk/`: backend Python.
- `frontend/`: cliente web Vue/Vite.
- `tests/`: validación automatizada del backend.
- `docker-compose.yml`: despliegue del stack.
- `scripts/start-services.sh`: arranque asistido con Docker.

## Backend Python

### `domain`

Contiene los modelos tipados que atraviesan el pipeline:

- `SensorDescriptor`
- `HourlyObservation`
- `ParameterSeries`
- `InputSnapshot`
- `AQIResult`
- `FuzzyResult`
- `Alert`
- `ModuleResult`

### `config`

Define `Settings`, defaults globales y carga de variables de entorno.

### `ingestion`

Incluye `OpenAQClient`, responsable de:

- consultar ubicaciones;
- consultar sensores;
- recuperar series horarias;
- adaptar la estructura remota a la representación interna.

### `processing`

Agrupa transformaciones y métricas auxiliares:

- `normalization.py`: limpieza y forma interna de series;
- `coverage.py`: cobertura global;
- `concurrence.py`: concurrencia entre contaminantes;
- `persistence.py`: persistencia temporal;
- `context.py`: capa contextual crisp.

### `aqi`

Contiene `AQICalculator` y las constantes normativas del índice.

### `fuzzy`

Contiene:

- constantes del motor;
- funciones de membresía;
- `MembershipCurveFactory`;
- `MamdaniRiskEngine`.

### `alerting`

Construye el mensaje final que acompaña la salida estructurada.

### `application`

Contiene:

- `AirQualityRiskPipeline`, orquestador principal;
- `scenarios.py`, definición de escenarios `mock`.

### `api`

Contiene:

- constantes de rutas;
- servicios de metadata, explainability y serialización;
- `server.py`, que publica los endpoints HTTP.

### `storage`

Incluye `HistoryStore`, responsable del histórico local en archivo.

### `interfaces`

Expone la CLI del prototipo mediante `aqrisk`.

## Frontend

El frontend está organizado para separar presentación, estado y configuración.

### `components`

Contiene las piezas visibles principales:

- `DashboardSection.vue`
- `TraceabilitySection.vue`
- `ExplainabilitySection.vue`
- `EvaluationSection.vue`
- `ChartPanel.vue`
- `SidebarNav.vue`
- `ExecutivePanel.vue`
- `HistoryFilters.vue`
- `LocationPicker.vue`

### `composables`

Agrupa lógica reutilizable:

- `useWorkspaceData.js`: carga de metadata, corridas, escenarios, histórico y ubicaciones;
- `useResultCharts.js`: construcción de datasets para gráficas;
- `useResultPresentation.js`: presentación derivada de resultados;
- `useHistoryFilters.js`: filtrado del histórico;
- `useLocationSearch.js`: búsqueda y selección de ubicaciones;
- `useCaptureMode.js`: soporte para captura/exportación visual.

### `config`

Incluye configuración declarativa del frontend:

- `chartOptions.js`
- `sections.js`
- `openaqStations.js`

### `services`

`api.js` concentra las llamadas HTTP al backend.

### `utils`

Contiene funciones puras para:

- lectura y apoyo de AQI;
- descarga de imágenes PNG.

## Pruebas

El estado actual de pruebas automatizadas es acotado:

- `tests/test_pipeline.py`: smoke tests y regresión básica del pipeline;
- `tests/test_api.py`: contrato HTTP básico.

No existe todavía una suite propia de frontend ni pruebas E2E.

## Orden recomendado de lectura

Para entender el sistema completo:

1. `README.md`
2. `docs/architecture.md`
3. `docs/rule_base.md`
4. `src/aqrisk/application/pipeline.py`
5. `src/aqrisk/api/server.py`
6. `frontend/src/App.vue`
7. `tests/test_pipeline.py`
8. `tests/test_api.py`
