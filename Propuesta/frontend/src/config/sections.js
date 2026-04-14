export const SECTIONS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "traceability", label: "Trazabilidad" },
  { id: "explainability", label: "Explicabilidad" },
  { id: "evaluation", label: "Evaluación" },
];

export const SECTION_GUIDES = {
  dashboard: {
    title: "Cómo leer el dashboard",
    caption: "Esta vista resume el episodio actual y muestra la progresión desde la entrada hasta la salida del sistema.",
    items: [
      {
        title: "Qué mirar primero",
        body: "Empieza por el resumen de la corrida y las cuatro tarjetas superiores. Ahí se concentra el AQI global, la categoría base, el riesgo final y la cobertura del episodio.",
      },
      {
        title: "Cómo leer las gráficas",
        body: "La serie temporal muestra el comportamiento reciente del parámetro seleccionado. La gráfica de subíndices permite identificar el contaminante dominante. La comparación AQI base frente a salida final muestra si el motor difuso endureció o mantuvo la lectura inicial.",
      },
      {
        title: "Qué decisión permite",
        body: "Esta vista permite decidir si el episodio requiere una revisión más profunda en trazabilidad o explicabilidad y si la salida final es coherente con la fuente de datos y la cobertura disponible.",
      },
    ],
  },
  traceability: {
    title: "Cómo leer la trazabilidad",
    caption: "Esta vista expone el recorrido completo de la decisión y los elementos observados por el sistema.",
    items: [
      {
        title: "Ruta de decisión",
        body: "La ruta de decisión enumera las cinco capas del artefacto. Sirve para ubicar en qué etapa se consolidó el AQI, en cuál se activó la base difusa y si hubo ajuste contextual.",
      },
      {
        title: "Parámetros y sensores",
        body: "Los parámetros soportados y no soportados permiten identificar qué parte de la entrada fue usada en el cálculo normativo. La lista de sensores ayuda a verificar la estructura real de la estación consultada.",
      },
      {
        title: "Reglas y ajustes",
        body: "La lista de reglas activadas muestra qué reglas participaron y con qué fuerza. Los ajustes contextuales permiten justificar por qué la salida final se mantuvo o cambió frente a la clasificación base.",
      },
    ],
  },
  explainability: {
    title: "Cómo leer la explicabilidad",
    caption: "Esta vista describe el comportamiento interno del modelo difuso.",
    items: [
      {
        title: "Funciones de pertenencia",
        body: "Las curvas de AQI, concurrencia y persistencia muestran cómo el sistema representa lingüísticamente las entradas. Cada término activa una zona distinta del razonamiento.",
      },
      {
        title: "Reglas activadas",
        body: "La distribución de reglas activadas permite identificar qué fragmentos de la base principal participaron en la corrida. No todas las reglas se activan con la misma fuerza en cada episodio.",
      },
      {
        title: "Defuzzificación",
        body: "La gráfica de agregación y defuzzificación muestra la salida continua del sistema antes de traducirla a una etiqueta final. Esa puntuación explica por qué la salida se ubicó en una clase específica.",
      },
    ],
  },
  evaluation: {
    title: "Cómo leer la evaluación",
    caption: "Esta vista ayuda a contrastar la corrida actual con su historial y a revisar el impacto del ajuste contextual.",
    items: [
      {
        title: "Alerta final",
        body: "El bloque superior resume el mensaje operativo del sistema. Debe leerse junto con la categoría final y la cobertura disponible.",
      },
      {
        title: "Antes y después",
        body: "La comparación antes y después muestra si la capa contextual modificó la salida principal del motor difuso o si la mantuvo.",
      },
      {
        title: "Histórico",
        body: "El histórico local permite comparar episodios y verificar estabilidad entre corridas. Los filtros ayudan a recuperar estaciones, fechas o contaminantes dominantes específicos.",
      },
    ],
  },
};
