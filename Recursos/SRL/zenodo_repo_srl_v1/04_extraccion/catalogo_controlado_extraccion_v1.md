# Catalogo Controlado de Extraccion (v1)

## Reglas generales
- `NR`: No reportado en el articulo.
- `NA`: No aplica al estudio.
- `Other:<texto>`: cuando el valor no encaja en el catalogo. `Other` sin detalle no es valido.
- Campos multivalor: separar con `; ` (punto y coma + espacio).
- Evidencia de pagina: formato `p.X` o `p.X-p.Y`; multivalor con `; `.
- Consistencia: usar exactamente los tokens definidos abajo.

## Campos categoricos y valores permitidos

### `D1_Data_source_type`
- `Direct_Sensors`
- `Public_Datasets`
- `Hybrid_Sensors+Datasets`
- `Simulated_Data`
- `Other:<texto>`
- `NR`
- `NA`

### `D1_Time_characteristics`
- `Real_Time`
- `Near_Real_Time`
- `Offline_Batch`
- `Hybrid`
- `Other:<texto>`
- `NR`
- `NA`

### `D1_Preprocessing` (multivalor)
- `Calibration`
- `Missing_Imputation`
- `Cleaning`
- `Feature_Engineering`
- `Synchronization`
- `Classification`
- `MapReduce`
- `Filtering`
- `Normalization`
- `Other:<texto>`
- `NR`
- `NA`

### `D1_Pollutants_inputs` (multivalor)
- Usar contaminantes en formato canónico (ej.: `PM2.5`, `PM10`, `CO2`, `CO`, `NO2`, `SO2`, `O3`, `NH3`, `CH4`, `TVOC`).
- Normalización obligatoria de VOC:
  - `VOC` -> `TVOC`
  - `tVOC` -> `TVOC`
  - `VOCs (TVOC)` -> `TVOC`
- Normalización obligatoria de PM (formato/semántica):
  - `PM_2.5`, `PM 2.5`, `PM25` -> `PM2.5`
  - `PM_10`, `PM 10` -> `PM10`
  - `PM_Sensor (airborne particles)` -> `PM`
- Mantener variables de material particulado específicas (`PM2.5`, `PM10`) separadas de categorías generales (`PM`).
- Si el estudio solo reporta conteo/tamaño de partícula no equivalente directo a PM2.5/PM10, conservar descriptor específico (ej.: `Particle_Count_0.5um`).
- `Other:<texto>` cuando no encaje en el catálogo.
- `NR`
- `NA`

### `D1_Env_variables_inputs` (multivalor)
- Usar variables ambientales en formato canónico: `Temperature`, `Humidity`, `Air_Pressure`, `Wind`, `UV`.
- Normalización obligatoria:
  - `Relative_Humidity` -> `Humidity`
  - `Air_pressure` -> `Air_Pressure`
  - `Temperature (recorded_not_used_for_FIAQI)` -> `Temperature`
  - `NR (...)` -> `NR`
- Si el estudio reporta variables temporales/contextuales, usar `Other:<texto>` (ej.: `Other:Day_of_Week`, `Other:Hour_of_Day`).
- Campos multivalor con separador `; ` y orden canónico recomendado:
  - `Temperature; Humidity; Air_Pressure; Wind; UV`
- `NR`
- `NA`

### `D2_Fuzzy_approach_type`
- `Type1_FIS`
- `Type2_FIS`
- `Mamdani`
- `Sugeno`
- `ANFIS`
- `I-ANFIS`
- `ADFIST`
- `Hybrid_Fuzzy`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Fuzzy_role`
- `Central`
- `Complementary`
- `Comparative`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Inference_purpose` (multivalor)
- `AQI_Estimation`
- `AQI_Classification`
- `Pollutant_Prediction`
- `Risk_Alerting`
- `Route_Optimization`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Rule_base_definition`
- `Explicit_Rule_Table`
- `Equation_Based`
- `Adaptive_Rule_Base`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Membership_functions` (multivalor)
- `Linguistic_Labels`
- `Gaussian`
- `Adaptive_MF`
- `Implicit_MF`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Defuzzification_method`
- `Centroid`
- `Bisector`
- `MOM`
- `SOM`
- `LOM`
- `Weighted_Average`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Risk_modeling_approach`
- `AQI_Thresholds`
- `LoP_m-AQI`
- `Prediction_Based_Risk`
- `Other:<texto>`
- `NR`
- `NA`

