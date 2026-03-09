#!/usr/bin/env python3
"""
Fase 1 (D2) - Normalizacion documentada (Puntos 1-7).

Genera:
- Dataset de sintesis actualizado con columnas:
  - D2_Fuzzy_approach_type_norm
  - D2_Inference_purpose_norm
  - D2_Membership_functions_norm
  - D2_Interpretability_elements_norm
  - D2_Rule_base_definition_norm
  - D2_Defuzzification_method_norm
  - D2_Risk_modeling_approach_norm
  - D2_Synthesis_notes
- Conteos pre y post normalizacion (formato explotado) para:
  - D2_Fuzzy_approach_type
  - D2_Inference_purpose
  - D2_Membership_functions
  - D2_Interpretability_elements
  - D2_Rule_base_definition
  - D2_Defuzzification_method
  - D2_Risk_modeling_approach
- Trazabilidad por variante con evidencia para redaccion citada (p1 y p2).
- Diccionarios de mapeo aplicados (p1 y p2).

No modifica los datasets originales de screening.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

import pandas as pd


SPLIT_RE = re.compile(r"[;|]+")
NA_VALUES = {"", "NR", "N/R", "NA", "N/A"}


def read_dataset(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig")


def parse_multi(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).strip()
    if text.upper() in NA_VALUES:
        return []
    return [item.strip() for item in SPLIT_RE.split(text) if item.strip()]


def parse_multi_keep_nr(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).strip()
    if not text:
        return []
    out: list[str] = []
    for item in SPLIT_RE.split(text):
        token = item.strip()
        if not token:
            continue
        token_u = token.upper()
        if token_u in {"N/R", "NA", "N/A"}:
            continue
        if token_u == "NR":
            out.append("NR")
            continue
        out.append(token)
    return out


def explode_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    rows: list[str] = []
    for value in df[col]:
        rows.extend(parse_multi(value))
    if not rows:
        return pd.DataFrame(columns=["value", "k"])
    counts = pd.Series(rows).value_counts().rename_axis("value").reset_index(name="k")
    return counts


def explode_counts_with_nr(df: pd.DataFrame, col: str) -> pd.DataFrame:
    rows: list[str] = []
    for value in df[col]:
        rows.extend(parse_multi_keep_nr(value))
    if not rows:
        return pd.DataFrame(columns=["value", "k"])
    counts = pd.Series(rows).value_counts().rename_axis("value").reset_index(name="k")
    return counts


def map_approach_token(token: str) -> str:
    mapping = {
        "I-ANFIS": "ANFIS",
        "Other:RANFIS": "ANFIS",
        "Other:TSK": "Sugeno/TSK",
        "Sugeno": "Sugeno/TSK",
        "Other:Tsukamoto": "Tsukamoto",
        "Type1_FIS": "Type1_Generic",
        "Other:Fuzzy_ARTMAP": "Hybrid_Fuzzy",
    }
    return mapping.get(token, token)


def map_purpose_token(token: str) -> str:
    mapping = {
        "Other:Sensor_Calibration_Adjustment": "Operational_Optimization",
        "Other:Filter_Replacement_Support": "Operational_Optimization",
        "Other:HVAC_Power_Optimization": "Operational_Optimization",
        "Route_Optimization": "Operational_Optimization",
    }
    return mapping.get(token, token)


def map_membership_token(token: str) -> str:
    mapping = {
        "Other:Triangular": "Triangular",
        "Other:Trapezoidal": "Trapezoidal",
        "Other:Bell_Shaped": "Bell",
        "Other:Generalized_Bell": "Bell",
    }
    return mapping.get(token, token)


def map_interpretability_token(token: str) -> str:
    mapping = {
        "Other:Fuzzy_Surface": "Fuzzy_Surface",
        "Other:Confusion_Matrix": "Confusion_Matrix",
        "Other:Tree_Structure": "Rule_Transparency",
        "Other:Color_Mapping": "AQI_Mapping",
        "AQI_Mapping_Table": "AQI_Mapping",
    }
    return mapping.get(token, token)


def map_rule_base_token(token: str) -> str:
    mapping = {
        "Other:Two_Rules_Reported": "Explicit_Rule_Table",
        "Other:Mamdani_Rule_Base": "Explicit_Rule_Table",
    }
    return mapping.get(token, token)


def map_defuzzification_token(token: str) -> str:
    mapping = {
        "Other:Takagi_Sugeno_and_Centroid_reported": "Centroid; Weighted_Average",
    }
    return mapping.get(token, token)


def map_risk_token(token: str) -> str:
    mapping = {
        "Other:PM2.5_Forecast_Only": "Prediction_Based_Risk",
        "Other:Threshold_Based_Environment_Quality": "AQI_Thresholds",
        "Other:OR_Risk_Group_0_to_13": "Custom_Risk_Scale",
        "LoP_m-AQI": "Custom_Risk_Scale",
    }
    return mapping.get(token, token)


def normalize_approach_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        mapped = map_approach_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_purpose_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        mapped = map_purpose_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_membership_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        if token == "Other:Triangular_Trapezoidal":
            for item in ["Triangular", "Trapezoidal"]:
                if item not in out:
                    out.append(item)
            continue
        if token == "Other:Linear_Output":
            # Consequente de Sugeno; se conserva como nota, no como tipo de MF.
            continue
        mapped = map_membership_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_interpretability_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        mapped = map_interpretability_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_rule_base_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        mapped = map_rule_base_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_defuzzification_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        if token == "Other:Takagi_Sugeno_and_Centroid_reported":
            for item in ["Centroid", "Weighted_Average"]:
                if item not in out:
                    out.append(item)
            continue
        mapped = map_defuzzification_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def normalize_risk_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for token in tokens:
        mapped = map_risk_token(token)
        if mapped not in out:
            out.append(mapped)
    return out


def build_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "ADFIST": (
            "ADFIST",
            "Mantener separado de ANFIS: enfoque arbolado (Adaptive Dynamic FIS Tree) "
            "con optimizacion especifica reportada.",
        ),
        "I-ANFIS": (
            "ANFIS",
            "Variante de la familia ANFIS; se normaliza para consolidar conteos por familia.",
        ),
        "Other:RANFIS": (
            "ANFIS",
            "Reportado como variante reforzada de ANFIS en el estudio.",
        ),
        "Other:TSK": (
            "Sugeno/TSK",
            "TSK es subfamilia de Sugeno; se unifica para analisis comparativo.",
        ),
        "Sugeno": (
            "Sugeno/TSK",
            "Se unifica con TSK para reducir dispersion semantica en la sintesis.",
        ),
        "Other:Tsukamoto": (
            "Tsukamoto",
            "Tsukamoto se mantiene como categoria propia (no equivalente a Sugeno/TSK).",
        ),
        "Type1_FIS": (
            "Type1_Generic",
            "Etiqueta generica tipo-1 sin subtipo explicito; se remapea para evitar ambiguedad.",
        ),
        "Other:Fuzzy_ARTMAP": (
            "Hybrid_Fuzzy",
            "Fuzzy ARTMAP integra componente neuro-fuzzy/ML; se agrega en Hybrid_Fuzzy con nota de variante.",
        ),
    }

    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi(record["D2_Fuzzy_approach_type"])
        for token in tokens:
            if token not in notes_map:
                continue
            mapped, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": map_approach_token(token),
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "I-ANFIS",
            "Normalized_token": "ANFIS",
            "Rule_type": "family_unification",
            "Rationale": "Variante de ANFIS consolidada en la familia base.",
        },
        {
            "Original_token": "Other:RANFIS",
            "Normalized_token": "ANFIS",
            "Rule_type": "family_unification",
            "Rationale": "Variante reforzada de ANFIS consolidada para conteo por familia.",
        },
        {
            "Original_token": "Sugeno",
            "Normalized_token": "Sugeno/TSK",
            "Rule_type": "family_unification",
            "Rationale": "Unificacion operativa con TSK para evitar dispersion semantica.",
        },
        {
            "Original_token": "Other:TSK",
            "Normalized_token": "Sugeno/TSK",
            "Rule_type": "family_unification",
            "Rationale": "TSK tratado como subfamilia de Sugeno para comparacion agregada.",
        },
        {
            "Original_token": "Other:Tsukamoto",
            "Normalized_token": "Tsukamoto",
            "Rule_type": "separate_family",
            "Rationale": "Se mantiene como familia propia (no equivalente a Sugeno/TSK).",
        },
        {
            "Original_token": "Type1_FIS",
            "Normalized_token": "Type1_Generic",
            "Rule_type": "disambiguation",
            "Rationale": "Etiqueta generica de FIS tipo-1 sin subtipo explicito.",
        },
        {
            "Original_token": "Other:Fuzzy_ARTMAP",
            "Normalized_token": "Hybrid_Fuzzy",
            "Rule_type": "hybrid_family",
            "Rationale": "Se integra en Hybrid_Fuzzy y se conserva nota de variante ML para trazabilidad narrativa.",
        },
        {
            "Original_token": "ADFIST",
            "Normalized_token": "ADFIST",
            "Rule_type": "preserve_variant",
            "Rationale": "Se preserva como variante estructural (FIS en arbol) del corpus.",
        },
    ]
    return pd.DataFrame(rows)


def build_purpose_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:Sensor_Calibration_Adjustment": (
            "Operational_Optimization",
            "Objetivo operativo de calibracion/ajuste, consolidado en optimizacion operativa.",
        ),
        "Other:Filter_Replacement_Support": (
            "Operational_Optimization",
            "Soporte de decision de reemplazo de filtro, consolidado en optimizacion operativa.",
        ),
        "Other:HVAC_Power_Optimization": (
            "Operational_Optimization",
            "Optimizacion de potencia HVAC, consolidada como optimizacion operativa.",
        ),
        "Route_Optimization": (
            "Operational_Optimization",
            "Optimizacion de ruta, consolidada en la misma categoria operativa.",
        ),
    }
    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi(record["D2_Inference_purpose"])
        for token in tokens:
            if token not in notes_map:
                continue
            _, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": map_purpose_token(token),
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_purpose() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "Other:Sensor_Calibration_Adjustment",
            "Normalized_token": "Operational_Optimization",
            "Rule_type": "purpose_unification",
            "Rationale": "Se integra como optimizacion operativa orientada al ajuste del sistema.",
        },
        {
            "Original_token": "Other:Filter_Replacement_Support",
            "Normalized_token": "Operational_Optimization",
            "Rule_type": "purpose_unification",
            "Rationale": "Se integra como objetivo operativo de soporte de mantenimiento.",
        },
        {
            "Original_token": "Other:HVAC_Power_Optimization",
            "Normalized_token": "Operational_Optimization",
            "Rule_type": "purpose_unification",
            "Rationale": "Se integra como optimizacion operativa de actuacion.",
        },
        {
            "Original_token": "Route_Optimization",
            "Normalized_token": "Operational_Optimization",
            "Rule_type": "purpose_unification",
            "Rationale": "Se integra en optimizacion operativa para comparabilidad de propositos especiales.",
        },
    ]
    return pd.DataFrame(rows)


def build_membership_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:Triangular": (
            "Triangular",
            "Forma explicita de MF triangular.",
        ),
        "Other:Trapezoidal": (
            "Trapezoidal",
            "Forma explicita de MF trapezoidal.",
        ),
        "Other:Triangular_Trapezoidal": (
            "Triangular; Trapezoidal",
            "Expresion compuesta desdoblada en dos etiquetas de forma.",
        ),
        "Other:Bell_Shaped": (
            "Bell",
            "Se unifica en familia Bell para comparabilidad.",
        ),
        "Other:Generalized_Bell": (
            "Bell",
            "Se unifica en familia Bell para comparabilidad.",
        ),
        "Other:Linear_Output": (
            "excluded_from_MF_counts",
            "No se cuenta como MF; se trata como nota de consecuente Sugeno.",
        ),
    }
    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi(record["D2_Membership_functions"])
        for token in tokens:
            if token not in notes_map:
                continue
            proposed, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": proposed,
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_membership() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "Other:Triangular",
            "Normalized_token": "Triangular",
            "Rule_type": "shape_unification",
            "Rationale": "Forma explicita de MF triangular.",
        },
        {
            "Original_token": "Other:Trapezoidal",
            "Normalized_token": "Trapezoidal",
            "Rule_type": "shape_unification",
            "Rationale": "Forma explicita de MF trapezoidal.",
        },
        {
            "Original_token": "Other:Triangular_Trapezoidal",
            "Normalized_token": "Triangular; Trapezoidal",
            "Rule_type": "shape_split",
            "Rationale": "Se desdobla en dos etiquetas para analisis multietiqueta.",
        },
        {
            "Original_token": "Other:Bell_Shaped",
            "Normalized_token": "Bell",
            "Rule_type": "shape_unification",
            "Rationale": "Se integra en familia Bell para comparabilidad.",
        },
        {
            "Original_token": "Other:Generalized_Bell",
            "Normalized_token": "Bell",
            "Rule_type": "shape_unification",
            "Rationale": "Se integra en familia Bell para comparabilidad.",
        },
        {
            "Original_token": "Other:Linear_Output",
            "Normalized_token": "excluded_from_MF_counts",
            "Rule_type": "scope_refinement",
            "Rationale": "Se excluye de MF por representar consecuente de salida en Sugeno.",
        },
    ]
    return pd.DataFrame(rows)


def build_interpretability_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:Fuzzy_Surface": (
            "Fuzzy_Surface",
            "Se explicita como visualizacion de superficie difusa.",
        ),
        "Other:Confusion_Matrix": (
            "Confusion_Matrix",
            "Se explicita como evidencia de desempeno clasificatorio.",
        ),
        "Other:Tree_Structure": (
            "Rule_Transparency",
            "Se integra en transparencia de reglas por su caracter explicativo estructural.",
        ),
        "Other:Color_Mapping": (
            "AQI_Mapping",
            "Se integra como mapeo visual de clases AQI.",
        ),
        "NR": (
            "NR",
            "Se mantiene explicito para trazabilidad de ausencia de reporte.",
        ),
    }

    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi_keep_nr(record["D2_Interpretability_elements"])
        for token in tokens:
            if token not in notes_map:
                continue
            proposed, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": proposed,
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_interpretability() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "AQI_Mapping_Table",
            "Normalized_token": "AQI_Mapping",
            "Rule_type": "label_generalization",
            "Rationale": "Se generaliza la evidencia de mapeo AQI (tabular o visual) en una sola categoria.",
        },
        {
            "Original_token": "Other:Fuzzy_Surface",
            "Normalized_token": "Fuzzy_Surface",
            "Rule_type": "label_unification",
            "Rationale": "Se explicita como visualizacion de superficie difusa.",
        },
        {
            "Original_token": "Other:Confusion_Matrix",
            "Normalized_token": "Confusion_Matrix",
            "Rule_type": "label_unification",
            "Rationale": "Se explicita como evidencia de desempeno clasificatorio.",
        },
        {
            "Original_token": "Other:Tree_Structure",
            "Normalized_token": "Rule_Transparency",
            "Rule_type": "conceptual_merge",
            "Rationale": "Se integra por su valor explicativo en la interpretabilidad del sistema.",
        },
        {
            "Original_token": "Other:Color_Mapping",
            "Normalized_token": "AQI_Mapping",
            "Rule_type": "conceptual_merge",
            "Rationale": "Se integra como mapeo visual de clases AQI.",
        },
        {
            "Original_token": "NR",
            "Normalized_token": "NR",
            "Rule_type": "explicit_missingness",
            "Rationale": "Se mantiene como categoria explicita de no reporte.",
        },
    ]
    return pd.DataFrame(rows)


def build_rule_base_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:Two_Rules_Reported": (
            "Explicit_Rule_Table",
            "Se integra como base de reglas explicita al reportar reglas concretas.",
        ),
        "Other:Mamdani_Rule_Base": (
            "Explicit_Rule_Table",
            "Se integra como base de reglas explicita de tipo Mamdani.",
        ),
    }

    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi_keep_nr(record["D2_Rule_base_definition"])
        for token in tokens:
            if token not in notes_map:
                continue
            proposed, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": proposed,
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_rule_base() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "Other:Two_Rules_Reported",
            "Normalized_token": "Explicit_Rule_Table",
            "Rule_type": "conceptual_merge",
            "Rationale": "Reporte de reglas puntuales se consolida como base explicita.",
        },
        {
            "Original_token": "Other:Mamdani_Rule_Base",
            "Normalized_token": "Explicit_Rule_Table",
            "Rule_type": "conceptual_merge",
            "Rationale": "Base de reglas Mamdani se consolida en la categoria explicita.",
        },
    ]
    return pd.DataFrame(rows)


def build_defuzzification_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:Takagi_Sugeno_and_Centroid_reported": (
            "Centroid; Weighted_Average",
            "Reporte mixto; se desdobla en ambos metodos para analisis multietiqueta.",
        ),
    }

    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi_keep_nr(record["D2_Defuzzification_method"])
        for token in tokens:
            if token not in notes_map:
                continue
            proposed, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": proposed,
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_defuzzification() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "Other:Takagi_Sugeno_and_Centroid_reported",
            "Normalized_token": "Centroid; Weighted_Average",
            "Rule_type": "method_split",
            "Rationale": "Metodo mixto desdoblado en dos etiquetas para comparabilidad.",
        },
    ]
    return pd.DataFrame(rows)


def build_risk_variant_notes(df: pd.DataFrame) -> pd.DataFrame:
    notes_map = {
        "Other:PM2.5_Forecast_Only": (
            "Prediction_Based_Risk",
            "Se integra como riesgo basado en prediccion (forecast especifico de PM2.5).",
        ),
        "Other:Threshold_Based_Environment_Quality": (
            "AQI_Thresholds",
            "Se integra como enfoque de umbrales para clasificacion de riesgo.",
        ),
        "Other:OR_Risk_Group_0_to_13": (
            "Custom_Risk_Scale",
            "Se integra como escala de riesgo propia definida por el estudio.",
        ),
        "LoP_m-AQI": (
            "Custom_Risk_Scale",
            "Indice compuesto propio; se integra como escala personalizada de riesgo.",
        ),
    }

    rows: list[dict[str, str]] = []
    for _, record in df.iterrows():
        tokens = parse_multi_keep_nr(record["D2_Risk_modeling_approach"])
        for token in tokens:
            if token not in notes_map:
                continue
            proposed, technical_note = notes_map[token]
            rows.append(
                {
                    "Article_ID": str(record.get("Article_ID", "")),
                    "Variant_detected": token,
                    "Proposed_normalized": proposed,
                    "Decision_status": "working_v1",
                    "Evidence_D2_pages": str(record.get("Evidence_D2_pages", "")),
                    "Title": str(record.get("Title", "")),
                    "Technical_note": technical_note,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Variant_detected", "Article_ID"]).reset_index(drop=True)
    return out


def build_mapping_table_risk() -> pd.DataFrame:
    rows = [
        {
            "Original_token": "Other:PM2.5_Forecast_Only",
            "Normalized_token": "Prediction_Based_Risk",
            "Rule_type": "conceptual_merge",
            "Rationale": "Forecast especifico de contaminante se integra en riesgo predictivo.",
        },
        {
            "Original_token": "Other:Threshold_Based_Environment_Quality",
            "Normalized_token": "AQI_Thresholds",
            "Rule_type": "conceptual_merge",
            "Rationale": "Clasificacion por umbrales se integra en enfoque AQI basado en thresholds.",
        },
        {
            "Original_token": "Other:OR_Risk_Group_0_to_13",
            "Normalized_token": "Custom_Risk_Scale",
            "Rule_type": "custom_scale",
            "Rationale": "Escala propia de riesgo, separada de AQI y prediccion.",
        },
        {
            "Original_token": "LoP_m-AQI",
            "Normalized_token": "Custom_Risk_Scale",
            "Rule_type": "custom_scale",
            "Rationale": "Indice hibrido propio, agrupado como escala personalizada.",
        },
    ]
    return pd.DataFrame(rows)


def build_synthesis_note(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t != map_approach_token(t)]
    variant_tokens += [t for t in tokens_raw if t == "ADFIST"]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        mapped = map_approach_token(token)
        if token == "ADFIST":
            parts.append("ADFIST se mantiene como variante estructural separada")
        elif token == "Other:Fuzzy_ARTMAP":
            parts.append("Fuzzy_ARTMAP (variante ML) se integra en Hybrid_Fuzzy")
        elif token in {"I-ANFIS", "Other:RANFIS"}:
            parts.append(f"{token} se consolida en ANFIS")
        elif token in {"Sugeno", "Other:TSK"}:
            parts.append(f"{token} se unifica en Sugeno/TSK")
        elif token == "Other:Tsukamoto":
            parts.append("Tsukamoto se mantiene como familia propia")
        elif token == "Type1_FIS":
            parts.append("Type1_FIS se remapea a Type1_Generic")
        else:
            parts.append(f"{token} -> {mapped}")

    return "; ".join(parts)


def build_synthesis_note_purpose(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t != map_purpose_token(t)]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:Sensor_Calibration_Adjustment":
            parts.append("Sensor_Calibration_Adjustment se integra en Operational_Optimization")
        elif token == "Other:Filter_Replacement_Support":
            parts.append("Filter_Replacement_Support se integra en Operational_Optimization")
        elif token == "Other:HVAC_Power_Optimization":
            parts.append("HVAC_Power_Optimization se integra en Operational_Optimization")
        elif token == "Route_Optimization":
            parts.append("Route_Optimization se integra en Operational_Optimization")
    return "; ".join(parts)


def build_synthesis_note_membership(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t.startswith("Other:")]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:Triangular":
            parts.append("Other:Triangular se unifica en Triangular")
        elif token == "Other:Trapezoidal":
            parts.append("Other:Trapezoidal se unifica en Trapezoidal")
        elif token == "Other:Triangular_Trapezoidal":
            parts.append("Other:Triangular_Trapezoidal se desdobla en Triangular y Trapezoidal")
        elif token in {"Other:Bell_Shaped", "Other:Generalized_Bell"}:
            parts.append(f"{token} se unifica en Bell")
        elif token == "Other:Linear_Output":
            parts.append("Other:Linear_Output se excluye del conteo de MF (nota de consecuente Sugeno)")
    return "; ".join(parts)


def build_synthesis_note_interpretability(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t.startswith("Other:") or t == "NR"]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:Fuzzy_Surface":
            parts.append("Other:Fuzzy_Surface se unifica en Fuzzy_Surface")
        elif token == "Other:Confusion_Matrix":
            parts.append("Other:Confusion_Matrix se unifica en Confusion_Matrix")
        elif token == "Other:Tree_Structure":
            parts.append("Other:Tree_Structure se integra en Rule_Transparency")
        elif token == "Other:Color_Mapping":
            parts.append("Other:Color_Mapping se integra en AQI_Mapping")
        elif token == "AQI_Mapping_Table":
            parts.append("AQI_Mapping_Table se generaliza a AQI_Mapping")
        elif token == "NR":
            parts.append("NR se mantiene explicito")
    return "; ".join(parts)


def build_synthesis_note_rule_base(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t != map_rule_base_token(t)]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:Two_Rules_Reported":
            parts.append("Other:Two_Rules_Reported se integra en Explicit_Rule_Table")
        elif token == "Other:Mamdani_Rule_Base":
            parts.append("Other:Mamdani_Rule_Base se integra en Explicit_Rule_Table")
    return "; ".join(parts)


def build_synthesis_note_defuzzification(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t == "Other:Takagi_Sugeno_and_Centroid_reported"]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:Takagi_Sugeno_and_Centroid_reported":
            parts.append(
                "Other:Takagi_Sugeno_and_Centroid_reported se desdobla en Centroid y Weighted_Average"
            )
    return "; ".join(parts)


def build_synthesis_note_risk(tokens_raw: list[str], tokens_norm: list[str]) -> str:
    variant_tokens = [t for t in tokens_raw if t != map_risk_token(t)]
    variant_tokens = list(dict.fromkeys(variant_tokens))
    if not variant_tokens:
        return ""

    parts: list[str] = []
    for token in variant_tokens:
        if token == "Other:PM2.5_Forecast_Only":
            parts.append("Other:PM2.5_Forecast_Only se integra en Prediction_Based_Risk")
        elif token == "Other:Threshold_Based_Environment_Quality":
            parts.append("Other:Threshold_Based_Environment_Quality se integra en AQI_Thresholds")
        elif token == "Other:OR_Risk_Group_0_to_13":
            parts.append("Other:OR_Risk_Group_0_to_13 se integra en Custom_Risk_Scale")
        elif token == "LoP_m-AQI":
            parts.append("LoP_m-AQI se integra en Custom_Risk_Scale")
    return "; ".join(parts)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir / "assets" / "sintesis" / "dataset.csv"
    dataset_path_mirror = script_dir.parent / "dataset.csv"
    output_dir = script_dir / "salidas" / "d2" / "fase1"

    df = read_dataset(dataset_path)

    pre_counts = explode_counts(df, "D2_Fuzzy_approach_type")

    normalized_tokens_all: list[str] = []
    for value in df["D2_Fuzzy_approach_type"]:
        normalized_tokens_all.extend(normalize_approach_tokens(parse_multi(value)))
    post_counts = (
        pd.Series(normalized_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_purpose = explode_counts(df, "D2_Inference_purpose")
    normalized_purpose_tokens_all: list[str] = []
    for value in df["D2_Inference_purpose"]:
        normalized_purpose_tokens_all.extend(normalize_purpose_tokens(parse_multi(value)))
    post_counts_purpose = (
        pd.Series(normalized_purpose_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_purpose_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_membership = explode_counts(df, "D2_Membership_functions")
    normalized_membership_tokens_all: list[str] = []
    for value in df["D2_Membership_functions"]:
        normalized_membership_tokens_all.extend(normalize_membership_tokens(parse_multi(value)))
    post_counts_membership = (
        pd.Series(normalized_membership_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_membership_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_interpretability = explode_counts_with_nr(df, "D2_Interpretability_elements")
    normalized_interpretability_tokens_all: list[str] = []
    for value in df["D2_Interpretability_elements"]:
        normalized_interpretability_tokens_all.extend(normalize_interpretability_tokens(parse_multi_keep_nr(value)))
    post_counts_interpretability = (
        pd.Series(normalized_interpretability_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_interpretability_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_rule_base = explode_counts_with_nr(df, "D2_Rule_base_definition")
    normalized_rule_base_tokens_all: list[str] = []
    for value in df["D2_Rule_base_definition"]:
        normalized_rule_base_tokens_all.extend(normalize_rule_base_tokens(parse_multi_keep_nr(value)))
    post_counts_rule_base = (
        pd.Series(normalized_rule_base_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_rule_base_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_defuzzification = explode_counts_with_nr(df, "D2_Defuzzification_method")
    normalized_defuzzification_tokens_all: list[str] = []
    for value in df["D2_Defuzzification_method"]:
        normalized_defuzzification_tokens_all.extend(
            normalize_defuzzification_tokens(parse_multi_keep_nr(value))
        )
    post_counts_defuzzification = (
        pd.Series(normalized_defuzzification_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_defuzzification_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )
    pre_counts_risk = explode_counts_with_nr(df, "D2_Risk_modeling_approach")
    normalized_risk_tokens_all: list[str] = []
    for value in df["D2_Risk_modeling_approach"]:
        normalized_risk_tokens_all.extend(normalize_risk_tokens(parse_multi_keep_nr(value)))
    post_counts_risk = (
        pd.Series(normalized_risk_tokens_all).value_counts().rename_axis("value").reset_index(name="k")
        if normalized_risk_tokens_all
        else pd.DataFrame(columns=["value", "k"])
    )

    df_norm = df.copy()
    norm_values: list[str] = []
    synth_notes_p1: list[str] = []
    for raw in df["D2_Fuzzy_approach_type"]:
        raw_tokens = parse_multi(raw)
        norm_tokens = normalize_approach_tokens(raw_tokens)
        norm_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p1.append(build_synthesis_note(raw_tokens, norm_tokens))
    df_norm["D2_Fuzzy_approach_type_norm"] = norm_values
    norm_purpose_values: list[str] = []
    synth_notes_p2: list[str] = []
    for raw in df["D2_Inference_purpose"]:
        raw_tokens = parse_multi(raw)
        norm_tokens = normalize_purpose_tokens(raw_tokens)
        norm_purpose_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p2.append(build_synthesis_note_purpose(raw_tokens, norm_tokens))
    df_norm["D2_Inference_purpose_norm"] = norm_purpose_values
    norm_membership_values: list[str] = []
    synth_notes_p3: list[str] = []
    for raw in df["D2_Membership_functions"]:
        raw_tokens = parse_multi(raw)
        norm_tokens = normalize_membership_tokens(raw_tokens)
        norm_membership_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p3.append(build_synthesis_note_membership(raw_tokens, norm_tokens))
    df_norm["D2_Membership_functions_norm"] = norm_membership_values
    norm_interpretability_values: list[str] = []
    synth_notes_p4: list[str] = []
    for raw in df["D2_Interpretability_elements"]:
        raw_tokens = parse_multi_keep_nr(raw)
        norm_tokens = normalize_interpretability_tokens(raw_tokens)
        norm_interpretability_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p4.append(build_synthesis_note_interpretability(raw_tokens, norm_tokens))
    df_norm["D2_Interpretability_elements_norm"] = norm_interpretability_values
    norm_rule_base_values: list[str] = []
    synth_notes_p5: list[str] = []
    for raw in df["D2_Rule_base_definition"]:
        raw_tokens = parse_multi_keep_nr(raw)
        norm_tokens = normalize_rule_base_tokens(raw_tokens)
        norm_rule_base_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p5.append(build_synthesis_note_rule_base(raw_tokens, norm_tokens))
    df_norm["D2_Rule_base_definition_norm"] = norm_rule_base_values
    norm_defuzzification_values: list[str] = []
    synth_notes_p6: list[str] = []
    for raw in df["D2_Defuzzification_method"]:
        raw_tokens = parse_multi_keep_nr(raw)
        norm_tokens = normalize_defuzzification_tokens(raw_tokens)
        norm_defuzzification_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p6.append(build_synthesis_note_defuzzification(raw_tokens, norm_tokens))
    df_norm["D2_Defuzzification_method_norm"] = norm_defuzzification_values
    norm_risk_values: list[str] = []
    synth_notes_p7: list[str] = []
    for raw in df["D2_Risk_modeling_approach"]:
        raw_tokens = parse_multi_keep_nr(raw)
        norm_tokens = normalize_risk_tokens(raw_tokens)
        norm_risk_values.append("; ".join(norm_tokens) if norm_tokens else "NR")
        synth_notes_p7.append(build_synthesis_note_risk(raw_tokens, norm_tokens))
    df_norm["D2_Risk_modeling_approach_norm"] = norm_risk_values

    synthesis_notes_combined: list[str] = []
    for n1, n2, n3, n4, n5, n6, n7 in zip(
        synth_notes_p1, synth_notes_p2, synth_notes_p3, synth_notes_p4, synth_notes_p5, synth_notes_p6, synth_notes_p7
    ):
        parts = [p for p in [n1, n2, n3, n4, n5, n6, n7] if p]
        synthesis_notes_combined.append(" | ".join(parts))
    df_norm["D2_Synthesis_notes"] = synthesis_notes_combined

    notes_df = build_variant_notes(df)
    mapping_df = build_mapping_table()
    notes_df_purpose = build_purpose_variant_notes(df)
    mapping_df_purpose = build_mapping_table_purpose()
    notes_df_membership = build_membership_variant_notes(df)
    mapping_df_membership = build_mapping_table_membership()
    notes_df_interpretability = build_interpretability_variant_notes(df)
    mapping_df_interpretability = build_mapping_table_interpretability()
    notes_df_rule_base = build_rule_base_variant_notes(df)
    mapping_df_rule_base = build_mapping_table_rule_base()
    notes_df_defuzzification = build_defuzzification_variant_notes(df)
    mapping_df_defuzzification = build_mapping_table_defuzzification()
    notes_df_risk = build_risk_variant_notes(df)
    mapping_df_risk = build_mapping_table_risk()

    output_dir.mkdir(parents=True, exist_ok=True)
    df_norm.to_csv(dataset_path, index=False, encoding="utf-8-sig")
    if dataset_path_mirror.exists():
        df_norm.to_csv(dataset_path_mirror, index=False, encoding="utf-8-sig")

    pre_counts.to_csv(output_dir / "d2_p1_fuzzy_approach_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts.to_csv(output_dir / "d2_p1_fuzzy_approach_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df.to_csv(output_dir / "d2_p1_fuzzy_approach_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df.to_csv(output_dir / "d2_p1_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_purpose.to_csv(output_dir / "d2_p2_inference_purpose_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_purpose.to_csv(output_dir / "d2_p2_inference_purpose_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_purpose.to_csv(output_dir / "d2_p2_inference_purpose_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_purpose.to_csv(output_dir / "d2_p2_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_membership.to_csv(output_dir / "d2_p3_membership_functions_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_membership.to_csv(output_dir / "d2_p3_membership_functions_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_membership.to_csv(output_dir / "d2_p3_membership_functions_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_membership.to_csv(output_dir / "d2_p3_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_interpretability.to_csv(output_dir / "d2_p4_interpretability_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_interpretability.to_csv(output_dir / "d2_p4_interpretability_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_interpretability.to_csv(output_dir / "d2_p4_interpretability_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_interpretability.to_csv(output_dir / "d2_p4_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_rule_base.to_csv(output_dir / "d2_p5_rule_base_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_rule_base.to_csv(output_dir / "d2_p5_rule_base_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_rule_base.to_csv(output_dir / "d2_p5_rule_base_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_rule_base.to_csv(output_dir / "d2_p5_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_defuzzification.to_csv(output_dir / "d2_p6_defuzzification_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_defuzzification.to_csv(output_dir / "d2_p6_defuzzification_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_defuzzification.to_csv(output_dir / "d2_p6_defuzzification_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_defuzzification.to_csv(output_dir / "d2_p6_mapping.csv", index=False, encoding="utf-8-sig")
    pre_counts_risk.to_csv(output_dir / "d2_p7_risk_modeling_pre_counts.csv", index=False, encoding="utf-8-sig")
    post_counts_risk.to_csv(output_dir / "d2_p7_risk_modeling_post_counts.csv", index=False, encoding="utf-8-sig")
    notes_df_risk.to_csv(output_dir / "d2_p7_risk_modeling_variant_notes.csv", index=False, encoding="utf-8-sig")
    mapping_df_risk.to_csv(output_dir / "d2_p7_mapping.csv", index=False, encoding="utf-8-sig")

    print("[OK] Salidas D2 Fase 1 / Puntos 1-7")
    print(f"[OK] Dataset actualizado: {dataset_path}")
    if dataset_path_mirror.exists():
        print(f"[OK] Dataset espejo actualizado: {dataset_path_mirror}")
    print(f"[OK] {output_dir / 'd2_p1_fuzzy_approach_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p1_fuzzy_approach_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p1_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p1_fuzzy_approach_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p2_inference_purpose_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p2_inference_purpose_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p2_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p2_inference_purpose_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p3_membership_functions_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p3_membership_functions_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p3_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p3_membership_functions_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p4_interpretability_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p4_interpretability_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p4_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p4_interpretability_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p5_rule_base_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p5_rule_base_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p5_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p5_rule_base_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p6_defuzzification_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p6_defuzzification_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p6_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p6_defuzzification_variant_notes.csv'}")
    print(f"[OK] {output_dir / 'd2_p7_risk_modeling_pre_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p7_risk_modeling_post_counts.csv'}")
    print(f"[OK] {output_dir / 'd2_p7_mapping.csv'}")
    print(f"[OK] {output_dir / 'd2_p7_risk_modeling_variant_notes.csv'}")


if __name__ == "__main__":
    main()
