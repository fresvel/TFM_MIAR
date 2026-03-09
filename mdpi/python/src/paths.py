from __future__ import annotations

from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
PYTHON_DIR = SRC_DIR.parent
REPO_ROOT = PYTHON_DIR.parents[1]

DATA_DIR = PYTHON_DIR / "data"
SYNTHESIS_DATA_DIR = DATA_DIR / "sintesis"
SCREENING_DIR = DATA_DIR / "screening"
ZENODO_DIR = DATA_DIR / "zenodo"
OUTPUTS_DIR = PYTHON_DIR / "outputs"

