#!/usr/bin/env python3
"""Valida consistencia minima de artefactos SRL antes de Analisis/Sintesis."""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path
import sys


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ids(rows, key="Article_ID"):
    return {r[key].strip() for r in rows if r.get(key, "").strip()}


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    required = {
        "articles_screened.csv": base / "01_screening" / "articles_screened.csv",
        "articles_full_text.csv": base / "02_elegibilidad" / "articles_full_text.csv",
        "articles_data_extraction.csv": base / "04_extraccion" / "articles_data_extraction.csv",
        "articles_quality_assessment.csv": base / "03_calidad" / "articles_quality_assessment.csv",
    }
    optional_summary = base / "03_calidad" / "qa_scores_summary.csv"

    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        print("ERROR: faltan archivos requeridos:")
        for name in missing:
            print(f"  - {name}")
        return 1

    screened = read_csv(required["articles_screened.csv"])
    full_text = read_csv(required["articles_full_text.csv"])
    extraction = read_csv(required["articles_data_extraction.csv"])
    qa = read_csv(required["articles_quality_assessment.csv"])
    qa_summary = read_csv(optional_summary) if optional_summary.exists() else []

    include_ids = {
        r["Article_ID"]
        for r in full_text
        if r.get("FT_Final_decision", "").strip() == "Include"
    }
    extraction_ids = ids(extraction)
    qa_ids = ids(qa)
    qa_summary_ids = ids(qa_summary) if qa_summary else set()

    errors = []

    if include_ids != extraction_ids:
        errors.append(
            "IDs Include (full text) no coinciden con extraction: "
            f"faltan={sorted(include_ids - extraction_ids)} "
            f"extras={sorted(extraction_ids - include_ids)}"
        )

    if include_ids != qa_ids:
        errors.append(
            "IDs Include (full text) no coinciden con QA: "
            f"faltan={sorted(include_ids - qa_ids)} "
            f"extras={sorted(qa_ids - include_ids)}"
        )

    if qa_summary and include_ids != qa_summary_ids:
        errors.append(
            "IDs Include (full text) no coinciden con QA summary: "
            f"faltan={sorted(include_ids - qa_summary_ids)} "
            f"extras={sorted(qa_summary_ids - include_ids)}"
        )

    # Check de columnas esperadas de extraccion
    expected_extraction_cols = 50
    real_cols = len(extraction[0].keys()) if extraction else 0
    if real_cols != expected_extraction_cols:
        errors.append(
            f"Extraccion tiene {real_cols} columnas (esperadas: {expected_extraction_cols})."
        )

    # Consistencia score/banda: usar summary si existe; si no, derivar desde QA principal.
    if qa_summary:
        score_band = Counter(r.get("Quality_band", "").strip() for r in qa_summary)
        if not {"Alta", "Media", "Baja"}.intersection(score_band.keys()):
            errors.append("QA summary no contiene bandas de calidad esperadas (Alta/Media/Baja).")
        try:
            scores = [float(r["Score_percent"]) for r in qa_summary]
        except Exception:
            errors.append("No se pudo parsear Score_percent en qa_scores_summary.csv.")
            scores = []
    else:
        score_band = Counter(r.get("QA_Quality_band", "").strip() for r in qa)
        if not {"Alta", "Media", "Baja"}.intersection(score_band.keys()):
            errors.append("QA principal no contiene bandas esperadas (Alta/Media/Baja).")
        try:
            scores = [float(r["QA_Score_percent"]) for r in qa]
        except Exception:
            errors.append("No se pudo parsear QA_Score_percent en articles_quality_assessment.csv.")
            scores = []

    print("=== Validacion SRL ===")
    print(f"screened: {len(screened)}")
    print(f"full_text: {len(full_text)} (Include={len(include_ids)})")
    print(f"extraction: {len(extraction)}")
    print(f"quality_assessment: {len(qa)}")
    print(f"qa_summary: {len(qa_summary)} ({'presente' if qa_summary else 'ausente'})")
    print(f"bandas_qa_summary: {dict(score_band)}")
    if scores:
        print(f"score_mean: {statistics.mean(scores):.2f}")
        print(f"score_median: {statistics.median(scores):.2f}")

    if errors:
        print("\nRESULTADO: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1

    print("\nRESULTADO: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
