 Propuesta
  La solución no debería basarse en un FIS que calcule “un AQI alternativo” desde cero. La propuesta
  más sólida para el TFM es un módulo híbrido con dos niveles:

  1. Un nivel determinista que calcule o consolide el estado de calidad del aire a partir de datos
     abiertos de monitoreo usando una referencia normativa trazable.
  2. Un nivel difuso, interpretable y auditable, que transforme ese estado en evaluación de riesgo y
     alertamiento operativo.

  Eso te resuelve un problema clave de la memoria: mantienes comparabilidad externa con un estándar
  conocido y, al mismo tiempo, justificas el aporte del módulo difuso como capa de apoyo a la
  decisión.

  Decisiones técnicas recomendadas

  - Fuente operativa principal: OpenAQ v3, no como índice ya calculado, sino como repositorio
    armonizado de mediciones y metadatos de estaciones. La propia documentación indica que ofrece
    datos históricos y cercanos a tiempo real, con unidades físicas y metadatos por sensor/
    ubicación. También deja una advertencia importante: el endpoint latest no garantiza cobertura
    completa por posibles llegadas fuera de orden. Para el módulo, conviene usar agregaciones
    horarias por sensor (/hours) y registrar cobertura.
  - Fuente de validación/referencia: EPA AQS/AirData cuando quieras una referencia regulatoria de
    alta trazabilidad. EPA distingue con claridad entre AirNow como dato preliminar en tiempo real y
    AQS/AirData como fuente regulatoria validada.
  - Fuente contextual complementaria: Open-Meteo Air Quality API solo como apoyo para contexto
    atmosférico o contraste con forecast, no como sustituto de la red de monitoreo. Sirve si quieres
    enriquecer temperatura, UV o comparar con un escenario de pronóstico.

  Arquitectura que te recomiendo

  - Capa 1. Ingesta: adaptador OpenAQ, consulta por ubicación/sensor/ventana temporal.
  - Capa 2. Estandarización: normalización de unidades, zona horaria, ventanas horarias, control de
    duplicados y faltantes.
  - Capa 3. Calidad de datos: porcentaje de cobertura, reglas de exclusión, trazabilidad de fuente,
    marca de datos insuficientes.
  - Capa 4. Núcleo AQI: cálculo de subíndices por contaminante y selección del valor dominante con
    breakpoints EPA.
  - Capa 5. Motor difuso: entrada con AQI/subíndices, persistencia temporal, mezcla de contaminantes
    y calidad/cobertura del dato.
  - Capa 6. Alertamiento: nivel lingüístico de riesgo, mensaje operativo y justificación de reglas
    activadas.
  - Capa 7. Exposición: dashboard/API para consulta, histórico y auditoría.

  Variables
  Para una primera versión realista, usaría:

  - Contaminantes: PM2.5, PM10, NO2, O3, CO, SO2, según disponibilidad real por estación.
  - Variables de contexto: temperatura y humedad si la fuente las trae; si no, quedan como
    opcionales.
  - Variables derivadas:
      - AQI_global
      - subindice_dominante
      - persistencia_3h o tendencia_corta
      - cobertura_dato
      - numero_de_contaminantes_disponibles

  Motor difuso
  Para esta memoria, la mejor decisión no es ANFIS como núcleo principal. Es Mamdani.
  Razón:

  - encaja mejor con tu criterio de auditabilidad,
  - permite explicar reglas en lenguaje natural,
  - se alinea con el cierre del nuevo estado del arte,
  - evita depender de entrenamiento intensivo para demostrar valor.

  Salida sugerida:

  - riesgo_bajo
  - riesgo_moderado
  - riesgo_alto
  - riesgo_muy_alto

  Reglas ejemplo:

  - si AQI_global es alto y persistencia es alta, entonces riesgo es muy alto;
  - si AQI_global es moderado pero PM2.5 y NO2 están simultáneamente elevados, entonces riesgo es
    alto;
  - si cobertura_dato es baja, entonces la salida debe incluir alerta con menor confianza o estado
    de precaución.

  Qué conviene escribir como aporte del TFM
  El aporte no sería “un nuevo AQI”. Sería esto:

  - un módulo reproducible basado en datos abiertos;
  - una capa difusa interpretable para evaluación de riesgo;
  - una lógica de alertamiento trazable;
  - un flujo auditable desde ingesta hasta salida.

  Validación
  La validación debería quedar así:

  - funcional: el pipeline corre completo;
  - lógica: la activación de reglas coincide con los escenarios esperados;
  - temporal: tiempo de respuesta por ciclo;
  - robustez: comportamiento con faltantes, cobertura baja y contaminantes ausentes;
  - comparativa: contraste entre AQI determinista y salida difusa;
  - reproducibilidad: misma entrada, misma salida, mismo registro de reglas.

  Punto crítico que debes fijar en la propuesta
  No usar AirNow como base principal del módulo si en la memoria lo vas a defender como fuente de
  evaluación estable. La documentación oficial dice que sus datos son preliminares y no deben usarse
  como base regulatoria. Para un TFM, eso sirve como fuente de visualización o contraste en tiempo
  real, pero no como base única de validación.

  Fuentes clave

  - OpenAQ API docs: https://docs.openaq.org/about/about
  - OpenAQ quick start y API key: https://docs.openaq.org/using-the-api/quick-start
  - OpenAQ measurements/hours: https://docs.openaq.org/resources/measurements
  - OpenAQ latest caveat: https://docs.openaq.org/resources/latest
  - EPA AirData basic information:
    https://www.epa.gov/outdoor-air-quality-data/airdata-basic-information
  - EPA AQI communication:
    https://www.epa.gov/wildfire-smoke-course/communicating-air-quality-conditions-air-quality-index
  - EPA AQS API: https://aqs.epa.gov/aqsweb/documents/ramltohtml.html
  - AirNow API disclaimer: https://docs.airnowapi.org/
  - WHO air quality guidelines:
    https://www.who.int/news-room/questions-and-answers/item/who-global-air-quality-guidelines
  - Open-Meteo Air Quality API: https://open-meteo.com/en/docs/air-quality-api
