# SRL - Estructura de trabajo y consistencia con Informe

Este directorio contiene los artefactos de la revision sistematica de literatura (SRL)
usados para sustentar la metodologia y, en la siguiente fase, el analisis y la sintesis.

## Criterio de organizacion aplicado

- Reorganizacion no destructiva: no se movieron archivos historicos ni datos base.
- Fuente operativa central: `Recursos/SRL/screening/`.
- Consistencia con el informe: se controla mediante trazabilidad explicita y validacion de CSV.

## Documentos de control

- Manifiesto SRL: `Recursos/SRL/screening/MANIFIESTO_SRL.md`
- Trazabilidad Informe-SRL: `Recursos/SRL/screening/TRAZABILIDAD_INFORME_SRL.md`
- Pipeline por fases: `Recursos/SRL/screening/PIPELINE_FASES_SRL.md`
- Auditoria de organizacion: `Recursos/SRL/screening/AUDITORIA_SCREENING_2026-02-15.md`
- Validador de consistencia: `Recursos/SRL/screening/scripts/validar_consistencia_srl.py`

## Nota de uso

La compilacion del informe (`Informe/make.sh`) sigue usando archivos dentro de `Informe/`.
La consistencia con SRL se mantiene por alineacion de contenido y referencias, no por rutas
compartidas entre carpetas.
