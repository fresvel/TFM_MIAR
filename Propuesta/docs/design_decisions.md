# Decisiones de diseño del núcleo IA

## 1. Punto de partida

El diseño del módulo adopta una estrategia de dos capas:

1. una capa normativa para construir el estado base del aire;
2. una capa difusa para ajustar riesgo y alerta.

La primera capa sigue el marco EPA. La segunda intenta resolver aspectos que el AQI clásico no modela con detalle suficiente.

## 2. Qué se toma de EPA

Del marco EPA se adoptan:

- contaminantes criterio;
- periodos de promediación;
- breakpoints;
- categorías de clasificación;
- interpretación básica del riesgo.

La selección operativa de `pm25`, `pm10`, `co`, `no2`, `o3` y `so2` no se apoya solo en el folleto divulgativo de EPA de 2014. Se apoya de forma específica en la tabla vigente de `AQI breakpoints` publicada por `EPA/AQS`, que es la referencia utilizada en el código para definir tramos, ventanas regulatorias y categorías del índice:

- `AQI breakpoints de EPA/AQS`: <https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html>

La implementación del prototipo usa estas categorías como estado base:

- `good`
- `moderate`
- `unhealthy_sensitive_groups`
- `unhealthy`
- `very_unhealthy`
- `hazardous`

## 3. Qué no cubre EPA y se resuelve en el módulo

EPA no define:

- una base de reglas difusas;
- un mecanismo de concurrencia entre contaminantes cercanos al dominante;
- una medida de persistencia temporal del deterioro;
- una forma de integrar temperatura y humedad como moduladores del riesgo;
- una penalización difusa por datos parcialmente incompletos.

Estas lagunas justifican la segunda capa del artefacto.

## 4. Exclusión de CO2 del núcleo actual

`CO2` aparece en varios antecedentes del SLR, pero su uso se concentra sobre todo en:

- calidad de aire interior;
- IAQ;
- combinaciones con TVOC, CH4 u otros sensores de confort/ventilación.

El núcleo actual del TFM se centra en AQI urbano con base regulatoria. Por ello, `CO2` no se incorpora al estado base. Puede añadirse después como variable contextual en una extensión indoor o híbrida.

## 5. Variables elegidas para la capa difusa

La malla principal no opera sobre todos los contaminantes crudos. Opera sobre variables agregadas:

- `aqi`
- `concurrence`
- `persistence`

Se añade una capa contextual externa con:

- `temperature`
- `humidity`

Esta separación evita mezclar dos problemas distintos:

- clasificación base del estado del aire;
- ajuste operativo del riesgo.

## 6. Definición de concurrencia

La concurrencia se define como la presencia de varios contaminantes con subíndices próximos al dominante.

Regla operativa:

- `low`: solo un contaminante alcanza la banda cercana al dominante;
- `medium`: dos contaminantes alcanzan esa banda;
- `high`: tres o más contaminantes alcanzan esa banda.

La banda cercana al dominante se fija en `80%` del AQI global, con un mínimo operativo de `25`.

## 7. Definición de persistencia

La persistencia se calcula a partir de estados AQI sucesivos del propio módulo. No se limita al material particulado. El objetivo es detectar si el deterioro se mantiene en el tiempo inmediato.

## 8. Justificación del tamaño de la base de reglas

La primera versión del prototipo usó `7` reglas como prueba de funcionamiento. Esa versión ya no se considera base final.

La base actual usa `54` reglas:

- `6` niveles EPA para `aqi`;
- `3` niveles para `concurrence`;
- `3` niveles para `persistence`.

Esto produce una malla completa:

`6 × 3 × 3 = 54`

La decisión responde mejor a criterios de:

- exhaustividad;
- trazabilidad;
- monotonicidad;
- defensa metodológica ante tribunal.

## 9. Relación con antecedentes

Los antecedentes revisados muestran bases explícitas de tamaño medio o alto cuando el sistema difuso opera sobre entradas instrumentales directas:

- `A165`: `64` reglas;
- `A167`: `36` reglas;
- `A114`: `36` reglas.

El módulo del TFM adopta una arquitectura distinta: primero consolida el estado base con AQI y luego aplica inferencia difusa sobre variables agregadas. Esto justifica una base completa, pero no desmesurada.

## 10. Papel de temperatura y humedad

`Temperature` y `humidity` no entran en la malla principal de 54 reglas. Se usan como moduladores externos porque:

- su papel es contextual;
- no pertenecen al AQI regulatorio;
- introducirlas en la malla principal dispararía la combinatoria sin mejorar necesariamente la interpretabilidad.

La capa contextual se resuelve con una base explícita de `9` reglas (`3 × 3`) sobre:

- `temperature`: `low`, `normal`, `high`;
- `humidity`: `low`, `medium`, `high`.

Esta capa no recalcula el AQI. Ajusta la severidad operativa de la salida cuando el riesgo base ya se encuentra comprometido o cuando el particulado está en un tramo relevante.

## 11. Tratamiento de series incompletas

Los periodos regulatorios no siempre llegan completos en datos abiertos. El módulo admite series parciales cuando la cobertura efectiva supera el umbral mínimo configurado. Esta decisión evita descartar contaminantes útiles por huecos pequeños y mantiene trazabilidad del criterio aplicado.
