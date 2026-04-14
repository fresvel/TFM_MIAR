# Instalación y despliegue

## Prerrequisitos

### Backend local

- `Python 3.12`
- `pip`

### Frontend local

- `Node.js 20`
- `npm`

### Despliegue dockerizado

- `Docker`
- `Docker Compose`

## Variables de entorno

El proyecto usa `Propuesta/.env`. Si no existe, puedes partir de `.env.example`.

Variables principales:

- `OPENAQ_API_KEY`: obligatoria para `mode=openaq`
- `OPENAQ_BASE_URL`: por defecto `https://api.openaq.org/v3`
- `OPENAQ_LOCATION_ID`: ubicación inicial por defecto
- `OPENAQ_LOOKBACK_HOURS`: ventana temporal base
- `OPENAQ_MIN_COVERAGE`: cobertura mínima base
- `AQRISK_HISTORY_PATH`: ruta del histórico local
- `AQRISK_API_PORT`: puerto expuesto del backend
- `AQRISK_FRONTEND_PORT`: puerto expuesto del frontend

## Instalación local

### Backend

```bash
cd Propuesta
python3 -m pip install -e .
```

Ejemplos:

```bash
aqrisk --mode mock --pretty
aqrisk --mode openaq --location-id 3175328 --pretty
```

### API HTTP

```bash
cd Propuesta
python3 -m pip install -e .
aqrisk-api --host 0.0.0.0 --port 18010
```

Verificación rápida:

```bash
curl http://localhost:18010/health
```

### Frontend

```bash
cd Propuesta/frontend
npm install
npm run dev
```

La aplicación espera por defecto la API en `http://localhost:18010`.

## Despliegue con Docker Compose

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

El script:

- verifica Docker;
- crea `.env` a partir de `.env.example` si hace falta;
- comprueba puertos;
- construye imágenes si se solicita;
- levanta ambos servicios en segundo plano.

## Servicios y puertos

### Backend

- servicio: `aqrisk-api`
- puerto interno: `8010`
- puerto expuesto por defecto: `18010`

### Frontend

- servicio: `aqrisk-frontend`
- puerto interno: `8080`
- puerto expuesto por defecto: `18080`

## Reconstrucción y reinicio

Reconstrucción normal:

```bash
cd Propuesta
docker compose up --build
```

Reconstrucción sin caché:

```bash
cd Propuesta
bash scripts/start-services.sh --no-cache
```

Detener servicios:

```bash
cd Propuesta
docker compose down
```

## Verificación operativa

1. Abrir `http://localhost:18080`
2. Confirmar que el frontend marca `Backend operativo`
3. Ejecutar una corrida `mock`
4. Verificar `Trazabilidad`, `Explicabilidad` y `Evaluación`
5. Si se dispone de `OPENAQ_API_KEY`, probar una corrida `openaq`

## Problemas comunes

### `OPENAQ_API_KEY` ausente

Las corridas reales fallarán de forma controlada. El modo `mock` sigue operativo.

### Puertos ocupados

Cambia `AQRISK_API_PORT` o `AQRISK_FRONTEND_PORT` en `.env`.

### Frontend sin acceso a la API

Verifica que:

- el backend esté levantado;
- `VITE_API_BASE_URL` apunte al puerto correcto;
- el servicio `aqrisk-api` esté en estado saludable.

### Dependencias del frontend no instaladas localmente

Ejecuta:

```bash
cd Propuesta/frontend
npm install
```
