# Checklist de integración web del prototipo

## 1. Base funcional

- [x] Núcleo Python del módulo AQRisk implementado.
- [x] Cálculo normativo del AQI con base en `EPA/AQS`.
- [x] Base principal de `54` reglas y capa contextual de `9` reglas.
- [x] Ejecución local por CLI y Docker básico.
- [x] Documentación técnica del núcleo.

## 2. Integración backend

- [x] Definir contrato HTTP mínimo para exponer el módulo.
- [x] Exponer endpoint de salud del servicio.
- [x] Exponer endpoint de metadatos para frontend.
- [x] Exponer endpoint de evaluación con selección de entrada.
- [x] Exponer trazas de explicabilidad para la corrida actual.
- [x] Exponer curvas de membresía para gráficas del frontend.
- [x] Persistir ejecuciones para revisión histórica.
- [x] Exponer catálogo dinámico de estaciones y sensores.
- [ ] Añadir autenticación si la etapa web crece hacia perfiles y roles.

## 3. Integración frontend

- [x] Definir objetivo del frontend como capa de control, visualización y explicabilidad.
- [x] Definir vistas mínimas del sistema.
- [x] Crear esqueleto inicial de `Vue 3 + Vite`.
- [x] Definir servicio HTTP de consumo del backend.
- [x] Conectar el formulario de entrada con el endpoint de evaluación.
- [x] Mostrar resultado base del AQI y salida final del sistema.
- [x] Mostrar trazabilidad de reglas activadas.
- [x] Mostrar cobertura, parámetros soportados y parámetros no soportados.

## 4. Explicabilidad y visualización

- [x] Definir conjunto mínimo de paneles de explicabilidad.
- [x] Graficar series temporales por contaminante.
- [x] Graficar subíndices por contaminante.
- [x] Graficar AQI base frente a salida final.
- [x] Graficar persistencia y concurrencia.
- [x] Graficar funciones de pertenencia.
- [x] Graficar reglas activadas y severidad.
- [x] Graficar agregación y defuzzificación con filtros básicos.
- [x] Graficar ajuste contextual antes y después.
- [x] Incorporar un resumen ejecutivo de la corrida actual.

## 5. Vistas objetivo del frontend

- [x] Definir `Dashboard` principal.
- [x] Definir vista de `Trazabilidad`.
- [x] Definir vista de `Explicabilidad`.
- [x] Definir vista de `Evaluación`.
- [x] Implementar navegación y estado compartido.

## 6. Despliegue y contenedores

- [x] Definir separación entre `backend-api` y `frontend`.
- [x] Preparar `docker-compose` para ambos servicios.
- [x] Añadir build del frontend.
- [x] Añadir volumen de persistencia para histórico local.
- [ ] Añadir servicio de persistencia si se decide almacenar corridas.

## 7. Segunda etapa

- [x] Dashboard avanzado con filtros por estación, fecha y parámetro.
- [x] Preparar la interfaz para capturas y evidencia visual del TFM.
- [ ] Perfil de usuario.
- [ ] Roles.
- [ ] Administración.
- [x] API de escenarios de evaluación.
- [ ] Exposición pública del módulo mediante web app completa.
