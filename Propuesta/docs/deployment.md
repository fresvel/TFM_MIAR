# Instalación y despliegue

## Propósito

Este documento explica cómo instalar, ejecutar y verificar `AQRisk` tanto en modo local como en despliegue dockerizado. La opción recomendada para ejecución reproducible es Docker, porque mantiene backend y frontend alineados con la configuración del prototipo.

## Prerrequisitos

### Ejecución local del backend

- `Python 3.12`
- `pip`

### Ejecución local del frontend

- `Node.js 20`
- `npm`

### Despliegue dockerizado

- `Docker`
- `Docker Compose`

## Variables de entorno

El proyecto usa `Propuesta/.env`. Si no existe, puede crearse a partir de `.env.example`.

Variables relevantes:

- `OPENAQ_API_KEY`: obligatoria para corridas reales
- `OPENAQ_BASE_URL`: por defecto `https://api.openaq.org/v3`
- `OPENAQ_LOCATION_ID`: ubicación inicial por defecto
- `OPENAQ_LOOKBACK_HOURS`: ventana temporal de consulta
- `OPENAQ_MIN_COVERAGE`: cobertura mínima requerida
- `AQRISK_HISTORY_PATH`: ruta del histórico local
- `AQRISK_API_PORT`: puerto expuesto del backend
- `AQRISK_FRONTEND_PORT`: puerto expuesto del frontend
- `AQRISK_SCENARIO_ID`: escenario por defecto en modo `mock`

Valores base del ejemplo actual:

- API: `18010`
- frontend: `18080`
- lookback: `24`
- cobertura mínima: `80`

## Instalación local

### Backend por CLI

```bash
cd Propuesta
python3 -m pip install -e .
```

Ejemplos:

```bash
aqrisk --mode mock --pretty
aqrisk --mode openaq --location-id 1134 --pretty
```

### API HTTP

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 18010
```

Verificación:

```bash
curl http://localhost:18010/health
```

### Frontend

```bash
cd Propuesta/frontend
npm install
npm run dev
```

En desarrollo local el frontend espera la API en `http://localhost:18010`, salvo override por `VITE_API_BASE_URL`.

## Despliegue con Docker

### Opción directa

```bash
cd Propuesta
docker compose up --build
```

### Opción asistida

```bash
cd Propuesta
bash scripts/start-services.sh --build
```

El script de arranque:

- verifica que Docker esté disponible;
- crea `.env` desde `.env.example` cuando no existe;
- comprueba que los puertos estén libres;
- construye imágenes si se solicita;
- levanta el stack en segundo plano.

## Servicios y puertos

### Backend

- servicio: `aqrisk-api`
- comando: `aqrisk-api --host 0.0.0.0 --port 8010`
- puerto interno: `8010`
- puerto expuesto por defecto: `18010`

### Frontend

- servicio: `aqrisk-frontend`
- puerto interno: `8080`
- puerto expuesto por defecto: `18080`
- variable de integración: `VITE_API_BASE_URL=http://localhost:${AQRISK_API_PORT}`

### Volúmenes

- `aqrisk_runtime_data`: histórico local del backend
- `aqrisk_frontend_node_modules`: dependencias del frontend dentro del contenedor

## Operaciones habituales

### Levantar servicios

```bash
cd Propuesta
docker compose up -d
```

### Reconstruir imágenes

```bash
cd Propuesta
docker compose up --build
```

### Reconstruir sin caché

```bash
cd Propuesta
bash scripts/start-services.sh --no-cache
```

### Detener servicios

```bash
cd Propuesta
docker compose down
```

### Ver estado

```bash
cd Propuesta
docker compose ps
```

## Verificación operativa

Checklist mínima:

1. abrir `http://localhost:18080`;
2. confirmar que el frontend puede consultar `GET /health`;
3. ejecutar una corrida `mock`;
4. revisar `Dashboard`, `Trazabilidad`, `Explicabilidad` y `Evaluación`;
5. si existe `OPENAQ_API_KEY`, probar una corrida `openaq`.

Verificación del backend:

```bash
curl http://localhost:18010/health
```

Prueba automatizada disponible:

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Problemas comunes

### `OPENAQ_API_KEY` ausente o inválida

Las corridas reales fallan de forma controlada. El modo `mock` sigue operativo.

### Puertos ocupados

Ajusta `AQRISK_API_PORT` o `AQRISK_FRONTEND_PORT` en `.env` y vuelve a levantar el stack.

### Frontend sin acceso a la API

Verifica que:

- el backend esté levantado;
- `VITE_API_BASE_URL` apunte al puerto correcto;
- `http://localhost:18010/health` responda correctamente.

### Problemas DNS dentro de Docker

Si `OpenAQ` falla con errores de resolución de nombres, revisa que el stack se haya levantado con el `docker-compose.yml` actual. La configuración ya fija DNS explícito para reducir ese problema.

### Dependencias del frontend no instaladas en local

Ejecuta:

```bash
cd Propuesta/frontend
npm install
```

### Histórico vacío o reiniciado

El histórico actual es local y depende del archivo o volumen configurado en `AQRISK_HISTORY_PATH`. Si cambia el contenedor o la ruta, la vista `Evaluación` puede iniciar sin registros previos.
