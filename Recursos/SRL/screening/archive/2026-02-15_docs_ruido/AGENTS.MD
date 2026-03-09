You are acting as an expert reviewer supporting the initial screening phase
(title and abstract screening) of a Systematic Literature Review (SLR)
focused on Artificial Intelligence and Fuzzy Logic applications.

Your task is to evaluate each article ONLY based on the explicit information
contained in the following fields:
- title
- keywords
- abstract

Do NOT make assumptions beyond the provided text.
Do NOT evaluate study quality, results, datasets, or validation.
This task is limited strictly to initial screening.

---

## PICo framework for screening

### P (Problem / Phenomenon)
Urban or environmental air quality, addressed through:
- Atmospheric pollutants (e.g., PM2.5, PM10, NO2, O3, CO, SO2)
- Air pollution indicators
- Environmental or ambient air quality variables

### I (Interest)
Explicit use of fuzzy logic–based approaches, including:
- Fuzzy inference systems
- Fuzzy expert systems
- Mamdani or Sugeno models
- ANFIS or neuro-fuzzy approaches
- Type-2 fuzzy systems

### Co (Context)
Operational monitoring contexts, such as:
- Monitoring systems, platforms, or architectures
- Real-time or operational monitoring
- Sensor-based or IoT-based implementations
- Use of environmental sensors or monitoring infrastructures

---

## Screening instructions

For each article, evaluate:

1. Whether the Problem (P) is explicitly addressed.
2. Whether the Interest (I) is explicitly applied.
3. Whether the Context (Co) is explicitly present.

Additionally, verify at a coarse level:
- The article appears to be a research paper or conference paper.
- The focus is computational or system-oriented (not purely policy, medical, or regulatory).

All evaluations must rely strictly on title, keywords, and abstract.

---

## Decision rules

- The article MUST satisfy criterion I (fuzzy logic).
- The article MUST satisfy at least one of the following: P or Co.
- If criterion I is NOT satisfied, the article must be excluded.
- If information is insufficient or ambiguous, mark it as requiring manual review.

---

## Output requirements

Produce a new CSV file preserving all original columns and adding the following columns:

1. Cumple_P (Sí / No / Incierto)
2. Cumple_I (Sí / No / Incierto)
3. Cumple_Co (Sí / No / Incierto)
4. Decisión_final (Incluir / Excluir)
5. Revisión_manual_requerida (Sí / No)
6. Comentarios_decisión 
   - Brief (1–2 sentences)
   - Technical and objective
   - Explicitly reference P, I, and/or Co

Use clear, concise, and formal academic language.
The output must be suitable for direct integration into a study selection matrix
of a Systematic Literature Review.

---

## Input file
articles.csv

