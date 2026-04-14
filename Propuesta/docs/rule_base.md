# Base normativa y base de reglas

## Propósito

Este documento describe la lógica del modelo implementado en el prototipo: cómo se construye el estado base mediante `AQI`, qué variables alimentan la inferencia difusa, cómo se organiza la malla principal de reglas y cómo actúa la capa contextual.

## 1. Consolidación normativa con AQI

El estado base del aire se obtiene por contaminante y se consolida con el subíndice dominante. El valor global del `AQI` corresponde al subíndice más alto entre los contaminantes soportados en la ventana analizada.

La referencia normativa de esta capa es la tabla vigente de `AQI breakpoints` de `EPA/AQS`:

- <https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html>

El backend implementa esta capa en `aqi/epa.py`.

## 2. Ventanas regulatorias implementadas

- `pm25`: promedio de 24 horas.
- `pm10`: promedio de 24 horas.
- `co`: promedio de 8 horas.
- `no2`: valor horario más reciente, convertido de `ppm` a `ppb`.
- `o3`: selección entre promedio de 8 horas y valor horario de 1 hora cuando este último entra en el tramo aplicable del AQI.
- `so2`: selección entre valor horario y promedio de 24 horas, conservando el subíndice más alto aplicable.

Cuando una ventana no está completa, el módulo admite cálculo con serie parcial si la cobertura efectiva alcanza el umbral mínimo configurado. En el estado actual ese umbral es `80%`.

## 3. Variables de entrada del motor difuso

La malla principal usa tres entradas:

- `aqi`: estado base consolidado;
- `concurrence`: cercanía entre contaminantes respecto del dominante;
- `persistence`: estabilidad reciente del estado base.

La `coverage` ya no forma parte de la malla principal. Se conserva como criterio de calidad del dato y de cautela en la salida. `temperature` y `humidity` se usan en una capa contextual separada.

## 4. Conjuntos lingüísticos

### AQI

El antecedente `aqi` sigue las seis categorías públicas del índice:

- `good`
- `moderate`
- `unhealthy_sensitive_groups`
- `unhealthy`
- `very_unhealthy`
- `hazardous`

### Concurrence

- `low`
- `medium`
- `high`

### Persistence

- `low`
- `medium`
- `high`

### Risk

La salida principal usa las mismas seis categorías públicas:

- `good`
- `moderate`
- `unhealthy_sensitive_groups`
- `unhealthy`
- `very_unhealthy`
- `hazardous`

## 5. Base principal de reglas

La base principal contiene `54` reglas y se construye como una malla completa:

`6 categorías AQI × 3 niveles de concurrence × 3 niveles de persistence = 54`

La implementación actual sigue un criterio monotónico:

- la salida no mejora respecto del estado base;
- la salida se mantiene o escala cuando aumentan concurrencia o persistencia;
- la combinación extrema conserva o incrementa la severidad del episodio.

### Lectura por bloques

#### AQI base `good`

La salida suele mantenerse en `good`, pero puede escalar a `moderate` o `unhealthy_sensitive_groups` si concurrencia y persistencia crecen.

#### AQI base `moderate`

La salida parte de `moderate` y puede escalar a `unhealthy_sensitive_groups` o `unhealthy` cuando el episodio deja de ser aislado o transitorio.

#### AQI base `unhealthy_sensitive_groups`

Este bloque puede mantenerse o escalar a `unhealthy` y `very_unhealthy`, según la combinación de concurrencia y persistencia.

#### AQI base `unhealthy`

La salida parte de `unhealthy` y puede llegar a `very_unhealthy` o `hazardous`.

#### AQI base `very_unhealthy`

La mayoría de combinaciones altas ya empujan la salida hacia `hazardous`.

#### AQI base `hazardous`

Todas las combinaciones se mantienen en `hazardous`.

## 6. Concurrence

La concurrencia mide si existen contaminantes acompañantes próximos al dominante.

Regla operativa:

- se define un umbral de cercanía igual al `80%` del dominante, con mínimo operativo de `25`;
- se excluye el contaminante dominante;
- cada contaminante restante aporta una cercanía normalizada entre `0` y `1`;
- la suma se reescala a `0–100`.

La saturación está diseñada para reflejar que a partir de varios acompañantes relevantes el episodio ya debe leerse como multi-contaminante alto.

## 7. Persistence

La persistencia resume si el estado base reciente se mantiene en varias ventanas sucesivas del propio módulo. Su propósito es distinguir entre un pico aislado y un deterioro más estable.

## 8. Mecanismo de inferencia

El motor difuso usa:

- implicación: mínimo;
- agregación: máximo;
- defuzzificación: centroide discreto en el rango `0..500`.

Las curvas de membresía y la malla de reglas residen en `fuzzy/constants.py` y `fuzzy/mamdani.py`.

## 9. Capa contextual

Temperatura y humedad no entran en la malla principal. Se usan en una capa crisp separada con `9` reglas (`3 × 3`):

- `temperature`: `low`, `normal`, `high`
- `humidity`: `low`, `medium`, `high`

La matriz contextual implementada es:

- `low/low`, `low/medium`, `low/high`: sin escalado
- `normal/low`, `normal/medium`: sin escalado
- `normal/high`: escala una categoría
- `high/low`: sin escalado
- `high/medium`: escala una categoría
- `high/high`: escala una categoría

La capa contextual no recalcula el `AQI`. Su función es modular la severidad operativa cuando el episodio ya presenta una condición suficientemente relevante.

## 10. Condición de aplicación contextual

El escalado contextual no se aplica de manera indiscriminada. En el estado actual:

- si la regla contextual no escala, la salida principal se conserva;
- si la regla contextual escala, el sistema comprueba un guardarraíl adicional;
- el escalado se permite cuando el `AQI` global es al menos `101` o cuando el subíndice particulado (`pm25` o `pm10`) alcanza `100`.

Con ello se evita sobrerreaccionar ante episodios leves solo por condiciones contextuales desfavorables.

## 11. Lectura de la salida

La salida numérica del centroide se interpreta con las mismas categorías públicas del índice:

- `0-50`: `good`
- `51-100`: `moderate`
- `101-150`: `unhealthy_sensitive_groups`
- `151-200`: `unhealthy`
- `201-300`: `very_unhealthy`
- `301-500`: `hazardous`

## 12. Escenarios controlados

Los escenarios `mock` no alteran la base de reglas. Sirven para demostrar comportamientos concretos del artefacto:

- `urban_escalation`: caso de escalado contextual;
- `particulate_pressure`: presión particulada sostenida;
- `moderate_multicontaminant`: concurrencia alta sin episodio extremo;
- `diffuse_overlap`: solape difuso y activación de varias reglas.