### `D2_Interpretability_elements` (multivalor)
- `Rule_Transparency`
- `MF_Plots`
- `AQI_Mapping_Table`
- `SOM_Visualization`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Platform_architecture`
- `IoT_2Tier`
- `WSN_Pipeline`
- `IoT_Fog_Layered`
- `IoT_Edge_Cloud`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Processing_mode`
- `Real_Time_Edge`
- `Real_Time_FogCloud`
- `Near_Real_Time`
- `Offline_Analytics`
- `Hybrid`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Communication_and_tech` (multivalor)
- `WiFi`
- `Zigbee`
- `Bluetooth`
- `I2C`
- `Cloud_Server`
- `HDFS_MapReduce`
- `Google_Map`
- `Google_Sheets`
- `AWS_EC2`
- `MQTT`
- `MATLAB`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Visualization_alerting` (multivalor)
- `Local_Display`
- `Dashboard`
- `Map_Visualization`
- `Alarm_Module`
- `Medical_Alert`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Deployment_context` (multivalor)
- `Indoor`
- `Outdoor`
- `Indoor_Outdoor`
- `Urban`
- `Residential`
- `Campus`
- `Industrial`
- `Lab_Simulation`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Hardware_and_sensors` (multivalor)
- `CO_Sensor`
- `PM_Sensor`
- `TempHumidity_Sensor`
- `MCU_NodeMCU`
- `MCU_Arduino`
- `SBC_RaspberryPi`
- `RTC_Module`
- `Alarm_Module`
- `Other:<texto>`
- `NR`
- `NA`

### `D3_Real_time_characteristics` (multivalor)
- `Continuous_Loop`
- `Interval_Sampling`
- `Streaming_Upload`
- `Threshold_Alerting`
- `Temporal_Delay_Evaluated`
- `Other:<texto>`
- `NR`
- `NA`

### `Eval_Metrics_reported` (multivalor)
- `Accuracy`
- `RMSE`
- `MAE`
- `MAPE`
- `R2`
- `COD`
- `Precision`
- `Recall`
- `F1`
- `AUC`
- `Throughput`
- `Delivery_Ratio`
- `Temporal_Delay`
- `Reliability`
- `Stability_AAS`
- `Other:<texto>`
- `NR`
- `NA`

### `Sensitivity_set`
- `HIGH_MED`
- `ALL_ONLY`

### `QA_Quality_band`
- `Alta`
- `Media`
- `Baja`


## Campos de valores reportados (formato estructurado)

### `Eval_Reported_values`
- Formato: `metrica=valor(unidad)`
- Multivalor: separar con `; `
- Ejemplo: `Accuracy=98.9(%); RMSE=1.2(ppb)`
- Si no reporta: `NR`

### `Eval_AQI_class_labels` (multivalor)
- Etiquetas de clase AQI/IAQ reportadas explícitamente por el estudio.
- Formato canónico recomendado: `Good; Moderate; Sensitive; Unhealthy; Harmful; Hazardous`.
- Si el estudio usa abreviaturas (`G`, `M`, `U`, `VU`, `D`), normalizar a:
  - `G` -> `Good`
  - `M` -> `Moderate`
  - `U` -> `Unhealthy`
  - `VU` -> `Very_Unhealthy`
  - `D` -> `Dangerous`
- Fuente preferente: definición de clases en el modelo (`D2_Model_size_values`); respaldo en umbrales explícitos (`D1_Reported_input_values`).
- Si no reporta etiquetas explícitas: `NR`.

### `Eval_AQI_class_count`
- Número total de clases AQI/IAQ reportadas por el estudio.
- Formato: entero positivo (`5`, `6`, ...).
- Si no está reportado, pero existen etiquetas en `Eval_AQI_class_labels`, usar el conteo de etiquetas.
- Si no hay evidencia suficiente: `NR`.

