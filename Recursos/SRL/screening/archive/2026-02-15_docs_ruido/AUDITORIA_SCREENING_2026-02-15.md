# Auditoria de organizacion de `screening` (2026-02-15)

## Objetivo

Reducir ruido operativo en `Recursos/SRL/screening`, conservar trazabilidad y dejar
organizadas las fases del flujo SRL sin eliminar evidencia.

## Criterios de clasificacion

- Canonico: insumo/salida oficial de fases SRL.
- Derivado: resumen, plantilla o documento de apoyo.
- Auxiliar: cache, backup local o copia no necesaria para ejecucion principal.

## Acciones aplicadas (no destructivas)

Se movieron archivos auxiliares a:

`Recursos/SRL/screening/archive/2026-02-15_auxiliares/`

### Movidos a archivo

- `__pycache__/get_pdfs.cpython-312.pyc`
- `ExclusionReasons` (stub sin extension; la version oficial es `ExclusionReasons.md`)
- `articles_data_extraction_full_backup.csv` (respaldo historico)
- `other_files/01.pdf` ... `other_files/08.pdf` (copias auxiliares)

## Estado posterior

- La fuente oficial de exclusion sigue en `ExclusionReasons.md`.
- El validador SRL sigue operativo y consistente con los CSV canonicos.
- No se eliminaron archivos; solo reubicacion para limpieza visual y control.

## Recomendaciones operativas

- Mantener en raiz de `screening` solo archivos canonicos de proceso + scripts.
- Mantener derivables/plantillas en `other_files/`.
- Enviar nuevos backups manuales directamente a `archive/<fecha>/`.

