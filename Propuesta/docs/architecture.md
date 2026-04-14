# Arquitectura del prototipo

## Resumen

`AQRisk` está construido como un prototipo modular con separación clara entre núcleo de evaluación, exposición por API y cliente web. La arquitectura prioriza tres propiedades del TFM: auditabilidad, explicabilidad y facilidad de despliegue local.

## Vista funcional

La ejecución completa sigue cinco capas:

1. adquisición y normalización de datos;
2. consolidación normativa del estado base mediante AQI;
3. derivación de variables auxiliares;
4. inferencia difusa principal y ajuste contextual;
5. construcción de alerta, persistencia local y exposición por API/frontend.

La separación es intencional. El AQI conserva su papel normativo y la capa difusa opera sobre variables derivadas, no sobre todos los contaminantes crudos.

## Vista de software

El paquete `aqrisk` queda organizado así:

- `domain`: modelos tipados y estructura de resultados.
- `ingestion`: cliente `OpenAQ` y recuperación de sensores/series.
- `processing`: normalización, cobertura, persistencia, concurrencia y reglas contextuales.
- `aqi`: cálculo determinista del índice con base `EPA/AQS`.
- `fuzzy`: funciones de pertenencia, base de reglas y motor `Mamdani`.
- `alerting`: composición de la salida operativa final.
- `application`: orquestación del pipeline y escenarios `mock`.
- `api`: backend HTTP.
- `storage`: histórico local.
- `interfaces`: CLI.

El frontend vive en `frontend/` y consume la API como cliente separado. No contiene lógica del motor; su responsabilidad es operar el prototipo y exponer capas de lectura.

## Flujo de ejecución

1. Resolver configuración desde entorno y parámetros de entrada.
2. Seleccionar modo `mock` u `openaq`.
3. Recuperar sensores y observaciones.
4. Normalizar series y calcular cobertura efectiva.
5. Obtener concentraciones representativas y subíndices AQI.
6. Consolidar AQI global y contaminante dominante.
7. Calcular `concurrence` y `persistence`.
8. Ejecutar la malla `Mamdani`.
9. Aplicar la capa contextual crisp si existen temperatura y humedad válidas.
10. Generar salida final, alerta e histórico.
11. Publicar resultados a través de CLI, API y frontend.

## Vista de despliegue

El despliegue actual usa dos servicios:

- `aqrisk-api`: backend Python expuesto en el host por `18010` y escuchando internamente en `8010`.
- `aqrisk-frontend`: aplicación Vue/Vite expuesta en el host por `18080`.

El histórico local se persiste en un volumen Docker. La solución es suficiente para el prototipo, pero no sustituye una base de datos robusta.

## Decisiones arquitectónicas

### Núcleo modular monoproceso

Se evita una arquitectura distribuida porque el objetivo del TFM no es escalar horizontalmente, sino demostrar razonamiento auditable y trazabilidad de extremo a extremo con complejidad controlada.

### Separación entre AQI y lógica difusa

El AQI se calcula de forma normativa y explícita. La inferencia difusa entra después, sobre variables agregadas. Esta decisión mantiene correspondencia con la referencia regulatoria y evita un sistema opaco.

### Capa contextual desacoplada

Temperatura y humedad no forman parte de la malla principal. La modulación contextual se resuelve con una matriz crisp `3 × 3`. Con ello se contiene la explosión combinatoria y se preserva interpretabilidad.

### Histórico local transitorio

El almacenamiento actual permite comparación básica entre corridas y soporte para la interfaz. No resuelve consulta avanzada, concurrencia multiusuario ni persistencia robusta.

## Estado de organización

La mayor deuda de organización estaba en el frontend, donde `App.vue` acumulaba estado, efectos, builders de gráficas y control de captura. Esa lógica ya está separada en:

- `composables/` para estado y derivación reactiva;
- `config/` para opciones y guías;
- `utils/` para helpers puros.

## Vacíos abiertos

- persistencia robusta;
- pruebas de frontend y E2E;
- autenticación y gestión de acceso si el alcance creciera;
- endurecimiento para despliegue público.
