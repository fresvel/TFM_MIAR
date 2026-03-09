# Python Workspace

Raiz unificada para el codigo Python activo del articulo y de la sintesis.

## Estructura

- `src/`: scripts Python activos.
- `outputs/`: tablas y figuras generadas por los scripts.
- `data/sintesis/`: dataset enriquecido y artefactos de sintesis usados por el pipeline.
- `data/screening/`: enlace simbolico a `Recursos/SRL/screening/`.
- `data/zenodo/`: enlace simbolico a `Recursos/SRL/zenodo_repo_srl_v1/`.

## Regla de uso

- La matriz base y publicable vive en `data/zenodo/`.
- El dataset enriquecido para sintesis vive en `data/sintesis/`.
- `src/` no debe volver a duplicarse fuera de `mdpi/python/`.
- `outputs/` es la unica raiz activa de salidas analiticas.
