# Arquitectura inicial

## 1. Vista funcional

El prototipo se organiza en cinco bloques funcionales:

1. Ingesta de datos.
2. Normalización y control de calidad.
3. Consolidación determinista del estado base.
4. Evaluación difusa del riesgo.
5. Generación de alerta y exposición por CLI.

## 2. Vista de software

El paquete `aqrisk` queda organizado así:

- `domain`: modelos de datos y tipos base.
- `ingestion`: acceso a OpenAQ y construcción de series.
- `processing`: normalización, cobertura y persistencia.
- `aqi`: cálculo determinista del AQI.
- `fuzzy`: funciones de pertenencia, reglas y motor Mamdani.
- `alerting`: composición de la salida interpretable.
- `application`: orquestación del pipeline.
- `interfaces`: punto de entrada por línea de comandos.
- `api`: exposición HTTP mínima del módulo.

La capa web ya se plantea como un consumidor externo del backend HTTP. Esta decisión evita acoplar la interfaz con el núcleo de cálculo y prepara la evolución hacia dashboard, evaluación y explicabilidad sin reescribir el dominio.

## 3. Decisiones de diseño

### 3.1 Arquitectura modular antes que microservicios

El primer corte se implementa como una aplicación modular monoproceso. Esta decisión reduce complejidad accidental y facilita depuración, trazabilidad y validación. La separación por paquetes deja preparada una migración posterior a servicios independientes si el trabajo lo requiere.

### 3.2 Dominio explícito

Las entidades principales del módulo se representan con `dataclasses` para conservar claridad estructural y minimizar dependencias externas.

### 3.3 AQI con ventanas regulatorias

El cálculo AQI implementa ventanas diferenciadas para `pm25`, `pm10`, `co`, `no2`, `o3` y `so2`. La concentración representativa de cada contaminante se obtiene desde series horarias y no desde el último valor aislado.

### 3.4 Inferencia Mamdani auditable

El motor difuso se implementa con reglas y funciones de pertenencia declaradas en código. Se evita depender de una librería externa para que cada etapa del razonamiento pueda inspeccionarse directamente.

La descripción textual de la base de reglas se documenta en `docs/rule_base.md`. La justificación ampliada de las decisiones se documenta en `docs/design_decisions.md`.

### 3.5 Salida preparada para futura API

La salida final del pipeline se serializa como JSON. Esta decisión facilita exponer el módulo más adelante mediante API web o servicio contenedorizado.

### 3.6 Control web desacoplado

La integración web se resuelve mediante dos piezas separadas:

- un backend HTTP ligero que expone evaluación y metadatos del modelo;
- un frontend Vue/Vite que actúa como controlador visual del artefacto.

Esta separación conserva trazabilidad técnica y permite que el frontend se concentre en control de entrada, explicabilidad y visualización.

### 3.7 Gestión web diferida

Las funciones de dashboard, perfil, roles y administración quedan fuera del primer corte. Se consideran una segunda etapa, posterior a la validación del núcleo del módulo.

## 4. Flujo del pipeline

1. Resolver configuración.
2. Obtener sensores de una estación.
3. Recuperar horas recientes por sensor.
4. Normalizar datos y calcular cobertura.
5. Construir snapshot por parámetro.
6. Calcular concentraciones representativas por ventana regulatoria, subíndices AQI y AQI global.
7. Calcular persistencia.
8. Ejecutar reglas Mamdani.
9. Generar alerta y salida JSON.
