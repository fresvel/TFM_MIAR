# Hoja de Ruta para Sintetizar la Pregunta D2

**Pregunta de investigación:**  
¿Qué tipos de sistemas de inferencia basados en lógica difusa se emplean para la evaluación de la calidad del aire y del riesgo asociado, y cuáles son sus principales criterios de diseño?

---

## FASE 1 — Preparación Analítica (Base Cuantitativa)

### 1. Normalización de Multietiquetas

Descomponer columnas con separador `;`:

- `D2_Fuzzy_approach_type`
- `D2_Inference_purpose`
- `D2_Membership_functions`
- `D2_Interpretability_elements`

Acciones:
- Aplicar `split(";")`
- Aplicar `explode()`
- Limpiar espacios
- Agrupar categorías `Other:` en clases coherentes
  - Ejemplo:
    - `Other:TSK` -> `Sugeno/TSK`
    - `Other:Tsukamoto` -> `Tsukamoto`
    - `Other:Fuzzy_ARTMAP` -> `Híbrido / ML-Fuzzy`

Objetivo: trabajar con componentes reales y no combinaciones compuestas.

---

### 2. Estadística Descriptiva Básica

Calcular frecuencias para:

- Tipo de FIS
- Rol del fuzzy (`Central` / `Complementary`)
- Propósito de inferencia
- Base de reglas
- Funciones de pertenencia
- Método de defuzzificación
- Enfoque de modelado de riesgo
- Elementos de interpretabilidad

Producto:
- Tabla de frecuencias ordenada
- Identificación de categorías dominantes

---

## FASE 2 — Producto Visual Estratégico

### Figura 1: Distribución de Tipos de FIS

Gráfico de barras:
- Eje X: Tipo base de FIS
- Eje Y: Frecuencia

Responde directamente:  
¿Qué tipos de sistemas se emplean?

---

### Figura 2 (Opcional pero potente): Matriz de Co-ocurrencia

Ejemplos recomendados:

- Tipo FIS × Propósito
- Tipo FIS × Defuzzificación
- Tipo FIS × Membership Functions

Representación sugerida:
- Heatmap o tabla cruzada

Permite identificar patrones como:
- `Mamdani` ↔ `Centroid`
- `Sugeno` ↔ `Weighted_Average`
- `ANFIS` ↔ `Adaptive_MF`

---

## FASE 3 — Identificación de Patrones de Diseño

Transformar variables en decisiones de ingeniería:

### Decisión 1 — Rol del fuzzy
- ¿Es núcleo decisional o componente auxiliar?

### Decisión 2 — Objetivo de inferencia
- Clasificación AQI
- Estimación AQI
- Predicción de contaminantes
- Alertas de riesgo
- Optimización

### Decisión 3 — Definición de reglas
- Tabla explícita
- Adaptativa
- Basada en ecuaciones

### Decisión 4 — Tipo de Membership Functions
- Triangular / Trapezoidal
- Gaussian
- Adaptativas

### Decisión 5 — Método de defuzzificación
- Centroid
- Weighted Average
- No reportado (`NR`)

### Decisión 6 — Modelado de riesgo
- Umbrales AQI
- Enfoque predictivo
- Escalas propias

### Decisión 7 — Elementos de interpretabilidad
- Transparencia de reglas
- MF plots
- Tablas AQI
- Superficies difusas
- No reportado

---

## FASE 4 — Construcción de Perfiles de Diseño

Crear perfiles por tipo de FIS.

Ejemplo estructural:

**Perfil Mamdani**
- Rol dominante
- Propósito principal
- MF típicas
- Base de reglas
- Defuzzificación
- Enfoque de riesgo
- Elementos de interpretabilidad

Repetir para:
- Sugeno/TSK
- ANFIS
- Híbridos
- Otros relevantes

Producto:
- Tabla compacta `Tipo FIS -> Configuración típica`

---

## FASE 5 — Redacción de Resultados

Estructura recomendada de la sección:

### 1. Introducción breve
Contextualiza qué se analiza.

### 2. Subapartado A — Tipos de sistemas empleados
- Distribución
- Predominancia
- Figura 1

### 3. Subapartado B — Criterios de diseño
- Patrones observados
- Decisiones de ingeniería
- Figura 2 o tabla de perfiles

### 4. Síntesis final (2–3 párrafos integradores)
Relacionar:
- Tipo de FIS
- Configuración técnica
- Estrategia de modelado de riesgo
- Nivel de interpretabilidad

---

## Principio Metodológico Clave

La narrativa debe:
- Interpretar patrones
- No listar categorías
- No repetir tablas
- No saturar con referencias

Las tablas y figuras contienen la evidencia.  
El texto contiene la interpretación configuracional.
