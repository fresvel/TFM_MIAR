• Análisis consolidado para “Vacíos, limitaciones e implicaciones”

  Fuente usada:

  - Recursos/SRL/síntesis/dataset.csv
  - Informe/secciones/02_cuerpo/03_objetivos.tex
  - Recursos/Articulos/04.pdf
  - Recursos/Articulos/05.pdf
  - Recursos/Articulos/06.pdf
  - Recursos/Articulos/07.pdf
  - Recursos/Articulos/08.pdf

  ### 1) Qué muestran los 19 estudios (SLR) con tus columnas

  - Cobertura de fuente de datos (D1_Data_source_type): 13/19 sensores directos, 5/19 híbrido
    sensores+dataset, 1/19 solo datasets públicos.
  - Operación temporal (D3_Processing_mode): 13/19 reportan etiquetas de tiempo real/casi tiempo
    real/fog-cloud.
  - Limitaciones explícitas (Main_limitation_reported): 4/19 no reportan limitación clara.
  - Heterogeneidad de evaluación (Eval_Metrics_reported, cruda): Accuracy 8, RMSE 7, MAE 5, MAPE 5,
    R2 3, resto disperso.
  - Trazabilidad incompleta puntual:
      - D3_Synthesis_notes vacío en A028.
      - D1_Reported_input_values en NR en A028 y A084.

  ### 2) Patrones de brecha observados

  - Generalización/validación externa insuficiente: A009, A028, A084, A087, A144.
  - Cobertura de variables/contaminantes limitada: A009, A138, A142, A149.
  - Integración/despliegue operativo incompleto: A028, A135, A144.
  - Coste computacional o eficiencia de red: A135, A138, A178.
  - Restricciones hardware/sensor/calibración: A001, A087.
  - Degradación por horizonte predictivo: A157.
  - Dominio clínico sin cierre causal fuerte: A142, A149.

  ### 3) Evidencia puntual (representativa) con DOI y enfoque

  - A028 (10.1109/ICABME66883.2025.11211707): objetivo AQI prediction con datos públicos; limitación
    explícita: sin despliegue operacional y sin validación multicidad.
  - A135 (10.1016/j.iot.2022.100628): PM2.5 forecasting, métricas robustas; limitación: no
    integración completa del forecasting en portal online.
  - A144 (10.3390/s22031008): predicción IAQ indoor; limitación: alcance de despliegue limitado y
    necesidad de validación multi-sitio.
  - A084 (10.1016/j.envsoft.2025.106734): ajuste PM2.5 multiciudad; limitación: sensibilidad por
    ciudad y necesidad de validación adicional.
  - A114 (10.18494/SAM4661): clasificación+control en tiempo real; sin limitación explícita formal.
  - A009 (10.1109/ICIBT52874.2022.9807786): AQI class assignment; limitación: pocos contaminantes y
    desempeño mayormente a nivel de clase.
  - A178 (10.1080/0952813X.2020.1744197): IoT-Fog + ANFIS-DE; limitación: eficiencia de red e
    interacción humano-computador pendientes.

  ### 4) Contraste con PDF 04–08 (antecedentes extra)

  - 04.pdf: usa dataset abierto (Aachen/Kaggle), muestreo ~2 min, pero enfoque de clasificación
    sobre dataset y “future work” orientado a más datasets/sitios.
  - 05.pdf: monitoreo en tiempo real, pero declara explícitamente que no generó/analizó datasets
    para validación.
  - 06.pdf: IoT + Mamdani en tiempo real con sensores del sistema, sin evidencia clara de dataset
    público externo trazable.
  - 07.pdf: modelo en tiempo real, sin identificación trazable de dataset público (UCI/Kaggle/
    GitHub).
  - 08.pdf: sí reporta dataset+código en GitHub y validación cruzada, pero con limitación fuerte de
    generalización (despliegue de 33 nodos en un solo contexto) y necesidad de pilotos multi-ciudad.

  ### 5) Vacío principal que emerge (candidato)

  Falta una solución que combine simultáneamente:

  - datos abiertos trazables y reutilizables (idealmente actualizables),
  - operación en tiempo real con inferencia difusa en entorno urbano,
  - evaluación comparable y reproducible (métricas + protocolo + evidencia),
  - y validación con alcance más allá de un solo contexto local.

  ### 6) Objetivos actuales del TFM (para alinear propuesta)

  Desde Informe/secciones/02_cuerpo/03_objetivos.tex:

  - Objetivo general: desarrollar un módulo de monitoreo de calidad del aire para evaluación de
    riesgo y alertas con inferencia difusa y datos abiertos en entorno urbano.
  - Objetivos específicos:
      1. Caracterizar variables, enfoque difuso y arquitectura (SLR).
      2. Diseñar arquitectura funcional (flujo de datos + inferencia + alertamiento).
      3. Implementar módulo con datos abiertos y procesamiento ambiental.
      4. Validar con métricas y casos de prueba en escenarios urbanos.

  ### 7) Alineación directa del vacío con tus objetivos

  - OE1 ya identifica el hueco (fragmentación entre datos abiertos, tiempo real y comparabilidad).
  - OE2 y OE3 deberían cerrar el hueco técnico (pipeline único y trazable).
  - OE4 debe cerrar el hueco metodológico (validación comparable y robusta).

  Si te parece, siguiente paso te propongo 3 formulaciones de “vacío a llenar” (con diferente nivel
  de ambición) para que elijas una y la pasamos al texto final del apartado.

