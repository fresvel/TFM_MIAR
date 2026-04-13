# Notas Técnicas Para Defensa: AQI, Dominancia y Motor Difuso

Este documento resume el funcionamiento real del prototipo AQRisk para poder explicarlo con precisión en defensa. Está basado en la implementación actual del backend, no en una descripción idealizada.

Archivos fuente principales:

- `Propuesta/src/aqrisk/aqi/epa.py`
- `Propuesta/src/aqrisk/application/pipeline.py`
- `Propuesta/src/aqrisk/processing/concurrence.py`
- `Propuesta/src/aqrisk/processing/context.py`
- `Propuesta/src/aqrisk/fuzzy/mamdani.py`

## 1. Idea General Del Flujo

El sistema sigue esta secuencia:

1. cargar y normalizar observaciones;
2. calcular subíndices AQI por contaminante;
3. obtener el AQI global y el contaminante dominante;
4. derivar persistencia y concurrencia;
5. ejecutar el motor difuso Mamdani;
6. aplicar ajuste contextual si existe temperatura y humedad;
7. construir alerta y salida final.

En notación compacta:

\[
\text{Snapshot} \rightarrow \text{AQIResult} \rightarrow (\text{Persistence}, \text{Concurrence}) \rightarrow \text{Fuzzy Engine} \rightarrow \text{Context Adjustment} \rightarrow \text{Alert}
\]

## 2. AQI Por Contaminante

Sí, el sistema calcula un valor AQI para cada contaminante soportado con datos válidos.

Los contaminantes soportados son:

- `pm25`
- `pm10`
- `co`
- `no2`
- `o3`
- `so2`

Cada contaminante no usa la misma ventana temporal. El backend primero calcula una concentración representativa regulatoria:

- `pm25`: media de 24 horas
- `pm10`: media de 24 horas
- `co`: media de 8 horas
- `no2`: último valor de 1 hora
- `o3`: se compara la ventana 8h con la 1h según las reglas EPA
- `so2`: se compara 1h con 24h según reglas EPA

## 3. Fórmula Del Subíndice AQI

Una vez obtenida la concentración representativa \(C\), el subíndice AQI se calcula por interpolación lineal usando el breakpoint normativo que contiene ese valor.

La fórmula usada es:

\[
I = \left(\frac{I_{hi} - I_{lo}}{C_{hi} - C_{lo}}\right)(C - C_{lo}) + I_{lo}
\]

Donde:

- \(C\): concentración observada o representativa
- \(C_{lo}, C_{hi}\): límites inferior y superior del breakpoint de concentración
- \(I_{lo}, I_{hi}\): límites inferior y superior del tramo AQI asociado
- \(I\): subíndice AQI resultante

Luego el valor se redondea.

Ejemplo conceptual:

Si un contaminante cae en el tramo normativo `51–100`, su subíndice final también caerá en ese tramo, dependiendo de qué tan cerca esté del límite inferior o superior del breakpoint de concentración.

## 4. Categorías AQI Del Sistema

La clasificación implementada es:

- `0–50`: `good`
- `51–100`: `moderate`
- `101–150`: `unhealthy_sensitive_groups`
- `151–200`: `unhealthy`
- `201–300`: `very_unhealthy`
- `301–500`: `hazardous`

Por tanto, la escala real del sistema no es `0–200`, sino `0–500`.

## 5. Dominancia Y AQI Global

El sistema calcula primero un conjunto de subíndices:

\[
\text{Subindices} = \{AQI_{pm25}, AQI_{pm10}, AQI_{co}, AQI_{no2}, AQI_{o3}, AQI_{so2}\}
\]

Luego selecciona el máximo:

\[
AQI_{global} = \max(\text{Subindices})
\]

Y el contaminante dominante es:

\[
\text{Dominant Parameter} = \arg\max(\text{Subindices})
\]

Esto significa:

- el contaminante dominante es el que gobierna el AQI global;
- la categoría base del episodio se calcula a partir de ese máximo.

## 6. Persistencia

La persistencia no entra directamente desde todos los contaminantes como entradas separadas del motor difuso. Se deriva a partir de una historia corta del AQI global.

En el pipeline se reconstruyen varias corridas parciales recientes del AQI:

\[
H = [AQI_{t-2}, AQI_{t-1}, AQI_t]
\]

Con esa serie histórica se obtiene `persistence_score`.

La idea semántica es:

- si el AQI alto se mantiene en el tiempo, la persistencia sube;
- si el episodio es más puntual o menos estable, la persistencia baja.

La implementación concreta de persistencia está encapsulada en `compute_persistence_score(...)`, y su salida se maneja en una escala aproximada de `0–100`.

## 7. Concurrencia

La concurrencia sí usa los subíndices de todos los contaminantes, pero no como entradas independientes al motor difuso. Primero los agrega a una sola métrica.

La lógica implementada es:

\[
\text{threshold} = \max(25,\ 0.8 \cdot AQI_{dominante})
\]

Luego se excluye un contribuyente dominante y se evalúa la cercanía relativa de cada contaminante adicional:

\[
\text{closeness}_i =
\operatorname{clamp}
\left(
\frac{AQI_i - \text{threshold}}
{AQI_{dominante} - \text{threshold}},
0,1
\right)
\]

La puntuación final se obtiene como:

\[
\text{concurrence} =
\min\left(100,\ \frac{\sum_i \text{closeness}_i}{3}\cdot 100\right)
\]

