# AGENTS.md

## Propósito
Este archivo permite que otro agente retome el trabajo del TFM sin perder contexto técnico ni documental.

## Estructura del proyecto
- `Informe/`: memoria del TFM en LaTeX.
- `Propuesta/`: implementación del artefacto, backend Python, frontend Vue y despliegue con Docker.
- `Recursos/`: artículos, PDFs y material de apoyo.

## Estado actual del trabajo
- La memoria ya fue corregida parcialmente con base en observaciones del tutor.
- El documento fue reestructurado para separar:
  - `3. Estado del arte`
  - `4. Marco teórico`
  - `5. Desarrollo del proyecto y resultados`
- El resumen en español, el abstract en inglés y unas conclusiones temporales ya existen.
- La fase 1 de metodología fue compactada para evitar duplicación con el estado del arte.
- La propuesta técnica ya está implementada como prototipo funcional con:
  - backend Python,
  - cálculo AQI,
  - motor difuso,
  - API HTTP,
  - frontend web,
  - Docker Compose.

## Estado actual de la implementación
- Backend: Python modular en `Propuesta/src/aqrisk/`
- Frontend: Vue/Vite en `Propuesta/frontend/`
- Despliegue: `Propuesta/docker-compose.yml`
- Script de arranque: `Propuesta/scripts/start-services.sh`
- Persistencia: histórica local básica, no base de datos robusta.
- Pruebas: humo del pipeline; faltan pruebas de API, frontend y E2E.

## Decisiones técnicas ya tomadas
- La base normativa usa AQI y breakpoints EPA/AQS.
- La evaluación actual del riesgo se apoya en lógica difusa Mamdani.
- Hay una base principal de 54 reglas y una capa contextual separada.
- La arquitectura actual prioriza explicabilidad, trazabilidad y auditabilidad.
- La web actual es parte del prototipo, pero no una plataforma productiva completa.

## Qué haría yo ahora
1. Corregir `README.md`, `requirements.md` y `architecture.md`.
2. Meter capturas reales del frontend en la memoria.
3. Instalar o preparar `Playwright MCP`.
4. Si el alcance aguanta, mover histórico local a `SQLite/PostgreSQL`.
5. Dejar roles/admin fuera del TFM salvo que el tutor lo exija.

## Prioridad de trabajo recomendada
### Alta
- Alinear documentación de `Propuesta/` con lo realmente implementado.
- Insertar evidencia visual real del frontend en `Informe/`.
- Cerrar ajustes pendientes del PDF según comentarios del tutor.

### Media
- Mejorar la evidencia de validación en `Informe/secciones/02_cuerpo/05_desarrollo.tex`.
- Formalizar persistencia de corridas.
- Preparar capturas y pruebas visuales con Playwright.

### Baja
- Roles, perfil, administración.
- Extensión predictiva híbrida.
- Exposición pública del sistema.

## Riesgos de consistencia
- `Propuesta/README.md` todavía puede quedar desalineado con el estado real de la web.
- `Propuesta/docs/requirements.md` y `Propuesta/docs/architecture.md` quedaron atrasados frente a lo implementado.
- La memoria ya afirma que existe interfaz web; si no se añaden capturas, el soporte probatorio queda débil.
- El nivel de validación redactado puede ser más fuerte que la evidencia automatizada disponible.

## Archivos clave a revisar primero
- `Informe/secciones/02_cuerpo/04_estado_del_arte.tex`
- `Informe/secciones/02_cuerpo/05_desarrollo.tex`
- `Informe/secciones/02_cuerpo/06_conclusiones.tex`
- `Propuesta/README.md`
- `Propuesta/docs/requirements.md`
- `Propuesta/docs/architecture.md`
- `Propuesta/frontend/src/App.vue`
- `Propuesta/src/aqrisk/api/server.py`

## Notas operativas
- El informe compila con `bash make.sh` dentro de `Informe/`.
- El stack de la propuesta se levanta con Docker.
- Hay cambios locales no committeados en `Informe/` y una figura nueva en drawio:
  - `Informe/assets/figuras/propuesta/fig02_pipeline_prototipo.drawio`

