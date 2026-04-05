# Trabajo futuro: extensión predictiva del artefacto

## Alcance

La incorporación de un modelo predictivo constituye una extensión natural del artefacto actual, pero amplía de forma significativa el alcance del TFM. El módulo implementado en esta etapa está centrado en la evaluación explicable del estado actual de la calidad del aire mediante una arquitectura híbrida compuesta por una capa normativa, una capa de variables auxiliares, una base difusa principal y una capa contextual. Añadir predicción implicaría abrir una nueva línea de trabajo orientada a series temporales, entrenamiento supervisado y validación prospectiva.

Por esa razón, esta idea se documenta como trabajo futuro y no como parte del alcance principal de la implementación actual.

## Enfoque híbrido propuesto

La extensión predictiva no consistiría en reemplazar el sistema actual, sino en reutilizarlo para generar variables expertas que enriquezcan un dataset supervisado.

La lógica sería esta:

1. Tomar los datos originales de la estación o del conjunto histórico.
2. Ejecutar el módulo actual sobre esos datos.
3. Obtener variables expertas derivadas.
4. Agregar esas variables al dataset.
5. Entrenar un modelo para predecir el estado futuro.

## Variables expertas derivadas

Las variables derivadas que podrían generarse a partir del artefacto actual incluyen:

- `AQI_base`
- `subindice_dominante`
- `concurrencia`
- `persistencia`
- `riesgo_difuso_actual`
- número de reglas activadas
- `cobertura`

## Sentido del enfoque

La idea es separar tres niveles de información:

- `datos crudos`: lo que mide la estación;
- `variables expertas`: lo que el sistema actual interpreta sobre ese estado;
- `modelo predictivo`: el componente que usa ambos conjuntos de variables para anticipar el comportamiento futuro.

Este enfoque es híbrido porque combina:

- información observada directamente en el entorno;
- conocimiento experto condensado por el sistema difuso;
- aprendizaje supervisado para anticipar estados futuros.

## Justificación conceptual

Las variables expertas pueden aportar valor porque resumen relaciones que no siempre quedan representadas con la misma claridad en las concentraciones crudas. Por ejemplo:

- `concurrencia` resume si varios contaminantes están presentes en niveles similares;
- `persistencia` resume la continuidad temporal del episodio;
- `AQI_base` resume la lectura normativa del estado actual;
- `riesgo_difuso_actual` resume una evaluación ya interpretada por el artefacto.

Estas variables podrían mejorar la capacidad predictiva respecto a un modelo entrenado únicamente con datos crudos.

## Ejemplo de diseño experimental

Supóngase un objetivo predictivo de categoría EPA futura a 6 horas.

### Modelo 1

Entradas:

- contaminantes actuales;
- temperatura;
- humedad;
- hora;
- día.

### Modelo 2

Entradas:

- todas las variables del modelo 1;
- `AQI_base`;
- `concurrencia`;
- `persistencia`;
- `riesgo_difuso_actual`.

Si el modelo 2 mejora frente al modelo 1, entonces podría sostenerse que el sistema difuso no solo sirve para clasificar el estado actual, sino también para producir variables de alto nivel útiles para predicción.

## Restricción metodológica principal

La etiqueta objetivo debe ser futura y observable.

Lo correcto sería:

- entradas en tiempo `t`;
- salida observada en `t+1`, `t+6` o `t+24`.

Lo que no conviene hacer es esto:

- entradas en tiempo `t`;
- salida del propio sistema en el mismo tiempo `t`.

Ese segundo caso produciría un modelo que solo imita la lógica actual del artefacto y no una predicción real del estado futuro.

## Interpretación correcta de las opciones

La opción predictiva básica sería:

- `A = predicción con datos crudos`

La opción híbrida sería:

- `C = predicción con datos crudos + variables expertas derivadas`

La opción híbrida resulta más potente si se implementa con una validación temporal correcta y con una comparación experimental explícita entre ambos enfoques.

## Recomendación para una futura implementación

Si se decide avanzar hacia predicción, la secuencia recomendada sería:

1. Definir un horizonte de predicción.
   - 1 hora
   - 6 horas
   - 24 horas
2. Definir la salida objetivo.
   - categoría EPA futura
   - riesgo futuro
3. Construir dos datasets.
   - dataset base
   - dataset base más variables difusas derivadas
4. Entrenar y comparar ambos enfoques.

## Valor potencial

Si esta línea futura se confirma experimentalmente, el artefacto podría evolucionar desde un sistema explicable de evaluación del estado actual hacia un sistema híbrido explicable y predictivo.
