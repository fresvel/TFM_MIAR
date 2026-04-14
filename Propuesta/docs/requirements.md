# Alcance funcional y criterios de validación

## Propósito

Este documento fija qué resuelve hoy el prototipo y cómo se valida ese estado. No describe una hoja de ruta futura: resume el artefacto implementado en `Propuesta`.

## Alcance implementado

El sistema cubre actualmente:

- ejecución en `mode=mock` con escenarios controlados;
- ejecución en `mode=openaq` por `location_id`;
- descubrimiento de ubicaciones y sensores `OpenAQ`;
- recuperación y normalización de series horarias;
- cálculo de cobertura efectiva;
- cálculo de subíndices y `AQI` global para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`;
- derivación de `concurrence` y `persistence`;
- inferencia `Mamdani` con base principal de `54` reglas;
- ajuste contextual crisp sobre temperatura y humedad con `9` reglas;
- generación de alerta interpretable y payload estructurado;
- persistencia local de corridas;
- exposición por CLI, API HTTP y frontend;
- despliegue dockerizado de todo el stack.

## Requerimientos funcionales

### Configuración y modos

El sistema debe aceptar configuración desde variables de entorno y desde parámetros de ejecución. Debe soportar, al menos, los modos `mock` y `openaq`.

### Adquisición y preprocesamiento

En modo `openaq`, el sistema debe recuperar sensores y series relevantes de una estación real, normalizar nombres y estructura temporal y construir una representación interna consistente antes de la evaluación.

### Evaluación normativa

El módulo debe calcular subíndices `AQI` y consolidar un `AQI` global usando la referencia `EPA/AQS`.

### Variables auxiliares

El sistema debe derivar `concurrence`, `persistence` y `coverage` como entradas de apoyo a la interpretación del riesgo.

### Inferencia y ajuste contextual

El prototipo debe generar una salida lingüística mediante inferencia `Mamdani` y, cuando existan datos contextuales válidos, evaluar una capa contextual separada.

### Trazabilidad y explicabilidad

La salida debe conservar información suficiente para explicar:

- fuente y ubicación;
- cobertura global;
- parámetros soportados y no soportados;
- subíndices y contaminante dominante;
- score y etiqueta principal;
- reglas activadas;
- salida final y ajuste contextual;
- alerta resultante.

### Operación web

La interfaz debe permitir:

- ejecutar corridas;
- seleccionar escenarios y estaciones;
- consultar `Dashboard`, `Trazabilidad`, `Explicabilidad` y `Evaluación`;
- comparar la corrida actual con el histórico local;
- exportar imágenes de gráficas para documentación.

## Requerimientos no funcionales

El estado actual del prototipo prioriza:

- reproducibilidad en `mock`;
- modularidad entre dominio, cálculo normativo, inferencia, API y presentación;
- auditabilidad de la base normativa y de la base de reglas;
- portabilidad para ejecución local y con Docker;
- mantenibilidad del backend bajo una estructura POO por servicios y modelos.

## Criterios de validación actuales

La validación disponible hoy cubre:

- ejecución de extremo a extremo del pipeline en `mock`;
- fallo controlado de `mode=openaq` cuando falta `OPENAQ_API_KEY`;
- contrato HTTP básico del backend;
- persistencia y consulta del histórico local;
- activación de múltiples reglas en `diffuse_overlap`;
- consumo estable del contrato por el frontend.

Estado actual de pruebas automatizadas:

- `11` pruebas backend en `tests/test_pipeline.py` y `tests/test_api.py`.

Comando de ejecución:

```bash
cd Propuesta
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Validación manual esperada

Además de la suite backend, el prototipo debe verificarse manualmente en la interfaz:

1. correr una evaluación `mock`;
2. revisar trazabilidad de reglas y ajustes contextuales;
3. inspeccionar paneles de explicabilidad;
4. comprobar comparación con histórico;
5. si hay credencial, ejecutar una corrida `openaq`.

## Fuera de alcance

No forman parte del estado actual:

- autenticación;
- perfiles y roles;
- administración;
- persistencia robusta en `SQLite` o `PostgreSQL`;
- endurecimiento para despliegue público;
- pruebas E2E;
- operación multiusuario.
