# AQRisk

`AQRisk` es el artefacto implementado del TFM. El sistema evalúa episodios de calidad del aire a partir de datos abiertos o escenarios controlados, consolida un estado base mediante `AQI`, deriva variables auxiliares y aplica una capa de inferencia difusa auditable con ajuste contextual explícito.

El repositorio `Propuesta/` reúne tres subsistemas:

- un backend Python con el núcleo de evaluación;
- una API HTTP que expone el resultado y los metadatos del modelo;
- un frontend Vue/Vite para operar el prototipo, revisar trazabilidad y apoyar la documentación de resultados.

La solución actual no corresponde a una plataforma productiva completa. Sí cubre el núcleo defendible del TFM: consolidación normativa, explicabilidad operativa, histórico local, despliegue dockerizado e interfaz web para inspección del razonamiento del artefacto.

## Capacidades implementadas

El flujo completo del sistema sigue estas etapas:

1. recuperar o sintetizar observaciones;
2. normalizar series y calcular cobertura;
3. obtener subíndices y `AQI` global con base `EPA/AQS`;
4. derivar `concurrence` y `persistence`;
5. ejecutar una malla `Mamdani` de `54` reglas;
6. aplicar una capa contextual crisp de `9` reglas sobre temperatura y humedad;
7. construir alerta, trazabilidad, explicabilidad e histórico local.

El resultado es una evaluación interpretable por capas. El frontend no recalcula nada: consume la API y organiza la lectura del estado base, la inferencia principal, el ajuste contextual y la comparación con corridas previas.

## Mapa del repositorio

### Backend

- `src/aqrisk/domain`: modelos tipados y estructura de resultados.
- `src/aqrisk/ingestion`: cliente `OpenAQ`, ubicaciones, sensores y series.
- `src/aqrisk/processing`: normalización, cobertura, persistencia, concurrencia y capa contextual.
- `src/aqrisk/aqi`: cálculo normativo del índice con referencia `EPA/AQS`.
- `src/aqrisk/fuzzy`: funciones de pertenencia, base de reglas y motor `Mamdani`.
- `src/aqrisk/alerting`: composición de la salida operativa final.
- `src/aqrisk/application`: pipeline principal y escenarios `mock`.
- `src/aqrisk/api`: endpoints HTTP, serialización y metadatos.
- `src/aqrisk/storage`: histórico local en archivo.
- `src/aqrisk/interfaces`: CLI.

### Frontend

- `frontend/src/components`: secciones visuales y paneles reutilizables.
- `frontend/src/composables`: estado, carga de datos, filtros y derivaciones reactivas.
- `frontend/src/config`: configuración de vistas, gráficos y estaciones OpenAQ sugeridas.
- `frontend/src/services`: cliente HTTP hacia la API.
- `frontend/src/utils`: utilidades puras y descarga de PNG.

### Soporte

- `tests`: pruebas del pipeline y del contrato HTTP.
- `docs`: documentación técnica del artefacto.
- `docker-compose.yml`: despliegue del stack completo.
- `scripts/start-services.sh`: arranque asistido con Docker.

Un mapa más descriptivo del backend y del frontend está en [docs/repository_guide.md](docs/repository_guide.md).

## Documentación disponible

La documentación se organiza por responsabilidad:

1. [README.md](README.md): guía maestra de entrada.
2. [docs/repository_guide.md](docs/repository_guide.md): mapa del repositorio, backend y frontend.
3. [docs/architecture.md](docs/architecture.md): arquitectura, flujo y límites técnicos.
4. [docs/rule_base.md](docs/rule_base.md): base normativa, variables auxiliares, malla difusa y capa contextual.
5. [docs/api_contract.md](docs/api_contract.md): endpoints, payloads y errores.
6. [docs/deployment.md](docs/deployment.md): instalación local, Docker y troubleshooting.
7. [docs/requirements.md](docs/requirements.md): alcance implementado y criterios de validación.
8. [docs/design_decisions.md](docs/design_decisions.md): justificación metodológica de las decisiones principales.

## Modos de ejecución

### `mock`

Usa escenarios controlados reproducibles para demostrar comportamiento del artefacto, activar reglas concretas y documentar casos que no siempre aparecen en datos reales.

Escenarios disponibles:

- `urban_escalation`
- `particulate_pressure`
- `moderate_multicontaminant`
- `diffuse_overlap`

### `openaq`

Consulta una estación real mediante `location_id`, recupera sensores y series horarias, y ejecuta el mismo pipeline sobre datos abiertos. Este modo requiere `OPENAQ_API_KEY`.

## Ejecución

### Opción recomendada: Docker

```bash
cd Propuesta
docker compose up --build
```

Puertos por defecto:

- API: `http://localhost:18010`
- Frontend: `http://localhost:18080`

### Backend por CLI

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk --mode mock --pretty
```

### API HTTP

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 18010
```

### Frontend en desarrollo

```bash
cd Propuesta/frontend
npm install
npm run dev
```

El detalle completo de configuración, arranque y verificación está en [docs/deployment.md](docs/deployment.md).

## Variables de entorno

El sistema carga configuración desde `Propuesta/.env`. Si el archivo no existe, puede crearse a partir de `.env.example`.

Variables principales:

- `OPENAQ_API_KEY`
- `OPENAQ_BASE_URL`
- `OPENAQ_LOCATION_ID`
- `OPENAQ_LOOKBACK_HOURS`
- `OPENAQ_MIN_COVERAGE`
- `AQRISK_HISTORY_PATH`
- `AQRISK_API_PORT`
- `AQRISK_FRONTEND_PORT`
- `AQRISK_SCENARIO_ID` como override opcional del escenario por defecto

## Validación actual

La validación automatizada disponible cubre:

- ejecución completa del pipeline en `mock`;
- fallo controlado de `mode=openaq` cuando falta `OPENAQ_API_KEY`;
- endpoints básicos del backend;
- persistencia y consulta del histórico local;
- explicación de reglas múltiples con `diffuse_overlap`.

La suite actual se ejecuta así:

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Estado actual de cobertura:

- backend: pruebas de pipeline y contrato HTTP;
- frontend: verificación manual, sin suite automatizada propia;
- E2E: no implementadas todavía.

## Estado actual y límites

El prototipo implementa el núcleo defendible del TFM, pero mantiene límites claros:

- no hay autenticación ni perfiles;
- el histórico sigue siendo local y basado en archivo;
- no existe persistencia robusta en `SQLite` o `PostgreSQL`;
- no hay endurecimiento para exposición pública;
- no hay pruebas E2E ni endurecimiento de frontend.

Estas restricciones responden al alcance definido para el artefacto. La prioridad es demostrar razonamiento trazable y defendible, no resolver todavía una plataforma multiusuario completa.