### `Eval_Comparator_values`
- Formato: `modelo:metrica=valor(unidad)`
- Multivalor/modelos: separar con ` | `
- Ejemplo: `Baseline:RMSE=2.0(ppb) | SVM:RMSE=1.8(ppb)`
- Si no hay comparador: `NR`

### `Eval_Improvement_reported`
- Formato preferente: `metrica_reduction=valor(%)` o descripcion breve controlada
- Ejemplo: `RMSE_reduction=35(%)`
- Si no reporta mejora cuantificada: `NR`

### `Evidence_Eval_values_pages`
- Paginas exactas que sustentan los valores numericos
- Formato: `p.X` o `p.X-p.Y`; multivalor con `; `


## Campos de valores reportados adicionales (D1-D3 y diseno experimental)

### `D1_Reported_input_values`
- Formato: `variable=valor(unidad)` o `variable=min-max(unidad)`
- Multivalor: separar con `; `
- Si no reporta: `NR`

### `D1_Sampling_frequency_values`
- Frecuencia/tasa de muestreo explicita (`Hz`, `s`, `min`, `h`)
- Si solo hay descripcion cualitativa: texto breve controlado
- Si no reporta: `NR`

### `D1_Time_window_values`
- Ventana temporal de captura/prueba (`N`, duracion, periodo, horizon`)
- Multivalor: separar con `; `
- Si no reporta: `NR`

### `D2_Model_size_values`
- Parametros estructurales del FIS (`inputs`, `outputs`, `rules`, `MFs`, `layers`)
- Formato: `parametro=valor`
- Multivalor: `; `
- Si no reporta: `NR`

### `D2_Optimization_values`
- Parametros de optimizacion (`iteraciones`, `poblacion`, `mutation`, `crossover`, etc.)
- Formato: `parametro=valor`
- Multivalor: `; `
- Si no aplica: `NA`; si no reporta: `NR`

### `D3_Operational_values`
- Valores operativos de plataforma (`peso`, `velocidad`, `autonomia`, `latencia`, etc.)
- Formato: `parametro=valor(unidad)`
- Multivalor: `; `
- Si no reporta: `NR`

### `D3_Communication_values`
- Valores de comunicacion (`alcance`, `intervalo_tx`, `bandwidth`, etc.)
- Formato: `parametro=valor(unidad)`
- Multivalor: `; `
- Si no reporta: `NR`

### `Eval_Dataset_size_values`
- Tamano de datos / muestras / escenarios (`n`, instancias, registros)
- Formato: `dataset=n`
- Multivalor: `; `
- Si no reporta: `NR`

### `Eval_Data_split_values`
- Particion experimental (`train/val/test`, `holdout`, `k-fold`)
- Formato: `regla=valor`
- Si no aplica: `NA`; si no reporta: `NR`

### `Eval_Experiment_count_values`
- Numero de experimentos/escenarios/modelos comparados
- Formato: `item=valor`
- Multivalor: `; `
- Si no reporta: `NR`

### `Evidence_D1_values_pages`, `Evidence_D2_values_pages`, `Evidence_D3_values_pages`
- Paginas exactas que sustentan los valores numericos de cada bloque
- Formato: `p.X` o `p.X-p.Y`; multivalor con `; `


## Nota de version (depuracion de matriz)
- Se adopta una matriz nucleo para extraccion alineada a D1-D3 y sintesis de resultados.
- Campos removidos por redundancia/superficialidad en la matriz activa:
  - `D1_Time_characteristics`
  - `D2_Inference_design_summary`
  - `D3_Operational_values`
  - `D3_Communication_values`
  - `Eval_Experiment_count_values`
  - `Evidence_D1_values_pages`
  - `Evidence_D2_values_pages`
  - `Evidence_D3_values_pages`
  - `Evidence_Eval_values_pages`
- Respaldo completo previo: `archive/2026-02-15_auxiliares/articles_data_extraction_full_backup.csv`.
