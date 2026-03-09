#!/usr/bin/env python3
"""
Fase 4 (D3) - Construccion de perfiles de plataforma.

Genera:
- Tabla compacta de perfiles por familia de arquitectura:
  Arquitectura -> Configuracion tipica de plataforma.

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


def top_profile_value(
    df_family: pd.DataFrame,
    col: str,
    top_n: int = 2,
    include_nr: bool = False,
) -> str:
    m = len(df_family)
    if m == 0:
        return "NR"

    counter: Counter[str] = Counter()
    for _, r in df_family[["Article_ID", col]].iterrows():
        vals = parse_multi(r[col], include_nr=include_nr)
        for v in vals:
            counter[v] += 1

    if not counter:
        return "NR"

    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    parts: list[str] = []
    for name, k in items:
        pct = round(100.0 * float(k) / float(m), 1)
        parts.append(f"{name} ({k}/{m}; {pct}%)")
    return " / ".join(parts)


def build_profiles_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    arch_col = col_or_fallback(df, "D3_Platform_architecture_norm", "D3_Platform_architecture")
    proc_col = col_or_fallback(df, "D3_Processing_mode_norm", "D3_Processing_mode")
    comm_col = col_or_fallback(df, "D3_Communication_and_tech_norm", "D3_Communication_and_tech")
    vis_col = col_or_fallback(df, "D3_Visualization_alerting_norm", "D3_Visualization_alerting")
    dep_col = col_or_fallback(df, "D3_Deployment_context_norm", "D3_Deployment_context")
    hw_col = col_or_fallback(df, "D3_Hardware_and_sensors_norm", "D3_Hardware_and_sensors")
    rt_col = col_or_fallback(df, "D3_Real_time_characteristics_norm", "D3_Real_time_characteristics")

    families: list[tuple[str, set[str]]] = [
        ("IoT_Edge_Cloud", {"IoT_Edge_Cloud", "IoT_Fog_Layered"}),
        ("IoT_2Tier", {"IoT_2Tier"}),
        ("Otros/Hybrid", {"WSN_Pipeline", "Sensor_Node_External_Analytics", "Standalone_Node_PC"}),
    ]

    # Solo agregar Cloud_Centric si aparece.
    cloud_mask = df[arch_col].apply(lambda x: "Cloud_Centric" in parse_multi(x, include_nr=False))
    if int(cloud_mask.sum()) > 0:
        families.insert(2, ("Cloud_Centric", {"Cloud_Centric"}))

    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []

    for fam_name, tokens in families:
        mask = df[arch_col].apply(lambda x: bool(set(parse_multi(x, include_nr=False)).intersection(tokens)))
        sub = df[mask].copy()
        m = len(sub)
        if m == 0:
            continue

        proc = top_profile_value(sub, proc_col, top_n=2, include_nr=False)
        comm = top_profile_value(sub, comm_col, top_n=2, include_nr=False)
        vis = top_profile_value(sub, vis_col, top_n=2, include_nr=False)
        dep = top_profile_value(sub, dep_col, top_n=2, include_nr=False)
        hw = top_profile_value(sub, hw_col, top_n=2, include_nr=False)
        rt = top_profile_value(sub, rt_col, top_n=2, include_nr=False)

        if lang == "es":
            rows_es.append({
                "Familia_arquitectura": fam_name,
                "m": m,
                "Procesamiento_dominante": proc,
                "Stack_recurrente": comm,
                "Visualizacion_alerta_tipica": vis,
                "Contexto_despliegue_dominante": dep,
                "Hardware_sensores_tipicos": hw,
                "Rasgo_tiempo_real": rt,
            })
        else:
            rows_en.append({
                "Architecture_family": fam_name,
                "m": m,
                "Dominant_processing": proc,
                "Recurrent_stack": comm,
                "Typical_visual_alerting": vis,
                "Dominant_deployment_context": dep,
                "Typical_hardware_sensors": hw,
                "Real_time_trait": rt,
            })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def main() -> None:
    df = read_dataset(SYNTHESIS_DATA_DIR / "dataset.csv")

    out_tab = {
        "es": OUTPUTS_DIR / "tablas" / "d3" / "es",
        "en": OUTPUTS_DIR / "tablas" / "d3" / "en",
    }

    for lang in ["es", "en"]:
        out_tab[lang].mkdir(parents=True, exist_ok=True)
        prof = build_profiles_table(df, lang=lang)

        csv_path = out_tab[lang] / f"d3_tabla_perfiles_plataforma_{lang}.csv"
        tex_path = out_tab[lang] / f"d3_tabla_perfiles_plataforma_{lang}.tex"
        prof.to_csv(csv_path, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                prof,
                tex_path,
                "X[0.9,l,m] X[0.3,c,m] X[1.3,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m]",
                "tab:d3_perfiles_plataforma",
                r"Directriz D3: perfiles compactos por familia de arquitectura (m sobre n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                prof,
                tex_path,
                "X[0.9,l,m] X[0.3,c,m] X[1.3,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m] X[1.2,l,m]",
                "tab:d3_platform_profiles",
                "Guideline D3: compact profiles by architecture family (m over n=19).",
            )

        print(f"[OK] Perfiles CSV: {csv_path}")
        print(f"[OK] Perfiles TEX: {tex_path}")


if __name__ == "__main__":
    main()
