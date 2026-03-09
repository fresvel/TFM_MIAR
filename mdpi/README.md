# Revisión de Redacción y Duplicidades - Sección Results (MDPI)

## Objetivo
Este proyecto consolida una revisión estructurada de la sección `Results` para identificar:
- redacción redundante,
- contenido innecesario (no responde a las preguntas de investigación),
- duplicidad entre tablas y figuras,
- recomendaciones de consolidación.

## Hallazgos Prioritarios
1. Hay contenido prescriptivo/de propuesta dentro de `Results` (no solo reporte de evidencia).
- Referencias: `3.- Results.tex:221`, `3.- Results.tex:301`, `3.- Results.tex:247`.
- Sugerencia: mover esas partes a `Discussion` (implicaciones/recomendaciones) y dejar en `Results` solo evidencia + interpretación directa.

2. Duplicación de introducciones/meta-texto en D3.
- Referencias: `3.- Results.tex:249`, `3.- Results.tex:254`, `3.- Results.tex:311`, `3.- Results.tex:316`.
- Sugerencia: dejar una sola apertura de subsección + una sola transición metodológica.

3. Repetición de ideas en perfil del corpus (PRISMA/retrieval/calidad).
- Referencias: `3.- Results.tex:5`, `3.- Results.tex:50`.
- Sugerencia: mantener números duros una sola vez (idealmente junto a PRISMA) y reducir el resto a interpretación.

4. Ambigüedad de redacción en deduplicación (puede parecer inconsistencia aritmética).
- Referencia: `3.- Results.tex:5`.
- Sugerencia: aclarar explícitamente “119 candidatos a duplicado detectados; 62 removidos; 57 conservados por priorización/falso positivo”.

## Duplicidad Tabla-Figura y qué conservar
1. D1 frecuencias.
- Tabla: `\input{.../d1_tabla_resumen_es.tex}`
- Figura frecuencia: `fig01_frecuencia_entradas.png`
- Recomendación: conservar tabla (precisión k/n/%) y mover la barra de frecuencia a anexo si necesitas recorte.

2. D1 relaciones por salida (dos pares barra+heatmap).
- Ambientales: `fig02_ambientales_vs_salida.png` + `fig07_relacion_ambiente_vs_salida.png`
- Contaminantes: `fig03_contaminantes_vs_salida.png` + `fig06_relacion_salida_vs_contaminantes.png`
- Recomendación: dejar un solo gráfico por par (ideal: heatmap) para evitar redundancia visual.

3. D2 distribución de tipos.
- Tabla principal D2 + figura de distribución simple.
- Recomendación: conservar tabla + coocurrencias; distribución simple puede ir a anexo.

4. D3 arquitectura/procesamiento.
- Tabla principal D3 + dos barras marginales + coocurrencia.
- Recomendación: conservar tabla + coocurrencia arquitectura-procesamiento; mover barras marginales si se requiere compactar.

5. Eval desempeño.
- Tabla resumen de valores + conjunto de boxplots.
- Recomendación: en cuerpo principal dejar tabla (valores exactos) y pasar boxplots a anexo, o mantener solo 1–2 métricas clave.

## Consistencia
- No se detectaron contradicciones obvias entre cifras narradas y tablas en los bloques revisados (D1, D2, D3, QA).
- Sí hay sobreexplicación repetitiva de la misma evidencia en varios bloques (sobre todo D3 y parte de D1/D2/Eval).

## Siguiente paso recomendado
Aplicar una versión depurada de `Results` siguiendo el checklist incluido en este proyecto.