_--__-__-__-__-__-__-__-__-__-__-__-__-__-__-_
1.- Crear subtemas para estos elementos:

  - Generalización/validación externa insuficiente: A009, A028, A084, A087, A144.
  - Cobertura de variables/contaminantes limitada: A009, A138, A142, A149.
  - Integración/despliegue operativo incompleto: A028, A135, A144.
  - Coste computacional o eficiencia de red: A135, A138, A178.
  - Restricciones hardware/sensor/calibración: A001, A087.
  - Degradación por horizonte predictivo: A157.
  - Dominio clínico sin cierre causal fuerte: A142, A149.
  
2.- Explicar cada uno de esos subtemas a partir de las evidencias de:
- A028 (10.1109/ICABME66883.2025.11211707): objetivo AQI prediction con datos públicos; limitación
    explícita: sin despliegue operacional y sin validación multicidad.
  - A135 (10.1016/j.iot.2022.100628): PM2.5 forecasting, métricas robustas; limitación: no
    integración completa del forecasting en portal online.
  - A144 (10.3390/s22031008): predicción IAQ indoor; limitación: alcance de despliegue limitado y
    necesidad de validación multi-sitio.
  - A084 (10.1016/j.envsoft.2025.106734): ajuste PM2.5 multiciudad; limitación: sensibilidad por
    ciudad y necesidad de validación adicional.
  - A114 (10.18494/SAM4661): clasificación+control en tiempo real; sin limitación explícita formal.
  - A009 (10.1109/ICIBT52874.2022.9807786): AQI class assignment; limitación: pocos contaminantes y
    desempeño mayormente a nivel de clase.
  - A178 (10.1080/0952813X.2020.1744197): IoT-Fog + ANFIS-DE; limitación: eficiencia de red e
    interacción humano-computador pendientes.
- A028 (10.1109/ICABME66883.2025.11211707): objetivo AQI prediction con datos públicos; limitación
    explícita: sin despliegue operacional y sin validación multicidad.
  - A135 (10.1016/j.iot.2022.100628): PM2.5 forecasting, métricas robustas; limitación: no
    integración completa del forecasting en portal online.
  - A144 (10.3390/s22031008): predicción IAQ indoor; limitación: alcance de despliegue limitado y
    necesidad de validación multi-sitio.
  - A084 (10.1016/j.envsoft.2025.106734): ajuste PM2.5 multiciudad; limitación: sensibilidad por
    ciudad y necesidad de validación adicional.
  - A114 (10.18494/SAM4661): clasificación+control en tiempo real; sin limitación explícita formal.
  - A009 (10.1109/ICIBT52874.2022.9807786): AQI class assignment; limitación: pocos contaminantes y
    desempeño mayormente a nivel de clase.
  - A178 (10.1080/0952813X.2020.1744197): IoT-Fog + ANFIS-DE; limitación: eficiencia de red e
    interacción humano-computador pendientes.
    
3.- Contrastar cada uno de esos temas con:

  - 04.pdf: usa dataset abierto (Aachen/Kaggle), muestreo ~2 min, pero enfoque de clasificación
    sobre dataset y “future work” orientado a más datasets/sitios.
  - 05.pdf: monitoreo en tiempo real, pero declara explícitamente que no generó/analizó datasets
    para validación.
  - 06.pdf: IoT + Mamdani en tiempo real con sensores del sistema, sin evidencia clara de dataset
    público externo trazable.
  - 07.pdf: modelo en tiempo real, sin identificación trazable de dataset público (UCI/Kaggle/
    GitHub).
  - 08.pdf: sí reporta dataset+código en GitHub y validación cruzada, pero con limitación fuerte de
    generalización (despliegue de 33 nodos en un solo contexto) y necesidad de pilotos multi-ciudad.
    
4.- Agregar al análisis esto en donde aporte de los subtemas pasados o generar cierre con:

- Cobertura de fuente de datos (D1_Data_source_type): 13/19 sensores directos, 5/19 híbrido
    sensores+dataset, 1/19 solo datasets públicos.
  - Operación temporal (D3_Processing_mode): 13/19 reportan etiquetas de tiempo real/casi tiempo
    real/fog-cloud.
  - Limitaciones explícitas (Main_limitation_reported): 4/19 no reportan limitación clara.
  - Heterogeneidad de evaluación (Eval_Metrics_reported, cruda): Accuracy 8, RMSE 7, MAE 5, MAPE 5,
    R2 3, resto disperso.
  - Trazabilidad incompleta puntual:
      - D3_Synthesis_notes vacío en A028.
      - D1_Reported_input_values en NR en A028 y A084.

5.- Explicar el vacío principal que emerge, como ingeniería de requerimiento o requisitos del sistema:

  Falta una solución que combine simultáneamente:

  - datos abiertos trazables y reutilizables (idealmente actualizables),
  - operación en tiempo real con inferencia difusa en entorno urbano,
  - evaluación comparable y reproducible (métricas + protocolo + evidencia),
  - y validación con alcance más allá de un solo contexto local.
  
 Para cada uno de los subtemas de 1 me irás presentando los resultados de los pasos 2-4, una vez finalizado cerraremos 4 y pasaremos i\'oa 5. Deberás ir marcando lo que hemos solventado y lo que nos falta. Yo aprobaré y te iré dando directrices para trabajar. Empecemos
