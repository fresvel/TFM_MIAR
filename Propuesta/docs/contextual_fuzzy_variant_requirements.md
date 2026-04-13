# Variante contextual difusa

Este documento resume los requisitos para implementar una variante alternativa de la capa contextual actual, de modo que pueda compararse el enfoque crisp existente frente a una segunda versión difusa.

## Objetivo

Construir una variante experimental en la que `temperature` y `humidity` dejen de evaluarse con cortes duros y pasen a una inferencia difusa propia, manteniendo comparable la salida final respecto del prototipo actual.

## Alcance mínimo

- conservar la capa principal Mamdani sin cambios funcionales;
- añadir una segunda implementación de la capa contextual;
- permitir ejecutar y comparar ambas variantes con el mismo episodio;
- exponer trazabilidad y explicabilidad de ambas;
- documentar diferencias de salida y de activación de reglas.

## Requisitos de backend

- definir funciones de pertenencia para `temperature`:
  - `low`
  - `normal`
  - `high`
- definir funciones de pertenencia para `humidity`:
  - `low`
  - `medium`
  - `high`
- decidir el tipo de salida contextual:
  - escalado discreto `0/1`, o
  - score contextual continuo
- implementar una base contextual difusa de `3 × 3 = 9` reglas;
- agregar un motor de inferencia contextual separado o reutilizar el patrón Mamdani existente;
- preservar el guardarraíl particulado o justificar su rediseño;
- exponer en API:
  - entradas contextuales reales,
  - pertenencias activas,
  - reglas contextuales activadas,
  - agregación contextual,
  - score o escalado contextual,
  - decisión final aplicada.

## Requisitos de frontend

- añadir selector de variante contextual:
  - `crisp`
  - `fuzzy`
- visualizar para la variante difusa:
  - curvas de pertenencia de temperatura;
  - curvas de pertenencia de humedad;
  - reglas activadas y fuerza;
  - agregación y salida contextual;
  - comparación antes/después sobre la salida principal;
- mantener una vista equivalente para la variante crisp actual;
- incluir una comparación directa `crisp vs fuzzy` en la pestaña de evaluación.

## Requisitos de comparación

- ejecutar ambos modos con los mismos escenarios `mock`;
- comparar al menos:
  - regla contextual seleccionada;
  - escalado aplicado;
  - label final;
  - score final;
  - estabilidad frente a pequeñas variaciones de temperatura y humedad;
- registrar resultados en un formato reproducible para el TFM.

## Requisitos de validación

- pruebas unitarias para funciones de pertenencia contextuales;
- pruebas unitarias para reglas contextuales difusas;
- pruebas del contrato API para la nueva traza contextual;
- validación visual de la UI en los dos modos;
- escenarios de borde alrededor de los umbrales actuales:
  - temperatura cercana a `10` y `30`;
  - humedad cercana a `40` y `70`.

## Criterio de decisión técnica

La variante difusa debería mantenerse solo si demuestra una mejora clara en al menos uno de estos puntos:

- transiciones más suaves y defendibles;
- mejor coherencia formal con la capa principal;
- mayor utilidad explicativa en la UI;
- menor arbitrariedad en torno a los cortes actuales.

Si no mejora de manera apreciable la interpretabilidad o la utilidad comparativa del artefacto, conviene mantener la capa contextual crisp actual por simplicidad y trazabilidad.
