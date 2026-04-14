# AQRisk

## Presentación del artefacto

`AQRisk` es el artefacto implementado del Trabajo Fin de Máster. Su objetivo es evaluar episodios de calidad del aire a partir de datos abiertos o escenarios controlados, consolidar un estado base mediante `AQI` y complementar esa lectura con una capa de inferencia difusa auditable y un ajuste contextual explícito.

El repositorio `Propuesta/` constituye, por tanto, el anexo técnico de implementación del TFM. Reúne el código fuente del backend, la API HTTP, el frontend web, las pruebas disponibles y la documentación necesaria para comprender la arquitectura del sistema, ejecutar el prototipo y revisar sus decisiones de diseño.

## Alcance del sistema

El artefacto implementa las siguientes capacidades:

1. adquisición de observaciones desde `OpenAQ` o construcción de escenarios reproducibles en modo `mock`;
2. normalización de series y cálculo de cobertura efectiva;
3. cálculo de subíndices y `AQI` global con base normativa `EPA/AQS`;
4. derivación de variables auxiliares `concurrence` y `persistence`;
5. ejecución de una malla `Mamdani` de `54` reglas;
6. aplicación de una capa contextual crisp de `9` reglas sobre temperatura y humedad;
7. construcción de alerta, trazabilidad, explicabilidad e histórico local.

El sistema actual resuelve el núcleo metodológico defendible del trabajo. No constituye todavía una plataforma multiusuario ni una solución endurecida para exposición pública.

## Estructura general del repositorio

El repositorio se organiza en cinco bloques principales:

- `src/aqrisk/`: backend Python estructurado por capas de dominio, adquisición, procesamiento, cálculo AQI, inferencia difusa, API, persistencia e interfaces.
- `frontend/`: cliente web Vue/Vite para control de ejecución, trazabilidad, explicabilidad y evaluación histórica.
- `tests/`: validación automatizada del pipeline y del contrato HTTP.
- `docs/`: documentación técnica del artefacto.
- `docker-compose.yml`: definición del despliegue del stack completo.

La estructura interna del backend conserva la organización citada en el informe:

- `domain`
- `ingestion`
- `processing`
- `aqi`
- `fuzzy`
- `alerting`
- `application`
- `api`
- `storage`
- `interfaces`

Una descripción más detallada del backend y del frontend está en [docs/repository_guide.md](docs/repository_guide.md).

## Arquitectura funcional

El sistema se compone de tres subsistemas:

- un backend de evaluación que concentra la lógica normativa, difusa y contextual;
- una API HTTP que expone el resultado y los metadatos públicos del modelo;
- un frontend web que actúa como cliente del backend y organiza la lectura operativa del artefacto.

El flujo de evaluación sigue esta secuencia:

1. resolver configuración y modo de ejecución;
2. recuperar o sintetizar observaciones;
3. normalizar series y calcular cobertura;
4. calcular subíndices y `AQI` global;
5. derivar `concurrence` y `persistence`;
6. ejecutar la inferencia difusa principal;
7. aplicar la capa contextual cuando existen datos válidos;
8. serializar la salida, registrar el histórico y exponer la evaluación por CLI, API y frontend.

Esta arquitectura mantiene una separación explícita entre la capa normativa y la capa difusa. El frontend no recalcula resultados: consume el contrato público del backend y organiza su interpretación.

## Modos de operación

### Modo `mock`

El modo `mock` permite ejecutar escenarios reproducibles y controlados. Su función es documentar comportamientos concretos del sistema, como la activación de varias reglas o el escalado contextual, incluso cuando esos casos no aparecen con facilidad en una estación real.

Escenarios actualmente disponibles:

- `urban_escalation`
- `particulate_pressure`
- `moderate_multicontaminant`
- `diffuse_overlap`

### Modo `openaq`

El modo `openaq` consulta una estación real mediante `location_id`, recupera sensores y series horarias, y ejecuta el mismo pipeline sobre datos abiertos. Este modo requiere `OPENAQ_API_KEY`.

## Documentación técnica disponible

La documentación incluida en `docs/` se organiza por finalidad:

1. [docs/repository_guide.md](docs/repository_guide.md): mapa del repositorio, del backend y del frontend.
2. [docs/architecture.md](docs/architecture.md): arquitectura, flujo de ejecución y límites técnicos.
3. [docs/rule_base.md](docs/rule_base.md): base normativa, variables auxiliares, reglas difusas y capa contextual.
4. [docs/api_contract.md](docs/api_contract.md): endpoints, payloads y errores.
5. [docs/deployment.md](docs/deployment.md): instalación local, despliegue dockerizado y resolución de problemas.
6. [docs/requirements.md](docs/requirements.md): alcance implementado y criterios de validación.
7. [docs/design_decisions.md](docs/design_decisions.md): justificación metodológica de las decisiones principales.

## Ejecución del artefacto

### Despliegue recomendado

La forma recomendada de ejecución es el despliegue dockerizado:

```bash
cd Propuesta
docker compose up --build
```

Puertos expuestos por defecto:

- API: `http://localhost:18010`
- frontend: `http://localhost:18080`

### Ejecución local

Backend por CLI:

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk --mode mock --pretty
```

API HTTP:

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 18010
```

Frontend en desarrollo:

```bash
cd Propuesta/frontend
npm install
npm run dev
```

Las instrucciones completas de instalación, variables de entorno, verificación operativa y resolución de problemas están en [docs/deployment.md](docs/deployment.md).

## Configuración

La configuración se carga desde `Propuesta/.env`. Si el archivo no existe, puede crearse a partir de `.env.example`.

Variables principales:

- `OPENAQ_API_KEY`
- `OPENAQ_BASE_URL`
- `OPENAQ_LOCATION_ID`
- `OPENAQ_LOOKBACK_HOURS`
- `OPENAQ_MIN_COVERAGE`
- `AQRISK_HISTORY_PATH`
- `AQRISK_API_PORT`
- `AQRISK_FRONTEND_PORT`
- `AQRISK_SCENARIO_ID`

## Validación disponible

La validación automatizada actual cubre:

- ejecución de extremo a extremo del pipeline en `mock`;
- fallo controlado de `mode=openaq` cuando falta `OPENAQ_API_KEY`;
- endpoints básicos del backend;
- persistencia y consulta del histórico local;
- casos con múltiples reglas activadas, en particular `diffuse_overlap`.

Comando de ejecución de la suite:

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Estado actual de cobertura:

- backend: pruebas de pipeline y contrato HTTP;
- frontend: validación manual;
- E2E: no implementadas.

## Límites actuales

El alcance actual deja fuera:

- autenticación y control de acceso;
- persistencia robusta en `SQLite` o `PostgreSQL`;
- endurecimiento para exposición pública;
- pruebas E2E;
- operación multiusuario.

Estas restricciones corresponden al alcance fijado para el TFM. La prioridad del artefacto es demostrar razonamiento trazable, defendible y técnicamente coherente.
