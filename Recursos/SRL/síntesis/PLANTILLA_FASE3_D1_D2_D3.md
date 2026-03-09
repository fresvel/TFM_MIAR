# Fase 3 (D1, D2, D3) - Plantilla Rellenada v1

## Base de trabajo
- Dataset analizado: `Recursos/SRL/síntesis/python/assets/sintesis/dataset.csv`
- Tamaño del corpus: `n=19` estudios incluidos
- Regla usada: todos los resultados reportan `k/n` y `%`
- Trazabilidad: validada con `Evidence_D1_pages`, `Evidence_D2_pages`, `Evidence_D3_pages` (19/19 con contenido)
- Pasada fina aplicada: normalización de sinónimos y variantes (`tVOC/VOC/VOCs (TVOC)` -> `TVOC`, familias `ANFIS`/`Mamdani`, consolidación de etiquetas `Other:*` para análisis comparativo)

## Convenciones
- `k`: número de estudios que cumplen la condición.
- `n`: total de estudios evaluados para esa condición.
- `%`: `(k/n)*100`.
- `NR`: no reportado.

---

## Directriz D1: Datos y Variables

### Objetivo analítico
Caracterizar qué entradas ambientales/contaminantes se usan, cómo se estructuran temporalmente y qué nivel de completitud presentan los campos de datos y preprocesamiento.

### Campos usados
- `D1_Pollutants_inputs`
- `D1_Env_variables_inputs`
- `D1_Target_output`
- `D1_Data_source_type`
- `D1_Sampling_frequency_values`
- `D1_Time_window_values`
- `D1_Preprocessing`
- `Evidence_D1_pages`

### Tabla D1-A. Frecuencia de variables/contaminantes
| Variable / Contaminante | k | n | % | Observación |
|---|---:|---:|---:|---|
| CO | 9 | 19 | 47.4 | Co-ocurre con PM2.5, CO2 y otros gases en estudios multi-contaminante. |
| PM2.5 | 8 | 19 | 42.1 | Presencia alta tanto en monitoreo como en predicción. |
| CO2 | 6 | 19 | 31.6 | Frecuente en escenarios indoor y de confort/aire interior. |
| PM10 | 5 | 19 | 26.3 | Reporte recurrente en estudios con enfoque IAQ/AQI. |
| SO2 | 4 | 19 | 21.1 | Menor frecuencia relativa, pero presente en estudios de gases criterio. |

### Tabla D1-B. Configuración temporal y fuente de datos
| Dimensión | Categoría | k | n | % | Nota de heterogeneidad |
|---|---|---:|---:|---:|---|
| Fuente de datos | Direct_Sensors | 13 | 19 | 68.4 | Predominio de adquisición directa en campo/plataforma. |
| Fuente de datos | Hybrid_Sensors+Datasets | 5 | 19 | 26.3 | Integración de sensores con datasets históricos o externos. |
| Frecuencia de muestreo | NR o sin intervalo explícito | 6 | 19 | 31.6 | Alta variabilidad de reporte temporal. |
| Frecuencia de muestreo | Intervalos en minutos (explícitos) | 4 | 19 | 21.1 | Coexiste con configuraciones en segundos/horas y streaming. |
| Ventana temporal | NR / no delimitada | 4 | 19 | 21.1 | Parte del corpus no explicita horizonte temporal comparable. |
| Ventana temporal | Experimentos/sesiones cortas | 5 | 19 | 26.3 | Convivencia con periodos mensuales y multianuales. |
| Preprocesamiento | Reportado | 17 | 19 | 89.5 | Cobertura alta, aunque con estrategias no homogéneas. |
| Preprocesamiento | NR | 2 | 19 | 10.5 | Casos con información insuficiente para comparación fina. |

### Trazabilidad mínima D1
| Article_ID | Campo | Valor resumido | Evidence_D1_pages |
|---|---|---|---|
| A001 | `D1_Pollutants_inputs` | CO2; SO2; NO2 | p.4-p.6; p.20-p.25 |
| A136 | `D1_Sampling_frequency_values` | 1(min) | p.1; p.5; p.8-p.9 |
| A178 | `D1_Pollutants_inputs` | Benzene (C6H6); SO2; PM2.5; PM10 | p.7-p.10; p.16 |

