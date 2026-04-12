# Requerimientos del módulo

## 1. Contexto

El prototipo implementa el núcleo del TFM: un módulo de monitoreo de calidad del aire que combina datos abiertos, cálculo AQI y lógica difusa para evaluar riesgo y generar alertas trazables.

Este documento ya no describe una idea preliminar. Describe el estado actual del prototipo y los vacíos que continúan abiertos.

## 2. Alcance actual del prototipo

El alcance implementado incluye:

- fuente operativa principal: `OpenAQ v3`;
- modo `mock` para escenarios controlados;
- modo `openaq` para corridas reales;
- análisis por `location_id`;
- ventana de análisis con series horarias recientes;
- cálculo AQI para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`;
- derivación de persistencia, concurrencia y cobertura;
- inferencia difusa `Mamdani`;
- ajuste contextual;
- salida JSON trazable;
- API HTTP;
- frontend web;
- ejecución dockerizada.

Quedan fuera del alcance actual:

- autenticación;
- perfiles;
- roles;
- administración;
- persistencia robusta en `SQLite` o `PostgreSQL`;
- validación E2E completa.

## 3. Requerimientos funcionales implementados

### RF-01. Configuración de ejecución

El sistema debe aceptar configuración por variables de entorno y argumentos de ejecución.

### RF-02. Modos de operación

El sistema debe permitir al menos:

- `mock`;
- `openaq`.

### RF-03. Descubrimiento de sensores

En modo `openaq`, el sistema debe recuperar sensores por `location_id` y filtrar parámetros relevantes.

### RF-04. Recuperación de series horarias

El sistema debe consultar observaciones horarias por sensor para construir la ventana de análisis.

### RF-05. Estandarización

El sistema debe normalizar nombres de parámetros, estructura temporal y representación interna de observaciones.

### RF-06. Control de cobertura

El sistema debe calcular cobertura efectiva para la ventana analizada y exponerla en la salida.

### RF-07. Evaluación AQI base

El sistema debe calcular subíndices AQI para contaminantes soportados y consolidar el valor dominante.

### RF-08. Concentraciones representativas

El sistema debe usar la ventana regulatoria correspondiente a cada contaminante:

- `pm25`: 24 horas;
- `pm10`: 24 horas;
- `co`: 8 horas;
- `no2`: 1 hora;
- `o3`: 8 horas o 1 hora;
- `so2`: 1 hora o 24 horas.

### RF-09. Variables auxiliares

El sistema debe derivar persistencia, concurrencia y métricas auxiliares necesarias para la inferencia.

### RF-10. Evaluación difusa

El sistema debe producir una categoría lingüística de riesgo mediante un sistema `Mamdani`.

### RF-11. Ajuste contextual

El sistema debe permitir modulación adicional del riesgo cuando existan variables contextuales disponibles.

### RF-12. Alertamiento

El sistema debe emitir una alerta interpretable que incluya:

- AQI global;
- contaminante dominante;
- riesgo final;
- cobertura;
- reglas activadas.

### RF-13. Trazabilidad

El sistema debe conservar fuente, estación, ventana temporal, parámetros procesados y decisiones intermedias.

### RF-14. Salida estructurada

El sistema debe producir salida JSON consumible por API y frontend.

### RF-15. API HTTP

El sistema debe exponer endpoints de salud, metadatos, evaluación, escenarios, ubicaciones, sensores e histórico.

### RF-16. Interfaz web

El sistema debe ofrecer una interfaz para:

- configurar corridas;
- seleccionar escenarios;
- visualizar resultados;
- revisar explicabilidad;
- consultar histórico local.

## 4. Requerimientos funcionales aún abiertos

### RFA-01. Persistencia robusta

El sistema debería migrar el histórico local a una base de datos consultable.

### RFA-02. Gestión de acceso

El sistema podría incorporar autenticación y distinción de perfiles si el alcance del TFM lo exige.

### RFA-03. Administración

La administración de fuentes, estaciones, parámetros de ejecución y registros queda abierta para una etapa posterior.

### RFA-04. Exposición pública controlada

La publicación de la aplicación en entorno accesible externamente sigue pendiente.

## 5. Requerimientos no funcionales

### RNF-01. Reproducibilidad

La misma entrada y la misma configuración deben producir la misma salida.

### RNF-02. Trazabilidad

Cada corrida debe poder auditarse por fuente, ventana, cobertura y reglas activadas.

### RNF-03. Modularidad

El sistema debe mantener separación entre dominio, procesamiento, inferencia, API y presentación.

### RNF-04. Auditabilidad

Las reglas difusas y el criterio AQI deben ser explícitos e inspeccionables.

### RNF-05. Portabilidad

El prototipo debe poder ejecutarse localmente y mediante Docker.

### RNF-06. Extensibilidad

La estructura debe permitir evolución posterior hacia persistencia robusta, validación ampliada y gestión web más completa.

## 6. Entradas mínimas

- `mode`
- `location_id` en modo `openaq`
- `OPENAQ_API_KEY` en modo `openaq`
- parámetros de ventana y cobertura mínima

## 7. Salidas mínimas

- estación consultada
- parámetros disponibles
- cobertura global
- subíndices AQI
- AQI global
- contaminante dominante
- persistencia
- concurrencia
- riesgo final
- alerta textual
- reglas activadas

## 8. Estado de implementación

### Implementado

- requerimientos base del módulo;
- arquitectura software;
- núcleo Python;
- API HTTP;
- interfaz web;
- dockerización;
- histórico local;
- escenarios controlados;
- pruebas de humo.

### Pendiente

- persistencia robusta;
- pruebas de API;
- pruebas del frontend;
- pruebas E2E;
- capturas integradas en la memoria;
- roles y administración, si se decidiera ampliar alcance.

## 9. Criterios de validación actuales

- el pipeline debe ejecutarse completo en `mock`;
- el módulo debe fallar de forma controlada cuando falte `OPENAQ_API_KEY`;
- la salida debe mantener trazabilidad suficiente para inspección manual;
- las reglas activadas deben ser visibles;
- el cálculo AQI debe ser verificable para contaminantes soportados;
- la web debe consumir correctamente la API del prototipo.

