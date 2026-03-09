#!/usr/bin/env python3
"""
Fase 1.2 (D3) - Estadistica descriptiva basica.

Genera:
- Tabla principal D3 (k/n/%; n=19) en CSV y LaTeX (longtblr).
- Tabla de completitud NR por dimension en CSV y LaTeX (longtblr).

Salidas en dos variantes:
- es: uso en informe
- en: uso de trabajo en Python
"""

from __future__ import annotations

from pathlib import Path
import re
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from paths import OUTPUTS_DIR, SYNTHESIS_DATA_DIR


SPLIT_RE = re.compile(r"[;|,]+")
NA_SET = {"", "NA", "N/A", "N/R"}


def setup_style() -> None:
    sns.set_theme(style="whitegrid", context="paper", palette="Set2")
    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": 320,
        "font.size": 12,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "text.usetex": False,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "axes.titleweight": "semibold",
        "legend.fontsize": 10,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#4d4d4d",
        "axes.linewidth": 0.8,
        "grid.alpha": 0.35,
    })


def save_fig(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def read_dataset(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig")


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


def concept_label(x: object) -> str:
    s = str(x).strip()
    if not s:
        return s
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def wrap_label(x: object, width: int = 16) -> str:
    s = concept_label(x)
    if not s:
        return s
    return "\n".join(
        textwrap.wrap(
            s,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def style_ticklabels(ax: plt.Axes, axis: str, wrap_width: int = 16) -> None:
    if axis == "x":
        labels = [t.get_text() for t in ax.get_xticklabels()]
    else:
        labels = [t.get_text() for t in ax.get_yticklabels()]

    pretty = [wrap_label(lbl, width=wrap_width) for lbl in labels]
    raw_lengths = [len(concept_label(lbl)) for lbl in labels if str(lbl).strip()]
    dense = len(labels) >= 9
    very_long = any(l > 18 for l in raw_lengths)
    rotation = 90 if (dense or very_long) else 0

    if axis == "x":
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(pretty, rotation=rotation, ha=("right" if rotation == 90 else "center"))
    else:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(pretty, rotation=0)


def counts_per_dimension(
    df: pd.DataFrame,
    id_col: str,
    dimension: str,
    col: str,
) -> pd.DataFrame:
    n = int(df[id_col].nunique())
    rows: list[tuple[str, str]] = []

    for _, r in df[[id_col, col]].iterrows():
        vals = parse_multi(r[col], include_nr=False)
        for v in vals:
            rows.append((str(r[id_col]), v))

    if not rows:
        return pd.DataFrame(columns=["Dimension", "Categoria", "k", "n", "%"])

    long = pd.DataFrame(rows, columns=[id_col, "Categoria"]).drop_duplicates()
    k = long.groupby("Categoria")[id_col].nunique().sort_values(ascending=False)
    out = pd.DataFrame({
        "Dimension": dimension,
        "Categoria": k.index,
        "k": k.values.astype(int),
        "n": n,
    })
    out["%"] = (out["k"] * 100.0 / n).round(1)
    return out


def nr_per_dimension(df: pd.DataFrame, id_col: str, dimension: str, col: str) -> dict[str, object]:
    n = int(df[id_col].nunique())
    nr_articles = 0

    for _, r in df[[id_col, col]].iterrows():
        vals = parse_multi(r[col], include_nr=True)
        if "NR" in vals or len([v for v in vals if v != "NR"]) == 0:
            nr_articles += 1

    return {
        "Dimension": dimension,
        "Columna": col,
        "NR_articulos": int(nr_articles),
        "n": n,
        "%_NR": round(100.0 * float(nr_articles) / float(n), 1),
    }


def build_tables(df: pd.DataFrame, lang: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    id_col = "Article_ID"
    dims = [
        ("Arquitectura de plataforma", "D3_Platform_architecture_norm", "D3_Platform_architecture"),
        ("Modo de procesamiento", "D3_Processing_mode_norm", "D3_Processing_mode"),
        ("Comunicacion/tecnologia", "D3_Communication_and_tech_norm", "D3_Communication_and_tech"),
        ("Visualizacion y alertamiento", "D3_Visualization_alerting_norm", "D3_Visualization_alerting"),
        ("Contexto de despliegue", "D3_Deployment_context_norm", "D3_Deployment_context"),
        ("Hardware y sensores", "D3_Hardware_and_sensors_norm", "D3_Hardware_and_sensors"),
        ("Operacion en tiempo real", "D3_Real_time_characteristics_norm", "D3_Real_time_characteristics"),
    ]

    if lang == "en":
        dim_map = {
            "Arquitectura de plataforma": "Platform architecture",
            "Modo de procesamiento": "Processing mode",
            "Comunicacion/tecnologia": "Communication/technology",
            "Visualizacion y alertamiento": "Visualization and alerting",
            "Contexto de despliegue": "Deployment context",
            "Hardware y sensores": "Hardware and sensors",
            "Operacion en tiempo real": "Real-time operation",
        }
    else:
        dim_map = {d[0]: d[0] for d in dims}

    main_rows: list[pd.DataFrame] = []
    nr_rows: list[dict[str, object]] = []

    for dim_es, pref, raw in dims:
        col = col_or_fallback(df, pref, raw)
        dim_name = dim_map[dim_es]

        t = counts_per_dimension(df, id_col, dim_name, col)
        t = t[t["Categoria"] != "NR"].copy()
        main_rows.append(t)

        nr_rows.append(nr_per_dimension(df, id_col, dim_name, col))

    main = pd.concat(main_rows, ignore_index=True)
    nr = pd.DataFrame(nr_rows)

    if lang == "en":
        main = main.rename(columns={"Categoria": "Category"})
        nr = nr.rename(columns={"Columna": "Column", "NR_articulos": "NR_articles", "%_NR": "NR_%"})
        main = main[["Dimension", "Category", "k", "n", "%"]]
        nr = nr[["Dimension", "Column", "NR_articles", "n", "NR_%"]]
    else:
        main = main[["Dimension", "Categoria", "k", "n", "%"]]
        nr = nr[["Dimension", "Columna", "NR_articulos", "n", "%_NR"]]

    return main, nr


def onehot(df: pd.DataFrame, id_col: str, col: str) -> pd.DataFrame:
    rows: list[tuple[str, str]] = []
    for _, r in df[[id_col, col]].iterrows():
        vals = parse_multi(r[col], include_nr=False)
        for v in vals:
            rows.append((str(r[id_col]), v))
    if not rows:
        return pd.DataFrame()
    long = pd.DataFrame(rows, columns=[id_col, "item"]).drop_duplicates()
    return (pd.crosstab(long[id_col], long["item"]) > 0).astype(int)


def plot_architecture_distribution(df: pd.DataFrame, out_dir: Path, lang: str) -> None:
    col_arch = col_or_fallback(df, "D3_Platform_architecture_norm", "D3_Platform_architecture")
    arch = onehot(df, "Article_ID", col_arch)
    if arch.empty:
        return

    arch_counts = arch.sum(axis=0).sort_values(ascending=True)
    y_labels = [wrap_label(x, width=18) for x in arch_counts.index]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    set2 = sns.color_palette("Set2", 8)
    ax.barh(y_labels, arch_counts.values, color=set2[0], edgecolor="#4d4d4d", linewidth=0.6)
    for i, v in enumerate(arch_counts.values):
        ax.text(v + 0.1, i, str(int(v)), va="center")

    if lang == "es":
        ax.set_xlabel("Numero de estudios")
        ax.set_ylabel("")
    else:
        ax.set_xlabel("Number of studies")
        ax.set_ylabel("")

    fig.tight_layout()
    save_fig(fig, out_dir, "fig01_distribucion_arquitectura")


def plot_processing_distribution(df: pd.DataFrame, out_dir: Path, lang: str) -> None:
    col_proc = col_or_fallback(df, "D3_Processing_mode_norm", "D3_Processing_mode")
    proc = onehot(df, "Article_ID", col_proc)
    if proc.empty:
        return

    proc_counts = proc.sum(axis=0).sort_values(ascending=True)
    y_labels = [wrap_label(x, width=18) for x in proc_counts.index]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    set2 = sns.color_palette("Set2", 8)
    ax.barh(y_labels, proc_counts.values, color=set2[1], edgecolor="#4d4d4d", linewidth=0.6)
    for i, v in enumerate(proc_counts.values):
        ax.text(v + 0.1, i, str(int(v)), va="center")

    if lang == "es":
        ax.set_xlabel("Numero de estudios")
        ax.set_ylabel("")
    else:
        ax.set_xlabel("Number of studies")
        ax.set_ylabel("")

    fig.tight_layout()
    save_fig(fig, out_dir, "fig02_distribucion_procesamiento")


def plot_cooccurrence_heatmap(
    df: pd.DataFrame,
    out_dir: Path,
    col_left: str,
    col_right: str,
    stem: str,
    title_es: str,
    title_en: str,
    xlabel_es: str,
    xlabel_en: str,
    ylabel_es: str,
    ylabel_en: str,
    lang: str,
    top_n: int = 12,
) -> None:
    A = onehot(df, "Article_ID", col_left)
    B = onehot(df, "Article_ID", col_right)
    if A.empty or B.empty:
        return
    idx = A.index.intersection(B.index)
    if len(idx) == 0:
        return

    M = A.loc[idx].T.dot(B.loc[idx])
    row_order = M.sum(axis=1).sort_values(ascending=False).head(top_n).index
    col_order = M.sum(axis=0).sort_values(ascending=False).head(top_n).index
    M2 = M.loc[row_order, col_order]
    M2.index = [wrap_label(x, width=18) for x in M2.index]
    M2.columns = [wrap_label(x, width=16) for x in M2.columns]

    fig, ax = plt.subplots(figsize=(9.8, 6.2))
    sns.heatmap(M2, annot=True, fmt="d", linewidths=0.4, linecolor="#d0d0d0", cmap="Blues", ax=ax)
    if lang == "es":
        ax.set_xlabel(xlabel_es)
        ax.set_ylabel(ylabel_es)
    else:
        ax.set_xlabel(xlabel_en)
        ax.set_ylabel(ylabel_en)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)
    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def main() -> None:
    df = read_dataset(SYNTHESIS_DATA_DIR / "dataset.csv")
    setup_style()

    out_tab = {
        "es": OUTPUTS_DIR / "tablas" / "d3" / "es",
        "en": OUTPUTS_DIR / "tablas" / "d3" / "en",
    }
    out_fig = {
        "es": OUTPUTS_DIR / "figuras" / "d3" / "es",
        "en": OUTPUTS_DIR / "figuras" / "d3" / "en",
    }

    for lang in ["es", "en"]:
        out_tab[lang].mkdir(parents=True, exist_ok=True)
        out_fig[lang].mkdir(parents=True, exist_ok=True)
        main_table, nr_table = build_tables(df, lang=lang)

        main_csv = out_tab[lang] / f"d3_tabla_principal_{lang}.csv"
        main_tex = out_tab[lang] / f"d3_tabla_principal_{lang}.tex"
        nr_csv = out_tab[lang] / f"d3_tabla_completitud_nr_{lang}.csv"
        nr_tex = out_tab[lang] / f"d3_tabla_completitud_nr_{lang}.tex"

        main_table.to_csv(main_csv, index=False, encoding="utf-8-sig")
        nr_table.to_csv(nr_csv, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                main_table,
                main_tex,
                "X[1.5,l,m] X[2.0,l,m] X[0.55,c,m] X[0.55,c,m] X[0.7,c,m]",
                "tab:d3_tabla_principal",
                r"Directriz D3: tabla principal de evidencia cuantitativa (k/n/\%; n=19). Elaboracion propia.",
            )
            write_longtblr(
                nr_table,
                nr_tex,
                "X[1.6,l,m] X[1.8,l,m] X[0.7,c,m] X[0.55,c,m] X[0.8,c,m]",
                "tab:d3_tabla_completitud_nr",
                r"Directriz D3: completitud por dimension critica (NR sobre n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                main_table,
                main_tex,
                "X[1.5,l,m] X[2.0,l,m] X[0.55,c,m] X[0.55,c,m] X[0.7,c,m]",
                "tab:d3_main_table",
                "Guideline D3: main quantitative evidence table (k/n/%; n=19).",
            )
            write_longtblr(
                nr_table,
                nr_tex,
                "X[1.6,l,m] X[1.8,l,m] X[0.7,c,m] X[0.55,c,m] X[0.8,c,m]",
                "tab:d3_nr_completeness",
                "Guideline D3: completeness by critical dimension (NR over n=19).",
            )

        print(f"[OK] Tabla principal CSV: {main_csv}")
        print(f"[OK] Tabla principal TEX: {main_tex}")
        print(f"[OK] Tabla completitud NR CSV: {nr_csv}")
        print(f"[OK] Tabla completitud NR TEX: {nr_tex}")

        # Figuras D3 (Fase 2).
        plot_architecture_distribution(df, out_fig[lang], lang)
        plot_processing_distribution(df, out_fig[lang], lang)
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D3_Platform_architecture_norm", "D3_Platform_architecture"),
            col_right=col_or_fallback(df, "D3_Processing_mode_norm", "D3_Processing_mode"),
            stem="fig03_coocurrencia_arquitectura_vs_procesamiento",
            title_es="Coocurrencia: Arquitectura vs Procesamiento",
            title_en="Co-Occurrence: Architecture vs Processing",
            xlabel_es="Modo de procesamiento",
            xlabel_en="Processing mode",
            ylabel_es="Arquitectura",
            ylabel_en="Architecture",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D3_Platform_architecture_norm", "D3_Platform_architecture"),
            col_right=col_or_fallback(df, "D3_Communication_and_tech_norm", "D3_Communication_and_tech"),
            stem="fig04_coocurrencia_arquitectura_vs_stack",
            title_es="Coocurrencia: Arquitectura vs Stack Tecnologico (Top)",
            title_en="Co-Occurrence: Architecture vs Technology Stack (Top)",
            xlabel_es="Comunicacion/tecnologia",
            xlabel_en="Communication/technology",
            ylabel_es="Arquitectura",
            ylabel_en="Architecture",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D3_Deployment_context_norm", "D3_Deployment_context"),
            col_right=col_or_fallback(df, "D3_Hardware_and_sensors_norm", "D3_Hardware_and_sensors"),
            stem="fig05_coocurrencia_contexto_vs_instrumentacion",
            title_es="Coocurrencia: Contexto de Despliegue vs Instrumentacion (Top)",
            title_en="Co-Occurrence: Deployment Context vs Instrumentation (Top)",
            xlabel_es="Hardware/sensores",
            xlabel_en="Hardware/sensors",
            ylabel_es="Contexto de despliegue",
            ylabel_en="Deployment context",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D3_Real_time_characteristics_norm", "D3_Real_time_characteristics"),
            col_right=col_or_fallback(df, "D3_Visualization_alerting_norm", "D3_Visualization_alerting"),
            stem="fig06_coocurrencia_tiempo_real_vs_visualizacion",
            title_es="Coocurrencia: Tiempo Real vs Visualizacion/Alerta (Top)",
            title_en="Co-Occurrence: Real-Time vs Visualization/Alerting (Top)",
            xlabel_es="Visualizacion/alertamiento",
            xlabel_en="Visualization/alerting",
            ylabel_es="Operacion en tiempo real",
            ylabel_en="Real-time operation",
            lang=lang,
        )

        print(f"[OK] Figuras D3: {out_fig[lang]}")


if __name__ == "__main__":
    main()
