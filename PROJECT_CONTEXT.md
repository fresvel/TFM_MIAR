# PROJECT_CONTEXT.md

## Resumen ejecutivo
Este TFM desarrolla un módulo de monitoreo de calidad del aire basado en datos abiertos y lógica difusa, con capacidad de evaluación del riesgo y generación de alertas. El trabajo tiene dos frentes acoplados:
- la memoria en LaTeX, dentro de `Informe/`;
- el prototipo funcional, dentro de `Propuesta/`.

## Estado de la memoria

### Reestructuración principal
La memoria ya no usa el bloque contenedor `Fundamentación Teórica` como antes. La estructura actual separa:
- `3. Estado del arte`
- `4. Marco teórico`
- `5. Desarrollo del proyecto y resultados`

### Cambios ya aplicados
- Resumen en español redactado.
- Abstract en inglés redactado.
- Conclusiones temporales incorporadas.
- Convocatoria corregida a `Primera`.
- Índices y citaciones ya no deben ir en azul; se ajustó el color de enlaces en `Informe/config/spacing.yml`.
- Se eliminaron cajas informativas de plantilla.
- Se compactó la fase 1 de metodología para no duplicar el SLR.
- Se renombraron capítulos para responder a comentarios del tutor.
- Las ecuaciones visibles del marco teórico ya están numeradas.

### Pendientes documentales relevantes
- Añadir capturas reales del frontend en operación.
- Fortalecer la sección de resultados con evidencia visual y comparativa.
- Revisar si el apéndice debe absorber material técnico del frontend/API.
- Terminar de corregir detalles finos del PDF a partir del archivo `Correcciones.pdf`.

## Estado de la propuesta técnica

### Backend
Ubicación:
- `Propuesta/src/aqrisk/`

Componentes principales:
- cálculo AQI con base EPA/AQS,
- procesamiento y normalización,
- persistencia y concurrencia,
- inferencia difusa Mamdani,
- ajuste contextual,
- API HTTP.

### Frontend
Ubicación:
- `Propuesta/frontend/`

Funciones ya implementadas:
- selección de entradas,
- visualización de resultados,
- trazabilidad,
- explicabilidad,
- historial básico,
- escenarios,
- paneles con gráficas.

### Docker
Ubicación:
- `Propuesta/docker-compose.yml`

El proyecto ya cuenta con contenedores para backend y frontend.

## Modelo lógico actual

### Capa normativa
- calcula AQI base con criterios EPA/AQS.

### Variables auxiliares
- derivan persistencia, concurrencia y cobertura.

### Capa difusa principal
- usa una base principal de 54 reglas.

### Capa contextual
- ajusta el riesgo con reglas adicionales sobre variables contextuales.

### Salida
- compone riesgo final, alerta y respuesta trazable.

## Validación actual
- Ya existe validación funcional del pipeline.
- Ya existe ejecución con estaciones reales vía OpenAQ.
- La validación sigue siendo limitada para una defensa fuerte si se exige comparación extensa entre estaciones y horizontes.

## Vacíos técnicos abiertos
- No hay autenticación ni gestión de acceso.
- No hay roles, perfil ni administración.
- La persistencia sigue siendo local y básica.
- No hay base de datos robusta.
- No hay pruebas automatizadas del frontend ni E2E.
- La publicación externa de la aplicación no está cerrada.

## Vacíos de consistencia entre memoria y código
- `Propuesta/README.md` puede seguir desfasado respecto a la existencia de la web.
- `Propuesta/docs/requirements.md` puede describir etapas que ya fueron implementadas.
- `Propuesta/docs/architecture.md` debe reflejar la API y el frontend ya existentes.
- La memoria ya afirma la interfaz web, pero todavía necesita evidencia visual.

## Qué haría yo ahora
1. Corregir `README.md`, `requirements.md` y `architecture.md`.
2. Meter capturas reales del frontend en la memoria.
3. Instalar o preparar `Playwright MCP`.
4. Si el alcance aguanta, mover histórico local a `SQLite/PostgreSQL`.
5. Dejar roles/admin fuera del TFM salvo que el tutor lo exija.

## MCPs recomendados para continuar
- `Playwright MCP`: validación visual, navegación automatizada, capturas y pruebas E2E.
- `GitHub MCP`: si se va a ordenar el trabajo por commits/PRs.
- `PostgreSQL MCP`: si se decide profesionalizar persistencia e histórico.

## Archivos que otro agente debe abrir primero
- `AGENTS.md`
- `Informe/secciones/02_cuerpo/05_desarrollo.tex`
- `Informe/secciones/02_cuerpo/04_estado_del_arte.tex`
- `Informe/secciones/02_cuerpo/06_conclusiones.tex`
- `Propuesta/README.md`
- `Propuesta/docs/requirements.md`
- `Propuesta/docs/architecture.md`
- `Propuesta/frontend/src/App.vue`
- `Propuesta/src/aqrisk/api/server.py`

## Observación práctica
Si el objetivo inmediato es dejar la memoria entregable, el frente correcto no es ampliar alcance. El frente correcto es:
- alinear documentación,
- meter evidencia visual,
- endurecer un poco resultados,
- y cerrar incoherencias entre `Informe/` y `Propuesta/`.