donde la suma se hace sobre los contaminantes adicionales al dominante.

Interpretación:

- si los demás contaminantes quedan muy por debajo del dominante, la concurrencia permanece baja;
- si uno o dos contaminantes quedan muy cerca del dominante, la concurrencia sube de forma gradual;
- el índice satura en `100` cuando el episodio ya equivale a tres acompañantes fuertes, porque el motor difuso solo distingue `low`, `medium` y `high`.

## 8. Qué Recibe El Motor Difuso

El motor difuso Mamdani no recibe todos los contaminantes por separado.

Recibe exactamente tres entradas:

\[
(\text{AQI}_{global},\ \text{Persistence Score},\ \text{Concurrence Score})
\]

Es decir:

- entrada 1: AQI global, gobernado por el contaminante dominante;
- entrada 2: persistencia temporal del episodio;
- entrada 3: concurrencia multicontaminante agregada.

Esto es importante para defensa:

- los otros contaminantes sí influyen;
- pero lo hacen de forma indirecta, principalmente a través de `concurrence_score`.

## 9. Conjuntos Difusos De Entrada

### AQI

El sistema define términos lingüísticos:

- `good`
- `moderate`
- `unhealthy_sensitive_groups`
- `unhealthy`
- `very_unhealthy`
- `hazardous`

Cada término tiene una función de pertenencia trapezoidal o triangular.

Ejemplo conceptual:

\[
\mu_{moderate}(x) = \text{triangular}(x; 40, 75, 110)
\]

\[
\mu_{good}(x) = \text{trapezoidal}(x; 0, 0, 30, 60)
\]

### Concurrencia

Términos:

- `low`
- `medium`
- `high`

Ejemplo:

\[
\mu_{medium}(x) = \text{triangular}(x; 35, 55, 75)
\]

### Persistencia

Términos:

- `low`
- `medium`
- `high`

Ejemplo:

\[
\mu_{high}(x) = \text{trapezoidal}(x; 65, 80, 100, 100)
\]

## 10. Base De Reglas Difusas

La base principal cruza:

- 6 términos de AQI
- 3 términos de concurrencia
- 3 términos de persistencia

Total:

\[
6 \times 3 \times 3 = 54 \text{ reglas}
\]

Forma general de una regla:

\[
\text{IF AQI is } A \text{ AND Concurrence is } C \text{ AND Persistence is } P \text{ THEN Risk is } R
\]

La fuerza de activación de una regla se calcula con el mínimo:

\[
\alpha_r = \min(\mu_A,\ \mu_C,\ \mu_P)
\]

## 11. Agregación Y Defuzzificación

Cada regla activa recorta la función de pertenencia de salida correspondiente.

La agregación se hace por máximo:

\[
\mu_{agg}(x) = \max_r \left( \min(\alpha_r,\ \mu_{R_r}(x)) \right)
\]

Luego la salida continua se obtiene por centroide:

\[
\text{Score} = \frac{\sum_x x \cdot \mu_{agg}(x)}{\sum_x \mu_{agg}(x)}
\]

Después se traduce esa puntuación a una etiqueta final:

- `<= 50`: `good`
- `<= 100`: `moderate`
- `<= 150`: `unhealthy_sensitive_groups`
- `<= 200`: `unhealthy`
- `<= 300`: `very_unhealthy`
- `> 300`: `hazardous`

## 12. Ajuste Contextual Posterior

Después del motor difuso principal, el sistema aplica una modulación contextual usando:

- temperatura
- humedad

No recalcula el AQI. Ajusta la etiqueta y el score de riesgo.

La capa contextual se basa en:

- clasificación de temperatura: `low`, `normal`, `high`
- clasificación de humedad: `low`, `medium`, `high`
- una matriz contextual que decide si escalar o no

Si hay escalamiento:

\[
\text{Adjusted Label} = \text{next EPA label}
\]

y el score se reemplaza por el punto medio de esa categoría.

Además, el ajuste está restringido: si el episodio particulado no es suficientemente alto, no escala aunque haya contexto adverso.

## 13. Respuesta Corta Para Defensa

Si te preguntan:

### “¿Se calcula AQI para cada contaminante?”

Sí. El sistema calcula un subíndice AQI por contaminante usando concentración representativa y breakpoints EPA. Luego toma el máximo como AQI global.

### “¿La lógica difusa usa solo el dominante?”

Directamente usa el AQI global, que viene del dominante. Pero los demás contaminantes también influyen indirectamente a través del índice de concurrencia, que resume cuántos contaminantes están cerca del dominante.

### “¿Entonces por qué no entran todos los contaminantes al motor?”

Porque el diseño prioriza:

- interpretabilidad;
- trazabilidad;
- menor complejidad del sistema difuso;
- separación entre capa normativa AQI y capa interpretativa de riesgo.

## 14. Mensaje Técnico Preciso

Una formulación sólida para defensa sería:

> El sistema primero transforma cada contaminante en un subíndice AQI normativo. Luego selecciona el máximo como AQI global y contaminante dominante. La lógica difusa no procesa cada contaminante de manera independiente, sino que procesa el AQI global junto con dos variables auxiliares: persistencia temporal y concurrencia multicontaminante. Así se conserva la base normativa EPA y, al mismo tiempo, se incorpora una capa interpretativa más rica para el riesgo final.
