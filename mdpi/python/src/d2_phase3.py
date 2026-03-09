#!/usr/bin/env python3
"""
Fase 3 (D2) - Trazabilidad y perfiles de diseno.

Genera, desde pandas:
- Tabla de trazabilidad minima D2 (3-5 estudios, campo, valor resumido, evidencia).
- Tabla de perfiles compactos por familia FIS:
  Mamdani, ANFIS, Sugeno/TSK, Hybrid_Fuzzy.

Salidas:
- CSV y LaTeX (longtblr) en es/en.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import pandas as pd
from paths import OUTPUTS_DIR, SYNTHESIS_DATA_DIR


SPLIT_RE = re.compile(r"[;|,]+")
NA_SET = {"", "NA", "N/A", "N/R"}


def read_dataset(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig")


def parse_multi(value: object, include_nr: bool = False) -> list[str]:
    if pd.isna(value):
        return ["NR"] if include_nr else []
    text = str(value).strip()
    if not text:
        return ["NR"] if include_nr else []
    out: list[str] = []
    for token in SPLIT_RE.split(text):
        t = token.strip()
        if not t:
            continue
        t_upper = t.upper()
        if t_upper in NA_SET:
            continue
        if t_upper == "NR":
            if include_nr:
                out.append("NR")
            continue
        out.append(t)
    return list(dict.fromkeys(out))


def col_or_fallback(df: pd.DataFrame, preferred: str, fallback: str) -> str:
    return preferred if preferred in df.columns else fallback


def latex_escape(x: object) -> str:
    if pd.isna(x):
        return ""
    s = str(x)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def write_longtblr(
    df: pd.DataFrame,
    out_path: Path,
    colspec: str,
    label: str,
    caption: str,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out = df.copy()
    for c in df_out.columns:
        df_out[c] = df_out[c].map(latex_escape)
    df_out.columns = [latex_escape(c) for c in df_out.columns]

    lines = [
        r"\begin{longtblr}[",
        r"  entry=none,",
        f"  label={{{label}}},",
        f"  caption={{{caption}}}",
        r"]{",
        f"  colspec={{{colspec}}},",
        r"  width=\textwidth,",
        r"  row{1}={font=\bfseries}",
        r"}",
        " & ".join(df_out.columns) + r" \\",
    ]
    for row in df_out.itertuples(index=False, name=None):
        lines.append(" & ".join(str(v) for v in row) + r" \\")
    lines.append(r"\end{longtblr}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_traceability_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    # 5 estudios representativos de variacion de diseno en D2.
    specs = [
        ("A009", "D2_Defuzzification_method_norm"),
        ("A087", "D2_Membership_functions_norm"),
        ("A149", "D2_Interpretability_elements_norm"),
        ("A168", "D2_Rule_base_definition_norm"),
        ("A142", "D2_Risk_modeling_approach_norm"),
    ]

    idx = df.set_index("Article_ID", drop=False)
    rows: list[tuple[str, str, str, str]] = []
    for aid, field in specs:
        if aid not in idx.index:
            continue
        r = idx.loc[aid]
        value = str(r.get(field, "")).strip()
        ev = str(r.get("Evidence_D2_pages", "")).strip()
        rows.append((aid, field, value, ev))

    if lang == "es":
        cols = ["Article_ID", "Campo", "Valor_resumido", "Evidence_D2_pages"]
    else:
        cols = ["Article_ID", "Field", "Summarized_value", "Evidence_D2_pages"]
    return pd.DataFrame(rows, columns=cols)


def dominant_value(
    df_family: pd.DataFrame,
    col: str,
    multi: bool,
    include_nr: bool = False,
) -> str:
    m = len(df_family)
    if m == 0:
        return "NR"
    counter: Counter[str] = Counter()
    for _, r in df_family[["Article_ID", col]].iterrows():
        if multi:
            vals = parse_multi(r[col], include_nr=include_nr)
        else:
            vals = parse_multi(r[col], include_nr=include_nr)
            if not vals and include_nr:
                vals = ["NR"]
        for v in vals:
            counter[v] += 1
    if not counter:
        return "NR"
    top_k = max(counter.values())
    top_vals = sorted([k for k, v in counter.items() if v == top_k])
    top_label = " / ".join(top_vals[:3])
    if len(top_vals) > 3:
        top_label += " +..."
    pct = round(100.0 * top_k / m, 1)
    return f"{top_label} ({top_k}/{m}; {pct}%)"


def build_profiles_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    fis_col = col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type")
    purpose_col = col_or_fallback(df, "D2_Inference_purpose_norm", "D2_Inference_purpose")
    mf_col = col_or_fallback(df, "D2_Membership_functions_norm", "D2_Membership_functions")
    rb_col = col_or_fallback(df, "D2_Rule_base_definition_norm", "D2_Rule_base_definition")
    defuzz_col = col_or_fallback(df, "D2_Defuzzification_method_norm", "D2_Defuzzification_method")
    risk_col = col_or_fallback(df, "D2_Risk_modeling_approach_norm", "D2_Risk_modeling_approach")
    interp_col = col_or_fallback(df, "D2_Interpretability_elements_norm", "D2_Interpretability_elements")

    families = ["Mamdani", "ANFIS", "Sugeno/TSK", "Hybrid_Fuzzy"]
    rows: list[dict[str, object]] = []

    for fam in families:
        mask = df[fis_col].apply(lambda x: fam in parse_multi(x, include_nr=False))
        sub = df[mask].copy()
        m = len(sub)
        if m == 0:
            continue

        role_dom = dominant_value(sub, "D2_Fuzzy_role", multi=False, include_nr=False)
        purpose_dom = dominant_value(sub, purpose_col, multi=True, include_nr=False)
        mf_dom = dominant_value(sub, mf_col, multi=True, include_nr=False)
        rb_dom = dominant_value(sub, rb_col, multi=False, include_nr=False)
        # En defuzzificacion se excluye NR para reflejar patron reportado;
        # si no hay reportes, queda NR.
        defuzz_dom = dominant_value(sub, defuzz_col, multi=True, include_nr=False)
        risk_dom = dominant_value(sub, risk_col, multi=True, include_nr=False)
        interp_dom = dominant_value(sub, interp_col, multi=True, include_nr=False)

        if lang == "es":
            rows.append({
                "Familia_FIS": fam,
                "m": m,
                "Rol_dominante": role_dom,
                "Proposito_principal": purpose_dom,
                "MF_tipica": mf_dom,
                "Base_reglas": rb_dom,
                "Defuzz_reportada": defuzz_dom,
                "Riesgo_principal": risk_dom,
                "Interpretabilidad_clave": interp_dom,
            })
        else:
            rows.append({
                "FIS_Family": fam,
                "m": m,
                "Dominant_role": role_dom,
                "Main_purpose": purpose_dom,
                "Typical_MF": mf_dom,
                "Rule_base": rb_dom,
                "Reported_defuzz": defuzz_dom,
                "Main_risk": risk_dom,
                "Key_interpretability": interp_dom,
            })

    return pd.DataFrame(rows)


def main() -> None:
    df = read_dataset(SYNTHESIS_DATA_DIR / "dataset.csv")

    out_tab = {
        "es": OUTPUTS_DIR / "tablas" / "d2" / "es",
        "en": OUTPUTS_DIR / "tablas" / "d2" / "en",
    }

    for lang in ["es", "en"]:
        out_tab[lang].mkdir(parents=True, exist_ok=True)

        trace = build_traceability_table(df, lang=lang)
        prof = build_profiles_table(df, lang=lang)

        trace_csv = out_tab[lang] / f"d2_tabla_trazabilidad_minima_{lang}.csv"
        trace_tex = out_tab[lang] / f"d2_tabla_trazabilidad_minima_{lang}.tex"
        prof_csv = out_tab[lang] / f"d2_tabla_perfiles_fis_{lang}.csv"
        prof_tex = out_tab[lang] / f"d2_tabla_perfiles_fis_{lang}.tex"

        trace.to_csv(trace_csv, index=False, encoding="utf-8-sig")
        prof.to_csv(prof_csv, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                trace,
                trace_tex,
                "X[0.8,l,m] X[1.35,l,m] X[2.6,l,m] X[1.0,l,m]",
                "tab:d2_trazabilidad_minima",
                r"Directriz D2: trazabilidad mínima de evidencia por estudio y campo. Elaboración propia.",
            )
            write_longtblr(
                prof,
                prof_tex,
                "X[0.9,l,m] X[0.35,c,m] X[1.1,l,m] X[1.5,l,m] X[1.1,l,m] X[1.1,l,m] X[1.1,l,m] X[1.1,l,m] X[1.3,l,m]",
                "tab:d2_perfiles_fis",
                r"Directriz D2: perfiles compactos de diseño por familia FIS (m sobre n=19). Elaboración propia.",
            )
        else:
            write_longtblr(
                trace,
                trace_tex,
                "X[0.8,l,m] X[1.35,l,m] X[2.6,l,m] X[1.0,l,m]",
                "tab:d2_minimum_traceability",
                "Guideline D2: minimum evidence traceability by study and field.",
            )
            write_longtblr(
                prof,
                prof_tex,
                "X[0.9,l,m] X[0.35,c,m] X[1.1,l,m] X[1.5,l,m] X[1.1,l,m] X[1.1,l,m] X[1.1,l,m] X[1.1,l,m] X[1.3,l,m]",
                "tab:d2_fis_profiles",
                "Guideline D2: compact design profiles by FIS family (m over n=19).",
            )

        print(f"[OK] Trazabilidad CSV: {trace_csv}")
        print(f"[OK] Trazabilidad TEX: {trace_tex}")
        print(f"[OK] Perfiles CSV: {prof_csv}")
        print(f"[OK] Perfiles TEX: {prof_tex}")


if __name__ == "__main__":
    main()
