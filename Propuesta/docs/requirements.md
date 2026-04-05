# Requerimientos del módulo

## 1. Contexto

El módulo responde al objetivo general del TFM: desarrollar un módulo de monitoreo de calidad del aire para apoyar la evaluación del riesgo y la generación de alertas mediante inferencia difusa y datos abiertos de redes de monitoreo ambiental en entornos urbanos.

Este documento traduce los objetivos, la metodología y la propuesta conceptual en requerimientos de software para el primer corte implementable.

## 2. Alcance del primer corte

El primer corte se implementa como un prototipo funcional en Python, dockerizable y ejecutable por línea de comandos. Su alcance queda delimitado así:

- Fuente operativa principal: OpenAQ v3.
- Unidad de análisis: una estación o `location` de OpenAQ.
- Ventana temporal de análisis: hasta veinticuatro horas recientes por sensor.
- Cálculo base: AQI determinista para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`.
- Capa interpretativa: motor Mamdani para evaluación de riesgo y alertamiento.

## 3. Requerimientos funcionales del núcleo actual

### RF-01. Configuración del módulo

El sistema debe cargar configuración de ejecución desde variables de entorno y argumentos de línea de comandos.

### RF-02. Selección de fuente y modo de ejecución

El sistema debe permitir al menos dos modos:

- `mock`, para ejecutar el pipeline con datos de prueba controlados.
- `openaq`, para consultar datos reales en OpenAQ v3.

### RF-03. Descubrimiento de sensores

En modo `openaq`, el sistema debe recuperar los sensores asociados a un `location_id` y filtrar aquellos que correspondan a parámetros relevantes para el módulo.

### RF-04. Recuperación horaria de mediciones

El sistema debe consultar las series horarias de cada sensor seleccionado y construir una ventana temporal suficiente para calcular concentraciones representativas según ventana regulatoria.

### RF-05. Normalización de datos

El sistema debe normalizar nombres de parámetros, unidades, marcas temporales y estructura interna de las observaciones.

### RF-06. Control de calidad del dato

El sistema debe registrar el porcentaje de cobertura de cada observación horaria y derivar una cobertura global de la ventana analizada.

### RF-07. Consolidación del estado base

El sistema debe calcular subíndices AQI para los contaminantes soportados y consolidar un estado base mediante el subíndice dominante.

### RF-07a. Concentraciones representativas por contaminante

El sistema debe obtener la concentración representativa de cada contaminante con la regla temporal que le corresponda:

- promedio de 24 horas para `pm25` y `pm10`;
- promedio de 8 horas para `co`;
- valor horario para `no2`;
- selección entre 8 horas y 1 hora para `o3`, según tramo aplicable;
- selección entre 1 hora y 24 horas para `so2`, según tramo aplicable.

Cuando la ventana nominal no esté completa, el sistema podrá calcular una concentración representativa con serie parcial siempre que la cobertura efectiva alcance el umbral mínimo configurado.

### RF-08. Cálculo de persistencia

El sistema debe derivar una medida simple de persistencia a partir del comportamiento reciente del estado base en la ventana analizada.

### RF-09. Evaluación difusa del riesgo

El sistema debe transformar el estado base y la persistencia en una clasificación lingüística de riesgo mediante un sistema de inferencia Mamdani.

### RF-10. Alertamiento

El sistema debe emitir una alerta textual interpretable que incluya:

- nivel de riesgo,
- contaminante dominante,
- AQI global,
- cobertura del dato,
- reglas activadas.

### RF-11. Trazabilidad

El sistema debe conservar en la salida el origen de los datos, la estación consultada, la ventana temporal y los parámetros utilizados.

### RF-12. Salida estructurada

El sistema debe generar una salida estructurada en formato JSON apta para ser consumida más adelante por una interfaz web o por otros módulos.

## 4. Requerimientos funcionales previstos para una capa web posterior

Estos requerimientos no forman parte del primer corte implementado. Se documentan para mantener continuidad con la evolución prevista del artefacto.

### RFW-01. Dashboard operativo

El sistema deberá ofrecer un tablero con visualización del estado de calidad del aire, riesgo difuso, contaminante dominante, cobertura del dato y alerta activa.

### RFW-02. Consulta histórica

El sistema deberá permitir consulta de ejecuciones previas, con filtros por estación, fecha y nivel de riesgo.

### RFW-03. Perfil de usuario

El sistema deberá permitir que cada usuario consulte sus preferencias de visualización, estaciones de interés y configuraciones personales de seguimiento.

### RFW-04. Roles de acceso

El sistema deberá distinguir al menos entre usuario general y administrador.

### RFW-05. Administración

El sistema deberá permitir a un administrador gestionar fuentes habilitadas, estaciones monitoreadas, parámetros de ejecución y registros de funcionamiento del módulo.

### RFW-06. Exposición por API

El sistema deberá exponer la salida del módulo mediante una API para consumo por interfaz web y servicios externos.

## 5. Requerimientos no funcionales

### RNF-01. Reproducibilidad

La ejecución con la misma entrada y la misma configuración debe producir la misma salida.

### RNF-02. Trazabilidad

Cada resultado debe poder asociarse a fuente, estación, ventana temporal, cobertura y reglas activadas.

### RNF-03. Modularidad

La implementación debe separar ingesta, normalización, AQI, inferencia difusa, alertamiento e interfaz de ejecución.

### RNF-04. Auditabilidad

Las reglas difusas, las funciones de pertenencia y el criterio de cálculo del AQI deben estar definidos en código de forma explícita.

### RNF-05. Portabilidad

El prototipo debe ejecutarse en entorno local y en contenedor Docker sin depender de servicios externos distintos de OpenAQ.

### RNF-06. Extensibilidad

La estructura del código debe permitir incorporar nuevos contaminantes, nuevas fuentes y una futura interfaz web sin rehacer el núcleo del módulo.

### RNF-07. Separación entre núcleo y presentación

La futura interfaz web no debe alterar la lógica del cálculo AQI, la inferencia difusa ni la trazabilidad del pipeline.

## 6. Entradas y salidas

## Entradas mínimas

- `mode`
- `location_id` en modo `openaq`
- `OPENAQ_API_KEY` en modo `openaq`
- ventana temporal y número de horas

## Salidas mínimas

- identificador de estación
- contaminantes disponibles
- cobertura global
- subíndices AQI
- AQI global
- contaminante dominante
- persistencia
- riesgo difuso
- alerta textual
- reglas activadas

## 7. Estado actual frente a la hoja de desarrollo

### Implementado en el primer corte

- levantamiento de requerimientos;
- definición de arquitectura de software;
- estructura del proyecto;
- implementación inicial del pipeline en Python;
- dockerización básica;
- prueba de humo del módulo.

### Pendiente para la siguiente etapa

- integración real y validación con OpenAQ;
- almacenamiento persistente de ejecuciones;
- API de servicio;
- dashboard, perfil, roles y administración.

## 8. Criterios de validación del primer corte

- El pipeline debe ejecutarse completo en modo `mock`.
- El módulo debe fallar de forma controlada cuando falte `OPENAQ_API_KEY`.
- La salida debe conservar trazabilidad suficiente para auditoría manual.
- Las reglas activadas deben ser visibles en el resultado.
- El cálculo AQI debe ser verificable para casos simples de contaminantes criterio con distinta ventana regulatoria.
