Perfecto. Aquí tienes una plantilla detallada de redacción para Fase 3 (D1, D2, D3), enfocada en
  qué analizar y cómo analizarlo, sin adelantarse a la síntesis global.

  Reglas base para las 3 directrices

  1. Cada afirmación debe llevar denominador explícito: k/n y %.
  2. Si hay faltantes, reportar NR y usar n_aplicable cuando corresponda.
  3. Distinguir siempre: “no reportado” vs “no aplica”.
  4. Cerrar cada directriz con hallazgos descriptivos, no conclusiones globales.
  5. Mantener trazabilidad: Article_ID + campos Evidence_*_pages.

  Plantilla D1 (Datos y Variables)

  1. Objetivo de análisis: caracterizar qué se mide, con qué datos y bajo qué esquema temporal.
  2. Campos a usar: D1_Pollutants_inputs, D1_Env_variables_inputs, D1_Target_output,
     D1_Data_source_type, D1_Sampling_frequency_values, D1_Time_window_values, D1_Preprocessing,
     Evidence_D1_pages.
  3. Qué analizar:
      - Presencia de contaminantes por estudio (admitiendo múltiples por artículo).
      - Variables ambientales más usadas.
      - Tipo de salida objetivo (clasificación, predicción, índice, etc.).
      - Fuentes de datos (sensores, dataset público, híbrido).
      - Frecuencia de muestreo y ventana temporal (rangos, heterogeneidad).
      - Técnicas de preprocesamiento reportadas.
  4. Cómo analizar:
      - Normalizar etiquetas (sinónimos, mayúsculas/minúsculas, unidades).
      - Separar listas múltiples por artículo y contar presencia por estudio.
      - Reportar top variables con k/n y %.
      - Construir tabla de heterogeneidad temporal (frecuencia/ventana).
      - Marcar campos con alto NR y su impacto en comparabilidad.
  5. Redacción sugerida:
      - “En D1, los contaminantes más reportados fueron [X] (k/n, %), seguidos de [Y] (k/n, %).”
      - “Las variables ambientales predominantes fueron [A] y [B], observadas en k/n estudios.”
      - “La adquisición de datos presenta heterogeneidad en frecuencia (rango) y ventana (rango), lo
        que limita comparaciones directas.”
      - “El preprocesamiento se reporta en k/n; en m/n casos se observa NR.”

  Plantilla D2 (Enfoque de Lógica Difusa)

  1. Objetivo de análisis: describir cómo se implementa el componente difuso y su función en el
     sistema.
  2. Campos a usar: D2_Fuzzy_approach_type, D2_Fuzzy_role, D2_Rule_base_definition,
     D2_Membership_functions, D2_Defuzzification_method, D2_Optimization_values,
     D2_Model_size_values, D2_Inference_purpose, Evidence_D2_pages.
  3. Qué analizar:
      - Tipos de enfoque difuso (Mamdani, ANFIS, Sugeno, híbridos).
      - Rol del módulo difuso (núcleo, apoyo, post-proceso).
      - Nivel de detalle en reglas y funciones de pertenencia.
      - Métodos de defuzzificación y su frecuencia.
      - Uso de optimización (sí/no, tipo).
  4. Cómo analizar:
      - Agrupar enfoques en taxonomía corta y consistente.
      - Reportar cobertura de documentación por componente (reglas, membresía, defuzzificación).
      - Identificar combinaciones frecuentes (p. ej., enfoque + optimización).
      - Separar patrones robustos (alto reporte) de patrones sensibles (alto NR).
  5. Redacción sugerida:
      - “Predomina el enfoque [X] (k/n), seguido por [Y] (k/n).”
      - “El rol del módulo difuso es principalmente [rol] en k/n estudios.”
      - “La base de reglas y funciones de pertenencia se documentan en k/n y k2/n; la
        defuzzificación muestra menor completitud (k3/n).”
      - “La optimización aparece en k/n, con métodos [lista resumida].”

  Plantilla D3 (Plataforma y Tiempo Real)

  1. Objetivo de análisis: describir arquitectura, operación y despliegue de los sistemas.
  2. Campos a usar: D3_Platform_architecture, D3_Processing_mode, D3_Communication_and_tech,
     D3_Hardware_and_sensors, D3_Deployment_context, D3_Visualization_alerting,
     D3_Real_time_characteristics, Evidence_D3_pages.
  3. Qué analizar:
      - Arquitecturas predominantes (IoT/Edge/Cloud/2-tier/WSN, etc.).
      - Modos de procesamiento (real-time, near-real-time, batch).
      - Tecnologías de comunicación y hardware usado.
      - Contextos de despliegue (indoor, urbano, laboratorio, etc.).
      - Capacidades de visualización/alerta.
  4. Cómo analizar:
      - Homologar nombres de arquitectura y procesamiento.
      - Cruzar arquitectura vs modo de procesamiento.
      - Reportar qué tan frecuente es operación en tiempo real declarada.
      - Señalar vacíos técnicos recurrentes por NR.
  5. Redacción sugerida:
      - “Las arquitecturas más frecuentes fueron [X] (k/n) y [Y] (k2/n).”
      - “El procesamiento se reporta principalmente como [modo] (k/n), con [modo2] en k2/n.”
      - “La comunicación/hardware se describe en k/n; los contextos de despliegue más recurrentes
        son [A] y [B].”
      - “La evidencia sugiere predominio de implementaciones operativas con distinta granularidad de
        reporte técnico.”

  Micro-estructura recomendada por directriz (para escribir rápido)

  1. Párrafo 1: alcance y variables analizadas.
  2. Párrafo 2: patrones dominantes (k/n, %).
  3. Párrafo 3: heterogeneidad y NR.
  4. Párrafo 4: implicación metodológica local de la directriz (sin cerrar RQ global).

  Si quieres, en el siguiente paso te preparo esto mismo como plantilla rellenable (.md) con campos
  [completar] y tablas listas para copiar al informe.
