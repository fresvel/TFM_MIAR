# Propuesta técnica

Primer corte ejecutable del módulo de monitoreo de calidad del aire planteado en el TFM.

## Alcance del primer corte

- Ingesta de datos desde OpenAQ v3 por `location_id` y sensores asociados.
- Consulta horaria por sensor para construir una ventana regulatoria de análisis.
- Control básico de calidad del dato mediante cobertura reportada por OpenAQ.
- Cálculo determinista de AQI para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`.
- Evaluación de riesgo mediante un sistema difuso tipo Mamdani.
- Generación de alerta interpretable y trazable.
- Ejecución local en Python o mediante Docker.

Este corte no implementa todavía interfaz web ni microservicios independientes. La estructura del código deja separadas las responsabilidades para permitir esa evolución después.

La capa determinista del AQI sigue la tabla vigente de `AQI breakpoints` de `EPA/AQS`:

- <https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html>

## Estructura

- `docs/requirements.md`: levantamiento de requerimientos.
- `docs/architecture.md`: arquitectura inicial del prototipo.
- `docs/rule_base.md`: base de reglas y malla difusa.
- `docs/design_decisions.md`: justificación de decisiones de diseño.
- `docs/integration_checklist.md`: checklist de integración web.
- `docs/api_contract.md`: contrato HTTP inicial.
- `src/aqrisk`: código fuente del módulo.
- `tests`: pruebas de humo del pipeline.
- `frontend`: interfaz web inicial para control y explicabilidad.

## Ejecución local

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk --mode mock --pretty
```

Para usar OpenAQ:

```bash
cd Propuesta
aqrisk --mode openaq --location-id 2178 --pretty
```

El comando carga `Propuesta/.env` automáticamente si existe.

## API HTTP

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 8010
```

Endpoints iniciales:

- `GET /health`
- `GET /api/v1/metadata`
- `POST /api/v1/evaluate`

## Pruebas

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Frontend

```bash
cd Propuesta/frontend
npm install
npm run dev
```

La interfaz espera por defecto la API en `http://localhost:18010`. Puede cambiarse con `VITE_API_BASE_URL`.

## Docker

```bash
cd Propuesta
docker compose up --build
```

Tambien puedes usar el script de arranque:

```bash
cd Propuesta
bash scripts/start-services.sh --build
```

Opciones disponibles:

- `--up`: levanta servicios sin reconstruir imagenes.
- `--build`: reconstruye imagenes y luego levanta servicios.
- `--no-cache`: reconstruye sin cache y luego levanta servicios.

Puertos por defecto en contenedores:

- API: `18010`
- Frontend: `18080`

Estos puertos se controlan con:

- `AQRISK_API_PORT`
- `AQRISK_FRONTEND_PORT`
