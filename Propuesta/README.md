# AQRisk

Prototipo del TFM para evaluación del riesgo en calidad del aire a partir de datos abiertos, cálculo normativo de AQI e inferencia difusa auditable. El repositorio reúne tres piezas acopladas pero separadas: un backend Python con el núcleo de razonamiento, una API HTTP para exponer la evaluación y un frontend Vue para operar el sistema, revisar trazabilidad y documentar resultados.

La implementación actual no pretende ser una plataforma productiva completa. Sí resuelve el núcleo defendible del trabajo: consolidación AQI con referencia `EPA/AQS`, derivación de variables auxiliares, inferencia `Mamdani`, capa contextual explícita, alertamiento interpretable, histórico local y despliegue dockerizado.

## Qué contiene el repositorio

- `src/aqrisk/`: núcleo backend organizado por capas de dominio, adquisición, procesamiento, AQI, inferencia difusa, API, almacenamiento e interfaces.
- `frontend/`: aplicación Vue/Vite para control de ejecución, trazabilidad, explicabilidad y evaluación histórica.
- `tests/`: pruebas actuales del pipeline y del contrato HTTP.
- `docs/architecture.md`: arquitectura funcional, de software y decisiones de separación.
- `docs/requirements.md`: alcance funcional implementado, límites y criterios de validación.
- `docs/api_contract.md`: endpoints, payloads y reglas de uso de la API.
- `docs/rule_base.md`: base normativa, variables lingüísticas, reglas difusas y capa contextual.
- `docs/design_decisions.md`: justificación de las decisiones nucleares del artefacto.
- `docs/deployment.md`: manual de instalación, ejecución local y despliegue con Docker.
- `docker-compose.yml`: despliegue del stack completo.
- `scripts/start-services.sh`: arranque asistido del stack dockerizado.

## Cómo está organizado el sistema

El backend sigue una arquitectura modular monoproceso. Primero recupera y normaliza observaciones; después calcula subíndices y AQI global; luego deriva `concurrence`, `persistence` y `coverage`; a continuación ejecuta la malla `Mamdani`; finalmente aplica una capa contextual separada y genera alerta, trazabilidad e histórico.

La API no contiene lógica de negocio propia: orquesta el pipeline, serializa la salida y publica los metadatos que consume el frontend. La web actúa como cliente del backend y concentra lectura operativa, trazabilidad y exportación visual, pero no altera el razonamiento del núcleo.

## Funcionalidad disponible

- modo `mock` con escenarios controlados reproducibles;
- modo `openaq` por `location_id`;
- cálculo AQI para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`;
- derivación de `concurrence`, `persistence` y `coverage`;
- inferencia difusa principal con `54` reglas;
- capa contextual crisp con `9` reglas sobre temperatura y humedad;
- histórico local de corridas;
- API HTTP para salud, metadatos, escenarios, ubicaciones, sensores, histórico y evaluación;
- frontend para dashboard, trazabilidad, explicabilidad y evaluación.

Quedan fuera del alcance actual: autenticación, perfiles, administración, persistencia robusta y endurecimiento para exposición pública.

## Estado de organización del código

La revisión estructural de esta iteración detectó un único archivo por encima de `1000` líneas: `frontend/src/App.vue`. Ese componente se refactorizó y quedó reducido a un ensamblador de pantalla. La lógica de estado, presentación, captura y construcción de gráficas se extrajo a `composables/`, `config/` y `utils/`.

## Ejecución rápida

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

### Stack completo con Docker

```bash
cd Propuesta
docker compose up --build
```

Puertos expuestos por defecto:

- API: `http://localhost:18010`
- Frontend: `http://localhost:18080`

El detalle completo de instalación y despliegue está en [docs/deployment.md](docs/deployment.md).

## Variables de entorno principales

El proyecto admite configuración desde `Propuesta/.env`. El archivo base es `.env.example`.

Variables más relevantes:

- `OPENAQ_API_KEY`
- `OPENAQ_BASE_URL`
- `OPENAQ_LOCATION_ID`
- `OPENAQ_LOOKBACK_HOURS`
- `OPENAQ_MIN_COVERAGE`
- `AQRISK_HISTORY_PATH`
- `AQRISK_API_PORT`
- `AQRISK_FRONTEND_PORT`

## Pruebas

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Las pruebas cubren el pipeline y el contrato HTTP básico. No hay todavía pruebas de frontend ni E2E.

## Lectura recomendada

1. `README.md`
2. `docs/architecture.md`
3. `docs/rule_base.md`
4. `docs/api_contract.md`
5. `docs/deployment.md`
