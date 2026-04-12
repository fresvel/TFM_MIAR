# Arquitectura del prototipo

## 1. Vista funcional

El prototipo se organiza en cinco capas funcionales:

1. adquisición y preparación de datos;
2. evaluación AQI base;
3. derivación de variables auxiliares;
4. inferencia difusa y ajuste contextual;
5. emisión de resultados y exposición por API/web.

Esta estructura coincide con la lógica explicada en la memoria y con la instrumentación real del sistema.

## 2. Vista de software

El paquete `aqrisk` queda organizado así:

- `domain`: modelos de datos y tipos base;
- `ingestion`: acceso a OpenAQ y construcción de series;
- `processing`: normalización, cobertura, persistencia, concurrencia y contexto;
- `aqi`: cálculo determinista del AQI;
- `fuzzy`: membresías, reglas y motor Mamdani;
- `alerting`: composición de la salida interpretable;
- `application`: orquestación del pipeline y escenarios;
- `api`: backend HTTP;
- `storage`: histórico local;
- `interfaces`: CLI.

La web consume la API como cliente separado y no altera el núcleo del razonamiento.

## 3. Vista de despliegue

El despliegue actual usa dos servicios:

- `aqrisk-api`
- `aqrisk-frontend`

Ambos se levantan desde `docker-compose.yml`. La persistencia actual del histórico se resuelve con almacenamiento local montado en volumen.

## 4. Decisiones de diseño

### 4.1 Arquitectura modular monoproceso

El backend se implementa como una aplicación modular monoproceso. Esta decisión reduce complejidad accidental y facilita depuración, validación y trazabilidad.

### 4.2 Separación entre núcleo, API y frontend

La lógica de dominio permanece en el núcleo Python. La API expone servicios de evaluación y consulta. El frontend se limita a control, visualización y explicabilidad.

### 4.3 AQI con base normativa explícita

El cálculo AQI sigue `EPA/AQS` y usa ventanas regulatorias diferenciadas por contaminante.

### 4.4 Inferencia difusa auditable

La lógica Mamdani se implementa con reglas y funciones de pertenencia declaradas en código, sin depender de una librería de caja negra.

### 4.5 Ajuste contextual desacoplado

La modulación contextual no recalcula el AQI. Opera sobre el riesgo derivado y mantiene separación entre capa normativa y capa interpretativa.

### 4.6 Histórico local como solución transitoria

El histórico actual permite inspección y comparación de corridas, pero no reemplaza una persistencia robusta.

### 4.7 Gestión de acceso diferida

Perfiles, roles y administración no forman parte del alcance actual del TFM.

## 5. Flujo de ejecución

1. Resolver configuración.
2. Seleccionar modo, estación y parámetros de ejecución.
3. Recuperar sensores y observaciones.
4. Estandarizar series y calcular cobertura.
5. Obtener concentraciones representativas.
6. Calcular subíndices AQI y AQI global.
7. Derivar persistencia y concurrencia.
8. Ejecutar inferencia Mamdani.
9. Aplicar ajuste contextual si existe contexto disponible.
10. Construir alerta, salida JSON e histórico local.
11. Exponer resultados por API y frontend.

## 6. Vacíos arquitectónicos aún abiertos

- falta persistencia robusta;
- faltan pruebas de API, frontend y E2E;
- falta endurecimiento para exposición pública;
- falta autenticación si se ampliara el alcance.

