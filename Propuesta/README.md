# Propuesta técnica

Implementación actual del prototipo del TFM para monitoreo de calidad del aire con base normativa AQI, inferencia difusa y salida trazable.

## Estado actual

El prototipo ya implementa:

- ingesta de datos reales desde `OpenAQ v3` por `location_id`;
- recuperación de series horarias por sensor;
- normalización temporal y control de cobertura;
- cálculo AQI para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2` con criterio `EPA/AQS`;
- derivación de variables auxiliares;
- inferencia difusa `Mamdani`;
- ajuste contextual;
- emisión de alerta y respuesta JSON trazable;
- API HTTP para evaluación y consulta;
- interfaz web para control, explicabilidad, escenarios e histórico local;
- despliegue con Docker Compose.

Lo que sigue fuera del alcance actual:

- autenticación;
- perfiles;
- roles;
- administración;
- persistencia robusta en base de datos;
- exposición pública endurecida.

## Referencia normativa

La capa determinista sigue la tabla vigente de `AQI breakpoints` de `EPA/AQS`:

- <https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html>

## Estructura del proyecto

- `docs/requirements.md`: requerimientos actualizados del prototipo.
- `docs/architecture.md`: arquitectura funcional, software y despliegue.
- `docs/rule_base.md`: base de reglas principal y capa contextual.
- `docs/design_decisions.md`: decisiones de diseño y justificación.
- `docs/api_contract.md`: contrato HTTP.
- `docs/integration_checklist.md`: checklist de integración web.
- `docs/ui_capture_plan.md`: plan de capturas para la memoria.
- `src/aqrisk/`: núcleo backend.
- `frontend/`: interfaz web Vue/Vite.
- `tests/`: pruebas actuales.
- `scripts/start-services.sh`: arranque del stack dockerizado.

## Ejecución local del núcleo

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk --mode mock --pretty
```

Para consultar OpenAQ:

```bash
cd Propuesta
aqrisk --mode openaq --location-id 3175328 --pretty
```

La configuración se carga desde `Propuesta/.env` si existe.

## API HTTP

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 18010
```

Endpoints actuales:

- `GET /health`
- `GET /api/v1/metadata`
- `GET /api/v1/locations`
- `GET /api/v1/locations/{id}/sensors`
- `GET /api/v1/history`
- `GET /api/v1/scenarios`
- `POST /api/v1/evaluate`

## Frontend

La interfaz web ya forma parte del prototipo. Permite:

- configurar corridas;
- seleccionar estación y escenario;
- visualizar subíndices, AQI, riesgo y alerta;
- inspeccionar trazabilidad;
- revisar reglas activadas;
- ver gráficas de explicabilidad;
- consultar histórico local.

Desarrollo local:

```bash
cd Propuesta/frontend
npm install
npm run dev
```

La API por defecto esperada es `http://localhost:18010`.

## Docker

Arranque directo:

```bash
cd Propuesta
docker compose up --build
```

O mediante script:

```bash
cd Propuesta
bash scripts/start-services.sh --build
```

Puertos por defecto:

- API: `18010`
- Frontend: `18080`

Variables asociadas:

- `AQRISK_API_PORT`
- `AQRISK_FRONTEND_PORT`

## Pruebas

Pruebas actuales:

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Cobertura actual:

- pruebas de humo del pipeline;
- falta ampliar pruebas de API, frontend y extremo a extremo.