### Redacción base D1
En D1, los contaminantes con mayor presencia fueron **CO** (`9/19`, `47.4%`) y **PM2.5** (`8/19`, `42.1%`), seguidos por **CO2** (`6/19`, `31.6%`) y **PM10** (`5/19`, `26.3%`).  
La fuente de datos predominante fue **Direct_Sensors** (`13/19`, `68.4%`), con presencia adicional de esquemas híbridos (`5/19`, `26.3%`).  
En la dimensión temporal se observa heterogeneidad: coexistencia de intervalos en segundos/minutos/horas con reportes sin intervalo explícito (`6/19`, `31.6%`), además de ventanas de observación cortas y periodos mensuales/multianuales.  
El preprocesamiento fue reportado en `17/19` estudios (`89.5%`), con `2/19` casos en `NR`, por lo que la comparación debe explicitar denominadores por variable.

---

## Directriz D2: Enfoque de Lógica Difusa

### Objetivo analítico
Describir el diseño del componente difuso (tipo de enfoque, rol, reglas, membresías, defuzzificación y optimización) y su completitud de reporte.

### Campos usados
- `D2_Fuzzy_approach_type`
- `D2_Fuzzy_role`
- `D2_Rule_base_definition`
- `D2_Membership_functions`
- `D2_Defuzzification_method`
- `D2_Optimization_values`
- `D2_Model_size_values`
- `D2_Inference_purpose`
- `Evidence_D2_pages`

### Tabla D2-A. Enfoques y rol del módulo difuso
| Dimensión | Categoría | k | n | % | Observación |
|---|---|---:|---:|---:|---|
| Tipo de enfoque | Mamdani | 7 | 19 | 36.8 | Es el enfoque más recurrente del corpus. |
| Tipo de enfoque | ANFIS (familia) | 7 | 19 | 36.8 | Incluye ANFIS y variantes reportadas en el corpus. |
| Tipo de enfoque | Sugeno | 3 | 19 | 15.8 | Se combina con otros enfoques en varios estudios. |
| Rol del módulo difuso | Central | 18 | 19 | 94.7 | El componente difuso actúa como núcleo inferencial dominante. |

### Tabla D2-B. Completitud de diseño difuso
| Elemento de diseño | Reportado (k) | n_aplicable | % | NR/No reportado | Nota |
|---|---:|---:|---:|---:|---|
| Base de reglas | 19 | 19 | 100.0 | 0 | Cobertura completa, con mezcla de reglas explícitas y adaptativas. |
| Funciones de pertenencia | 19 | 19 | 100.0 | 0 | Reporte completo, pero con tipologías heterogéneas. |
| Defuzzificación | 11 | 19 | 57.9 | 8 | Es el punto de menor completitud relativa en D2. |
| Optimización | 12 | 19 | 63.2 | 7 | Presencia intermedia; combinación de NR y campos vacíos. |

### Trazabilidad mínima D2
| Article_ID | Campo | Valor resumido | Evidence_D2_pages |
|---|---|---|---|
| A001 | `D2_Fuzzy_approach_type` | Hybrid_Fuzzy | p.1; p.7-p.10; p.25-p.27; p.31-p.32 |
| A149 | `D2_Defuzzification_method` | Centroid | p.3-p.4; p.6 |
| A178 | `D2_Rule_base_definition` | Adaptive_Rule_Base | p.11-p.15 |

### Redacción base D2
En D2, los enfoques más frecuentes fueron **Mamdani** (`7/19`, `36.8%`) y **ANFIS (familia)** (`7/19`, `36.8%`), con presencia adicional de configuraciones Sugeno e híbridas.  
El rol del módulo difuso fue principalmente **Central** (`18/19`, `94.7%`).  
La completitud de reporte fue alta en base de reglas y funciones de pertenencia (`19/19`, `100%` en ambos), pero menor en defuzzificación (`11/19`, `57.9%`) y optimización (`12/19`, `63.2%`).  
Por ello, la comparación entre diseños difusos requiere explicitar los casos con `NR` antes de contrastar desempeño o configuración.

---

## Directriz D3: Plataforma y Operación

### Objetivo analítico
Caracterizar arquitectura, modo de procesamiento y componentes de implementación (comunicación, hardware, despliegue y visualización) en sistemas de monitoreo.

