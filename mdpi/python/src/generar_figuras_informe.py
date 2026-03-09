#!/usr/bin/env python3
"""
Generador unificado de figuras para el informe.

Objetivo:
- Ejecutar en un solo comando todos los scripts que producen figuras.
- Sincronizar las figuras generadas hacia `Informe/assets/figuras/*`.

Uso:
  python generar_figuras_informe.py
  python generar_figuras_informe.py --bloques perfil,d1,d2
  python generar_figuras_informe.py --no-sync

Bloques disponibles:
  - perfil
  - d1
  - d2
  - d3
  - eval
"""

from __future__ import annotations

import argparse
import importlib
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from paths import OUTPUTS_DIR, REPO_ROOT


@dataclass(frozen=True)
class BlockSpec:
    module: str
    src_rel: Path
    dst_rels: tuple[Path, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera y sincroniza figuras del informe desde un script unificado.",
    )
    parser.add_argument(
        "--bloques",
        default="perfil,d1,d2,d3,eval",
        help="Lista separada por comas de bloques a ejecutar. Default: perfil,d1,d2,d3,eval",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Solo genera figuras; no copia a Informe/assets/figuras.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra acciones sin ejecutar generación ni copias.",
    )
    return parser.parse_args()


def resolve_paths() -> tuple[Path, Path, Path]:
    script_dir = Path(__file__).resolve().parent
    return script_dir, REPO_ROOT, OUTPUTS_DIR


def get_specs(py_root: Path) -> dict[str, BlockSpec]:
    return {
        "perfil": BlockSpec(
            module="character",
            src_rel=py_root / "figuras" / "perfil",
            dst_rels=(
                Path("Informe/assets/figuras/perfil"),
                Path("mdpi/mdpi/assets/figuras/perfil"),
            ),
        ),
        "d1": BlockSpec(
            module="d1_graphics",
            src_rel=py_root / "figuras" / "d1" / "es",
            dst_rels=(
                Path("Informe/assets/figuras/d1"),
                Path("mdpi/mdpi/assets/figuras/d1"),
            ),
        ),
        "d2": BlockSpec(
            module="d2_phase2",
            src_rel=py_root / "figuras" / "d2" / "es",
            dst_rels=(
                Path("Informe/assets/figuras/d2"),
                Path("mdpi/mdpi/assets/figuras/d2"),
            ),
        ),
        "d3": BlockSpec(
            module="d3_phase2",
            src_rel=py_root / "figuras" / "d3" / "es",
            dst_rels=(
                Path("Informe/assets/figuras/d3"),
                Path("mdpi/mdpi/assets/figuras/d3"),
            ),
        ),
        "eval": BlockSpec(
            module="eval_phase1",
            src_rel=py_root / "figuras" / "eval" / "es",
            dst_rels=(
                Path("Informe/assets/figuras/eval"),
                Path("mdpi/mdpi/assets/figuras/eval"),
            ),
        ),
    }


def run_module_main(module_name: str) -> None:
    module = importlib.import_module(module_name)
    main_fn = getattr(module, "main", None)
    if main_fn is None:
        raise RuntimeError(f"El modulo '{module_name}' no expone una funcion main().")
    main_fn()


def sync_pngs(src_dir: Path, dst_dir: Path) -> int:
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for png in src_dir.glob("*.png"):
        shutil.copy2(png, dst_dir / png.name)
        copied += 1
    return copied


def main() -> None:
    args = parse_args()
    script_dir, repo_root, py_root = resolve_paths()

    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    specs = get_specs(py_root)
    requested = [b.strip().lower() for b in args.bloques.split(",") if b.strip()]
    invalid = [b for b in requested if b not in specs]
    if invalid:
        valid = ", ".join(specs.keys())
        raise SystemExit(f"Bloques invalidos: {invalid}. Bloques validos: {valid}")

    print(f"[INFO] Bloques a ejecutar: {', '.join(requested)}")
    print(f"[INFO] Script dir: {script_dir}")
    print(f"[INFO] Repo root: {repo_root}")

    for block in requested:
        spec = specs[block]
        print(f"\n[STEP] Generando bloque '{block}' con modulo '{spec.module}'")
        if not args.dry_run:
            run_module_main(spec.module)
        else:
            print("  [DRY-RUN] Generacion omitida")

        if args.no_sync:
            print("  [INFO] --no-sync activo: no se copian figuras a directorios de compilacion")
            continue

        src_dir = spec.src_rel
        for dst_rel in spec.dst_rels:
            dst_dir = repo_root / dst_rel
            print(f"  [STEP] Sincronizando PNG: {src_dir} -> {dst_dir}")
            if not args.dry_run:
                if not src_dir.exists():
                    raise RuntimeError(f"No existe directorio fuente de figuras: {src_dir}")
                copied = sync_pngs(src_dir, dst_dir)
                print(f"  [OK] Copiadas {copied} imagenes")
            else:
                print("  [DRY-RUN] Copia omitida")

    print("\n[OK] Proceso unificado completado.")


if __name__ == "__main__":
    main()
