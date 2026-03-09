# Análisis preliminar (artículos incluidos)

Se realizó el corte sobre los **19 artículos incluidos** (no sobre excluidos/no recuperados).

## Definiciones operativas

- **Dataset**: uso explícito de datasets (benchmark, históricos o train/validation documentado).
- **DACs**: adquisición directa con sensores/plataforma IoT/WSN/microcontrolador (dispositivo de captura).
- **Predicción**: el paper declara explícitamente predicción/forecast/estimación del contaminante o AQI.

## 1) Clasificación Indoor / Outdoor / I+O

- **Indoor (10)**: `A114`, `A132`, `A135`, `A136`, `A138`, `A142`, `A144`, `A149`, `A157`, `A167`
- **Outdoor (6)**: `A009`, `A028`, `A084`, `A087`, `A168`, `A178`
- **I+O (3)**: `A001`, `A123`, `A165`

## 2) ¿Existen soluciones de predicción?

- **Sí**. Hay **10/19** con predicción explícita:
  - `A009`, `A028`, `A087`, `A135`, `A136`, `A138`, `A144`, `A149`, `A157`, `A178`

## 3) ¿Cuántos usan datasets y cuántos DACs?

- **Datasets explícitos**: **7/19**
  - `A028`, `A084`, `A135`, `A136`, `A144`, `A168`, `A178`

- **DACs (captura directa)**: **17/19**
  - `A001`, `A009`, `A028`, `A087`, `A114`, `A123`, `A132`, `A135`, `A136`, `A138`, `A142`, `A144`, `A149`, `A157`, `A165`, `A167`, `A168`

### Solapamiento

- **Dataset + DAC**: **5**
  - `A028`, `A135`, `A136`, `A144`, `A168`

- **Solo dataset**: **2**
  - `A084`, `A178`

## 4) ¿Hay datasets de tiempo real?

- **Sí**. Hay **13/19** con adquisición/flujo en tiempo real (streaming o captura continua en campo):
  - `A001`, `A087`, `A114`, `A123`, `A132`, `A135`, `A136`, `A142`, `A144`, `A149`, `A157`, `A165`, `A167`

## 5) ¿Hay técnicas de IA para predicción?

- **Sí**. Hay **12/19** con IA para predicción/estimación de calidad del aire o variables asociadas:
  - `A009`, `A028`, `A087`, `A114`, `A135`, `A136`, `A138`, `A144`, `A149`, `A157`, `A168`, `A178`

- **Técnicas encontradas**:
  - `ANFIS/RANFIS`
  - `ADFIST`
  - `fuzzy+PSO/GA`
  - `DRL`
  - `ensemble learning`
  - `ARIMA+Kalman+fuzzy`
  - `foundation models/ML`

## Dato adicional

### ¿Cuántos outdoors usan IA para predicción?

- **5** outdoors usan IA para predicción:
  - `A009`
  - `A028`
  - `A087`
  - `A168`
  - `A178`

> Nota: `A084` es outdoor, pero no quedó en el grupo de predicción IA.
