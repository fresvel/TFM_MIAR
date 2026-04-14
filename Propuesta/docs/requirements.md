# Alcance funcional y criterios de validación

## Contexto

Este documento describe qué resuelve hoy el prototipo y qué queda deliberadamente fuera del alcance. No es una lista especulativa: resume el estado implementado de `Propuesta`.

## Alcance implementado

El sistema cubre las siguientes capacidades:

- ejecución en modo `mock` para escenarios controlados;
- ejecución en modo `openaq` para corridas reales por `location_id`;
- descubrimiento de sensores y recuperación de series horarias;
- normalización de observaciones y cálculo de cobertura;
- cálculo de subíndices y AQI global para contaminantes criterio;
- derivación de `concurrence` y `persistence`;
- inferencia `Mamdani` con base principal de `54` reglas;
- ajuste contextual sobre temperatura y humedad con matriz crisp de `9` reglas;
- generación de alerta interpretable y salida estructurada;
- histórico local de corridas;
- exposición por CLI, API HTTP y frontend web;
- despliegue dockerizado del stack completo.

## Requerimientos funcionales clave

### Configuración y modos

El sistema debe aceptar configuración por variables de entorno y por parámetros de ejecución. Debe soportar al menos los modos `mock` y `openaq`.

### Adquisición y preprocesamiento

En modo `openaq`, el sistema debe recuperar sensores y series temporales para parámetros relevantes. Debe normalizar nombres, estructura temporal y representación interna antes de la evaluación.

### Evaluación normativa

El módulo debe calcular subíndices AQI y consolidar un AQI global con base en la referencia `EPA/AQS` para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`.

### Variables auxiliares

El prototipo debe derivar `concurrence`, `persistence` y `coverage` como soporte a la evaluación del riesgo y a la trazabilidad de la salida.

### Inferencia y ajuste contextual

El sistema debe generar una salida lingüística mediante inferencia `Mamdani` y, cuando existan datos contextuales válidos, evaluar una capa adicional de ajuste explícito.

### Exposición y trazabilidad

La salida debe conservar la información necesaria para explicar:

- fuente y ubicación;
- parámetros usados y no usados;
- cobertura global;
- subíndices y contaminante dominante;
- reglas activadas;
- salida principal y salida final;
- ajustes contextuales.

### Operación web

La interfaz debe permitir:

- ejecutar corridas;
- seleccionar escenarios y ubicaciones;
- consultar trazabilidad;
- revisar explicabilidad;
- comparar la corrida actual con el histórico local.

## Requerimientos no funcionales

- reproducibilidad para una misma entrada;
- modularidad entre dominio, procesamiento, inferencia y presentación;
- auditabilidad del criterio AQI y de la base de reglas;
- portabilidad para ejecución local y con Docker;
- extensibilidad hacia persistencia robusta y validación ampliada.

## Criterios de validación actuales

- el pipeline debe ejecutarse de extremo a extremo en modo `mock`;
- `mode=openaq` debe fallar de forma controlada si falta `OPENAQ_API_KEY`;
- la API debe exponer sus endpoints básicos y responder con payload trazable;
- el frontend debe consumir la API sin transformar el contrato del backend;
- el histórico local debe registrar y devolver corridas previas.

## Fuera de alcance

No forman parte del estado actual:

- autenticación;
- perfiles y roles;
- administración;
- persistencia robusta en `SQLite` o `PostgreSQL`;
- pruebas E2E y endurecimiento para exposición pública.
