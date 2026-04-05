# Base de reglas del módulo

## 1. Regla de consolidación AQI

El estado base del aire se obtiene por contaminante y luego se consolida con el subíndice dominante. El valor global del AQI corresponde al subíndice más alto entre los contaminantes soportados en la ventana analizada.

La referencia normativa de esta capa es la tabla actual de `AQI breakpoints` de `EPA/AQS`. A partir de esa fuente se fijan los contaminantes soportados, los tramos de concentración, las ventanas regulatorias y la lectura por categorías que utiliza el módulo:

- <https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html>

## 2. Ventanas regulatorias implementadas

- `pm25`: promedio de 24 horas.
- `pm10`: promedio de 24 horas.
- `co`: promedio de 8 horas sobre valores horarios.
- `no2`: valor horario más reciente, convertido de `ppm` a `ppb`.
- `o3`: comparación entre promedio de 8 horas y valor horario de 1 hora cuando este último entra en el tramo aplicable del AQI.
- `so2`: comparación entre valor horario y promedio de 24 horas, seleccionando el subíndice más alto aplicable.

Cuando una ventana no está completa, el módulo admite cálculo con serie parcial siempre que la cobertura efectiva alcance el umbral mínimo configurado. En el estado actual ese umbral es `80%`.

Esta decisión mantiene correspondencia con la lógica regulatoria de `EPA/AQS`, pero adapta el cálculo a las limitaciones habituales de cobertura en datos abiertos. El módulo registra esa condición para no ocultar que la ventana fue parcialmente observada.

## 3. Variables de entrada del motor difuso

El sistema difuso usa tres entradas principales en la malla base:

- `aqi`: estado base consolidado.
- `persistencia`: estabilidad reciente del estado base.
- `concurrencia`: proximidad entre varios contaminantes respecto del subíndice dominante.

La `coverage` ya no forma parte de la malla principal. Se mantiene como criterio de calidad del dato y de cautela en la salida. `Temperatura` y `humedad` se utilizan en una capa contextual explícita.

## 4. Conjuntos lingüísticos

### AQI

- `bueno`
- `moderado`
- `alto`
- `muy_alto`

### Persistencia

- `baja`
- `media`
- `alta`

### Concurrencia

- `low`
- `medium`
- `high`

### Riesgo

- `good`
- `moderate`
- `unhealthy_sensitive_groups`
- `unhealthy`
- `very_unhealthy`
- `hazardous`

## 5. Reglas difusas implementadas

La base principal contiene `54` reglas (`6 × 3 × 3`). Se construye a partir de:

- `6` categorías EPA para `aqi`;
- `3` niveles de `concurrencia`;
- `3` niveles de `persistencia`.

El criterio general es monotónico. La salida no puede mejorar respecto del estado base y solo puede mantenerse o escalar cuando aumenta concurrencia o persistencia.

### Grupo 1. AQI base `good`

- con concurrencia y persistencia bajas, la salida se mantiene en `good`;
- con concurrencia o persistencia elevadas, la salida puede escalar a `moderate`;
- con concurrencia alta y persistencia alta, la salida puede escalar a `unhealthy_sensitive_groups`.

### Grupo 2. AQI base `moderate`

- con baja concurrencia y baja persistencia, la salida se mantiene en `moderate`;
- cuando aumenta la concurrencia o la persistencia, la salida escala a `unhealthy_sensitive_groups`;
- en el caso más desfavorable del bloque, la salida alcanza `unhealthy`.

### Grupo 3. AQI base `unhealthy_sensitive_groups`

- el bloque parte de `unhealthy_sensitive_groups`;
- la combinación de concurrencia media/alta y persistencia media/alta eleva la salida a `unhealthy`;
- la combinación extrema del bloque eleva la salida a `very_unhealthy`.

### Grupo 4. AQI base `unhealthy`

- el bloque parte de `unhealthy`;
- la combinación de persistencia alta o concurrencia alta desplaza la salida a `very_unhealthy`;
- la combinación extrema del bloque eleva la salida a `hazardous`.

### Grupo 5. AQI base `very_unhealthy`

- el bloque parte de `very_unhealthy`;
- las combinaciones medias y altas llevan rápidamente a `hazardous`;
- la salida nunca baja del nivel base.

### Grupo 6. AQI base `hazardous`

- todas las combinaciones del bloque permanecen en `hazardous`.

### Reglas contextuales fuera de la malla principal

La capa contextual contiene `9` reglas (`3 × 3`) a partir de:

- `temperature`: `low`, `normal`, `high`;
- `humidity`: `low`, `medium`, `high`.

Su función es modular la severidad de la salida principal cuando el contexto atmosférico sugiere condiciones menos favorables.

#### Regla CTX-1

Si `temperature` es `low` y `humidity` es `low`, no se modifica la salida.

#### Regla CTX-2

Si `temperature` es `low` y `humidity` es `medium`, no se modifica la salida.

#### Regla CTX-3

Si `temperature` es `low` y `humidity` es `high`, no se modifica la salida.

#### Regla CTX-4

Si `temperature` es `normal` y `humidity` es `low`, no se modifica la salida.

#### Regla CTX-5

Si `temperature` es `normal` y `humidity` es `medium`, no se modifica la salida.

#### Regla CTX-6

Si `temperature` es `normal` y `humidity` es `high`, la salida escala una categoría.

#### Regla CTX-7

Si `temperature` es `high` y `humidity` es `low`, no se modifica la salida.

#### Regla CTX-8

Si `temperature` es `high` y `humidity` es `medium`, la salida escala una categoría.

#### Regla CTX-9

Si `temperature` es `high` y `humidity` es `high`, la salida escala una categoría.

Estas reglas solo se aplican cuando el AQI base es al menos `unhealthy_sensitive_groups` o cuando el índice particulado alcanza un tramo relevante.

## 5.1 Justificación del tamaño de la base

La base actual tiene `54` reglas porque el módulo usa una malla completa sobre las tres variables de decisión principales y evita un diseño parcial o ad hoc.

Esta decisión mantiene auditabilidad y al mismo tiempo evita una explosión combinatoria mayor. En los antecedentes revisados aparecen bases grandes cuando el FIS opera directamente sobre múltiples entradas instrumentales:

- `A165`: `64` reglas para `CO`, `CO2` y `CH4` con cinco clases de salida.
- `A167`: `36` reglas para dos sensores de `CO` con seis clases AQI/IAQ.
- `A114`: `36` reglas para humo, polvo, temperatura y humedad con tres clases de calidad ambiental.

El módulo del TFM usa otra estrategia: separar un núcleo determinista de consolidación AQI y una malla difusa sobre variables de decisión agregadas. Esto permite una base explícita, completa y justificable sin depender de combinaciones directas de todos los contaminantes crudos.

## 6. Mecanismo de inferencia

- implicación: mínimo;
- agregación: máximo;
- defuzzificación: centroide discreto en el rango `0..500`.

## 7. Lectura de la salida

La salida numérica del centroide se traduce según las categorías EPA:

- `0-50`: `good`;
- `51-100`: `moderate`;
- `101-150`: `unhealthy_sensitive_groups`;
- `151-200`: `unhealthy`;
- `201-300`: `very_unhealthy`;
- `301-500`: `hazardous`.
