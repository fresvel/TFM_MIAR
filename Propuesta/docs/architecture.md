# Arquitectura del prototipo

## Propósito arquitectónico

`AQRisk` se construyó como un prototipo modular orientado a tres propiedades: `auditabilidad`, `explicabilidad` y `despliegue controlado`. La arquitectura evita distribuir prematuramente el sistema y concentra el valor en un núcleo de evaluación bien separado del transporte HTTP y de la interfaz web.

## Vista general

El sistema tiene tres subsistemas principales:

- **backend de evaluación**: resuelve adquisición, normalización, cálculo AQI, variables auxiliares, inferencia difusa, ajuste contextual y alertamiento;
- **API HTTP**: expone el backend como servicio JSON y entrega metadatos que el frontend necesita para explicar el modelo;
- **frontend web**: actúa como cliente del backend y organiza la lectura de resultados en `Dashboard`, `Trazabilidad`, `Explicabilidad` y `Evaluación`.

La persistencia actual es deliberadamente simple: un histórico local en archivo para comparar corridas previas.

## Arquitectura del backend

El paquete `src/aqrisk/` conserva la estructura citada en el informe:

- `domain`: modelos tipados como `InputSnapshot`, `AQIResult`, `FuzzyResult`, `Alert` y `ModuleResult`.
- `ingestion`: cliente `OpenAQ` y funciones de recuperación de ubicaciones, sensores y series horarias.
- `processing`: normalización, cobertura, persistencia, concurrencia y capa contextual.
- `aqi`: cálculo determinista del índice a partir de breakpoints `EPA/AQS`.
- `fuzzy`: funciones de pertenencia, constantes del motor y `MamdaniRiskEngine`.
- `alerting`: composición del mensaje operativo final.
- `application`: `AirQualityRiskPipeline` y escenarios `mock`.
- `api`: servidor HTTP, mapeo de settings, serialización, metadata y explainability.
- `storage`: persistencia del histórico local.
- `interfaces`: CLI.

La separación es intencional. El núcleo normativo no vive en la API ni en el frontend, y la capa contextual no se mezcla con la malla difusa principal.

## Flujo de ejecución

La evaluación completa sigue once pasos:

1. resolver configuración desde entorno y parámetros de entrada;
2. seleccionar `mode=mock` o `mode=openaq`;
3. recuperar observaciones;
4. normalizar series y calcular cobertura;
5. obtener concentraciones representativas por contaminante;
6. calcular subíndices y `AQI` global;
7. derivar `concurrence` y `persistence`;
8. ejecutar la malla `Mamdani`;
9. aplicar la capa contextual crisp cuando hay temperatura y humedad válidas;
10. construir alerta e histórico local;
11. exponer el resultado por CLI, API y frontend.

Este flujo es el mismo en ambos modos. La diferencia entre `mock` y `openaq` está solo en el origen de los datos.

## Vista del frontend

El frontend vive en `frontend/` y se organiza por responsabilidad:

- `components/`: paneles y secciones visibles;
- `composables/`: carga de datos, filtros, estado reactivo y derivaciones;
- `config/`: configuración de vistas, gráficas y estaciones OpenAQ sugeridas;
- `services/`: cliente HTTP con `axios`;
- `utils/`: utilidades de apoyo y exportación de imágenes.

La aplicación no contiene lógica del motor. Su papel es:

- disparar corridas;
- mostrar el resumen ejecutivo;
- explicar las capas del modelo;
- comparar la corrida actual con el histórico local;
- facilitar la captura de evidencia visual.

## Decisiones arquitectónicas centrales

### Separación entre AQI y razonamiento difuso

El `AQI` se calcula primero como base normativa. La lógica difusa no sustituye esa capa, sino que opera después sobre variables derivadas. Esta decisión preserva trazabilidad regulatoria y evita convertir el sistema en una caja negra.

### Capa contextual desacoplada

Temperatura y humedad no forman parte de la malla principal de `54` reglas. Se resuelven en una matriz crisp `3 × 3` separada. Con ello se controla la complejidad combinatoria y se mantiene legibilidad metodológica.

### API fina y sin lógica de negocio

La API no recalcula reglas ni contiene heurísticas propias. Su responsabilidad es orquestar el pipeline, validar entradas simples, serializar la salida y publicar metadatos que el frontend usa para explicar el modelo.

### Persistencia local deliberadamente mínima

El histórico local sirve para comparación básica entre corridas y soporte a la vista `Evaluación`. No está diseñado para escenarios multiusuario ni para consulta analítica extensa.

## Vista de despliegue

El despliegue actual usa dos servicios Docker:

- `aqrisk-api`: backend Python, escucha internamente en `8010` y se expone por `18010` en el host;
- `aqrisk-frontend`: aplicación Vue/Vite, escucha internamente en `8080` y se expone por `18080`.

El histórico local se guarda en un volumen Docker dedicado. La configuración se carga desde `.env`.

## Fronteras y límites

La arquitectura actual resuelve el objetivo del TFM, pero deja fuera:

- autenticación y control de acceso;
- persistencia robusta;
- pruebas E2E;
- endurecimiento para despliegue público;
- operación distribuida o multiinstancia.

Estas ausencias no son omisiones accidentales. Son decisiones de alcance para priorizar un prototipo explicable y defendible.