### Campos usados
- `D3_Platform_architecture`
- `D3_Processing_mode`
- `D3_Communication_and_tech`
- `D3_Hardware_and_sensors`
- `D3_Deployment_context`
- `D3_Visualization_alerting`
- `D3_Real_time_characteristics`
- `Evidence_D3_pages`

### Tabla D3-A. Arquitectura y modo de procesamiento
| Dimensión | Categoría | k | n | % | Nota |
|---|---|---:|---:|---:|---|
| Arquitectura | IoT_Edge_Cloud | 6 | 19 | 31.6 | Arquitectura más frecuente en el corpus. |
| Arquitectura | IoT_2Tier | 3 | 19 | 15.8 | Segunda arquitectura con mayor recurrencia. |
| Arquitectura | WSN_Pipeline | 2 | 19 | 10.5 | Presencia menor, con variantes específicas. |
| Modo de procesamiento | Near_Real_Time | 7 | 19 | 36.8 | Modo más reportado. |
| Modo de procesamiento | Real_Time_Edge | 5 | 19 | 26.3 | Alta presencia en despliegues IoT/edge. |
| Modo de procesamiento | Hybrid | 4 | 19 | 21.1 | Combinación de operación en línea y componentes offline. |

### Tabla D3-B. Implementación técnica y despliegue
| Dimensión | Evidencia dominante | k | n | % | Cobertura/NR |
|---|---|---:|---:|---:|---|
| Comunicación/tecnología | WiFi | 6 | 19 | 31.6 | Campo reportado en 17/19 (`89.5%`), NR en 2/19. |
| Comunicación/tecnología | Cloud_Server | 6 | 19 | 31.6 | Alta presencia junto con MATLAB y plataformas IoT. |
| Hardware/sensores | PM_Sensor | 10 | 19 | 52.6 | Hardware reportado en 18/19 (`94.7%`), NR en 1/19. |
| Hardware/sensores | TempHumidity_Sensor | 9 | 19 | 47.4 | Componente frecuente en monitoreo ambiental integral. |
| Contexto de despliegue | Indoor | 12 | 19 | 63.2 | Predominio de escenarios interiores. |
| Contexto de despliegue | Urban | 11 | 19 | 57.9 | Alta recurrencia en ambientes urbanos. |
| Visualización/alertas | Dashboard | 8 | 19 | 42.1 | Campo con cobertura 16/19 (`84.2%`), NR/vacío en 3/19. |

### Trazabilidad mínima D3
| Article_ID | Campo | Valor resumido | Evidence_D3_pages |
|---|---|---|---|
| A001 | `D3_Platform_architecture` | IoT_2Tier | p.10; p.20; p.28-p.30 |
| A135 | `D3_Processing_mode` | Near_Real_Time | p.3-p.4; p.9-p.11 |
| A178 | `D3_Communication_and_tech` | Bluetooth; Zigbee; WiFi; AWS_EC2; MATLAB | p.6-p.8; p.14-p.16 |

### Redacción base D3
En D3, la arquitectura más frecuente fue **IoT_Edge_Cloud** (`6/19`, `31.6%`), seguida por **IoT_2Tier** (`3/19`, `15.8%`).  
El modo de procesamiento predominante fue **Near_Real_Time** (`7/19`, `36.8%`), con presencia importante de **Real_Time_Edge** (`5/19`, `26.3%`); en conjunto, los modos de tiempo real o cuasi-tiempo real alcanzan `13/19` (`68.4%`).  
En implementación técnica, destacan **WiFi** y **Cloud_Server** (`6/19` cada uno), mientras que en hardware predominan **PM_Sensor** (`10/19`) y **TempHumidity_Sensor** (`9/19`).  
El despliegue se concentra en entornos **Indoor** (`12/19`) y **Urban** (`11/19`), con visualización por **Dashboard** en `8/19` estudios.

---

## Checklist de control (Fase 3)
- [x] D1 redactado con `k/n` y `%` en hallazgos principales.
- [x] D2 redactado con cobertura de completitud por componente difuso.
- [x] D3 redactado con arquitectura, operación y despliegue.
- [x] Trazabilidad mínima consignada con `Evidence_*_pages`.
- [x] Distinción explícita de `NR` en campos críticos.
- [ ] Validar con revisión manual final de normalización semántica (sinónimos y etiquetas `Other:`) antes de pasar al informe.
