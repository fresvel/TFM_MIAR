#!/usr/bin/env python3
"""
Fase 2 (D2) - Evidencia cuantitativa y visual compacta.

Genera, desde pandas:
- Tabla principal D2 (k/n/%; n=19) en CSV y LaTeX (longtblr).
- Tabla de completitud NR por dimension.
- Figuras D2:
  1) Distribucion de tipos de FIS
  2) Coocurrencia estrategica (Tipo FIS x Proposito)
  3) Resumen de clases AQI (conteo de clases y etiquetas mas frecuentes)
  4) Coocurrencia (Tipo FIS x Defuzzificacion)
  5) Coocurrencia (Tipo FIS x Modelado de riesgo)
  6) Coocurrencia (Proposito x Interpretabilidad)
  7) Coocurrencia (Tipo FIS x Membership Functions)

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


def read_dataset(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig")


def save_fig(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


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
    # deduplicar por estudio
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
    include_nr: bool,
) -> tuple[pd.DataFrame, dict[str, int]]:
    n = int(df[id_col].nunique())
    rows: list[tuple[str, str]] = []
    nr_articles = 0
    for _, r in df[[id_col, col]].iterrows():
        vals = parse_multi(r[col], include_nr=include_nr)
        if include_nr:
            if vals == ["NR"] or len(vals) == 0:
                nr_articles += 1
        else:
            if len(vals) == 0:
                nr_articles += 1
        for v in vals:
            rows.append((str(r[id_col]), v))

    if not rows:
        out = pd.DataFrame(columns=["Dimension", "Categoria", "k", "n", "%"])
        return out, {"nr_articles": nr_articles, "n": n}

    long = pd.DataFrame(rows, columns=[id_col, "Categoria"])
    k = long.groupby("Categoria")[id_col].nunique().sort_values(ascending=False)
    out = pd.DataFrame({
        "Dimension": dimension,
        "Categoria": k.index,
        "k": k.values.astype(int),
        "n": n,
    })
    out["%"] = (out["k"] * 100.0 / n).round(1)
    return out, {"nr_articles": nr_articles, "n": n}


def build_main_table(df: pd.DataFrame, lang: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    id_col = "Article_ID"
    dims = [
        ("Tipo de FIS", "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type", False),
        ("Rol difuso", "D2_Fuzzy_role", "D2_Fuzzy_role", False),
        ("Proposito de inferencia", "D2_Inference_purpose_norm", "D2_Inference_purpose", False),
        ("Base de reglas", "D2_Rule_base_definition_norm", "D2_Rule_base_definition", False),
        ("Funciones de pertenencia", "D2_Membership_functions_norm", "D2_Membership_functions", False),
        ("Defuzzificacion", "D2_Defuzzification_method_norm", "D2_Defuzzification_method", True),
        ("Modelado de riesgo", "D2_Risk_modeling_approach_norm", "D2_Risk_modeling_approach", False),
        ("Interpretabilidad", "D2_Interpretability_elements_norm", "D2_Interpretability_elements", False),
    ]

    if lang == "en":
        dim_map = {
            "Tipo de FIS": "FIS Type",
            "Rol difuso": "Fuzzy Role",
            "Proposito de inferencia": "Inference Purpose",
            "Base de reglas": "Rule Base",
            "Funciones de pertenencia": "Membership Functions",
            "Defuzzificacion": "Defuzzification",
            "Modelado de riesgo": "Risk Modeling",
            "Interpretabilidad": "Interpretability",
        }
    else:
        dim_map = {d[0]: d[0] for d in dims}

    all_rows: list[pd.DataFrame] = []
    comp_rows: list[dict[str, object]] = []

    for dim_es, pref, raw, include_nr in dims:
        col = col_or_fallback(df, pref, raw)
        dim_name = dim_map[dim_es]
        t, comp = counts_per_dimension(df, id_col, dim_name, col, include_nr=include_nr)
        if not include_nr:
            t = t[t["Categoria"] != "NR"].copy()
        all_rows.append(t)
        comp_rows.append({
            "Dimension": dim_name,
            "Columna": col,
            "NR_articulos": int(comp["nr_articles"]),
            "n": int(comp["n"]),
            "%_NR": round(100.0 * float(comp["nr_articles"]) / float(comp["n"]), 1),
            "NR_en_tabla_principal": "Si" if include_nr and lang == "es" else (
                "Yes" if include_nr else ("No" if lang == "en" else "No")
            ),
        })

    main = pd.concat(all_rows, ignore_index=True)
    comp = pd.DataFrame(comp_rows)

    if lang == "es":
        main = main[["Dimension", "Categoria", "k", "n", "%"]]
    else:
        main = main.rename(columns={"Categoria": "Category", "Dimension": "Dimension"})
        main = main[["Dimension", "Category", "k", "n", "%"]]

    return main, comp


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


def plot_fis_distribution(df: pd.DataFrame, out_dir: Path, lang: str) -> None:
    col = col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type")
    oh = onehot(df, "Article_ID", col)
    if oh.empty:
        return
    counts = oh.sum(axis=0).sort_values(ascending=True)
    y_labels = [wrap_label(x, width=18) for x in counts.index]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    sns.barplot(x=counts.values, y=y_labels, ax=ax)
    if lang == "es":
        ax.set_title("Distribucion de Tipos de FIS")
        ax.set_xlabel("Numero de estudios")
    else:
        ax.set_title("Distribution of FIS Types")
        ax.set_xlabel("Number of Studies")
    ax.set_ylabel("")
    for i, v in enumerate(counts.values):
        ax.text(v + 0.15, i, str(int(v)), va="center")
    fig.tight_layout()
    save_fig(fig, out_dir, "fig01_distribucion_tipos_fis")


def plot_fis_vs_purpose(df: pd.DataFrame, out_dir: Path, lang: str, top_n: int = 12) -> None:
    col_fis = col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type")
    col_pur = col_or_fallback(df, "D2_Inference_purpose_norm", "D2_Inference_purpose")
    A = onehot(df, "Article_ID", col_fis)
    B = onehot(df, "Article_ID", col_pur)
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
        ax.set_title("Coocurrencia Estrategica: Tipo de FIS vs Proposito")
        ax.set_xlabel("Proposito de inferencia")
        ax.set_ylabel("Tipo de FIS")
    else:
        ax.set_title("Strategic Co-Occurrence: FIS Type vs Purpose")
        ax.set_xlabel("Inference Purpose")
        ax.set_ylabel("FIS Type")
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)
    fig.tight_layout()
    save_fig(fig, out_dir, "fig02_coocurrencia_fis_vs_proposito")


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
        ax.set_title(title_es)
        ax.set_xlabel(xlabel_es)
        ax.set_ylabel(ylabel_es)
    else:
        ax.set_title(title_en)
        ax.set_xlabel(xlabel_en)
        ax.set_ylabel(ylabel_en)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)
    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_aqi_summary(df: pd.DataFrame, out_dir: Path, lang: str) -> None:
    labels_col = "D2_AQI_class_labels"
    count_col = "D2_AQI_class_count"
    if labels_col not in df.columns or count_col not in df.columns:
        return

    # Panel A: distribucion de numero de clases AQI reportadas por estudio.
    count_series = pd.to_numeric(df[count_col], errors="coerce").dropna().astype(int)
    count_dist = count_series.value_counts().sort_index()

    # Panel B: frecuencia de etiquetas AQI reportadas.
    rows: list[tuple[str, str]] = []
    for _, r in df[["Article_ID", labels_col]].iterrows():
        vals = parse_multi(r[labels_col], include_nr=False)
        for v in vals:
            rows.append((str(r["Article_ID"]), v))
    label_counts = pd.Series(dtype=int)
    if rows:
        long = pd.DataFrame(rows, columns=["Article_ID", "label"]).drop_duplicates()
        label_counts = long.groupby("label")["Article_ID"].nunique().sort_values(ascending=False).head(10)

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8))
    ax1, ax2 = axes

    if not count_dist.empty:
        sns.barplot(x=count_dist.index.astype(str), y=count_dist.values, ax=ax1)
    if lang == "es":
        ax1.set_title("Numero de Clases AQI por Estudio")
        ax1.set_xlabel("Clases AQI reportadas")
        ax1.set_ylabel("Numero de estudios")
    else:
        ax1.set_title("Number of AQI Classes per Study")
        ax1.set_xlabel("Reported AQI Classes")
        ax1.set_ylabel("Number of Studies")
    for i, v in enumerate(count_dist.values):
        ax1.text(i, v + 0.1, str(int(v)), ha="center", va="bottom", fontsize=9)

    if not label_counts.empty:
        y_labels = [wrap_label(x, width=18) for x in label_counts.index]
        sns.barplot(x=label_counts.values, y=y_labels, ax=ax2)
    if lang == "es":
        ax2.set_title("Etiquetas AQI Mas Reportadas")
        ax2.set_xlabel("Numero de estudios")
        ax2.set_ylabel("")
    else:
        ax2.set_title("Most Reported AQI Labels")
        ax2.set_xlabel("Number of Studies")
        ax2.set_ylabel("")
    for i, v in enumerate(label_counts.values):
        ax2.text(v + 0.1, i, str(int(v)), va="center")

    fig.tight_layout()
    save_fig(fig, out_dir, "fig03_resumen_clases_aqi")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir / "assets" / "sintesis" / "dataset.csv"
    df = read_dataset(dataset_path)
    setup_style()

    out_base = script_dir / "salidas"
    out_fig = {
        "es": out_base / "figuras" / "d2" / "es",
        "en": out_base / "figuras" / "d2" / "en",
    }
    out_tab = {
        "es": out_base / "tablas" / "d2" / "es",
        "en": out_base / "tablas" / "d2" / "en",
    }

    for lang in ["es", "en"]:
        # Tabla principal y completitud.
        main_table, nr_table = build_main_table(df, lang=lang)
        out_tab[lang].mkdir(parents=True, exist_ok=True)

        main_csv = out_tab[lang] / f"d2_tabla_principal_{lang}.csv"
        main_tex = out_tab[lang] / f"d2_tabla_principal_{lang}.tex"
        nr_csv = out_tab[lang] / f"d2_tabla_completitud_nr_{lang}.csv"

        main_table.to_csv(main_csv, index=False, encoding="utf-8-sig")
        nr_table.to_csv(nr_csv, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                main_table,
                main_tex,
                "X[1.2,l,m] X[1.8,l,m] X[0.5,c,m] X[0.5,c,m] X[0.6,c,m]",
                "tab:d2_tabla_principal",
                r"Directriz D2: tabla principal de evidencia cuantitativa (k/n/\%; n=19). Elaboración propia.",
            )
        else:
            write_longtblr(
                main_table,
                main_tex,
                "X[1.2,l,m] X[1.8,l,m] X[0.5,c,m] X[0.5,c,m] X[0.6,c,m]",
                "tab:d2_main_table",
                "Guideline D2: main quantitative evidence table (k/n/%; n=19).",
            )

        # Figuras D2.
        out_fig[lang].mkdir(parents=True, exist_ok=True)
        plot_fis_distribution(df, out_fig[lang], lang)
        plot_fis_vs_purpose(df, out_fig[lang], lang)
        plot_aqi_summary(df, out_fig[lang], lang)
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type"),
            col_right=col_or_fallback(df, "D2_Defuzzification_method_norm", "D2_Defuzzification_method"),
            stem="fig04_coocurrencia_fis_vs_defuzzificacion",
            title_es="Coocurrencia Estrategica: Tipo de FIS vs Defuzzificacion",
            title_en="Strategic Co-Occurrence: FIS Type vs Defuzzification",
            xlabel_es="Defuzzificacion",
            xlabel_en="Defuzzification",
            ylabel_es="Tipo de FIS",
            ylabel_en="FIS Type",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type"),
            col_right=col_or_fallback(df, "D2_Risk_modeling_approach_norm", "D2_Risk_modeling_approach"),
            stem="fig05_coocurrencia_fis_vs_riesgo",
            title_es="Coocurrencia Estrategica: Tipo de FIS vs Modelado de Riesgo",
            title_en="Strategic Co-Occurrence: FIS Type vs Risk Modeling",
            xlabel_es="Modelado de riesgo",
            xlabel_en="Risk modeling",
            ylabel_es="Tipo de FIS",
            ylabel_en="FIS Type",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D2_Inference_purpose_norm", "D2_Inference_purpose"),
            col_right=col_or_fallback(df, "D2_Interpretability_elements_norm", "D2_Interpretability_elements"),
            stem="fig06_coocurrencia_proposito_vs_interpretabilidad",
            title_es="Coocurrencia Estrategica: Proposito vs Interpretabilidad",
            title_en="Strategic Co-Occurrence: Purpose vs Interpretability",
            xlabel_es="Interpretabilidad",
            xlabel_en="Interpretability",
            ylabel_es="Proposito de inferencia",
            ylabel_en="Inference purpose",
            lang=lang,
        )
        plot_cooccurrence_heatmap(
            df=df,
            out_dir=out_fig[lang],
            col_left=col_or_fallback(df, "D2_Fuzzy_approach_type_norm", "D2_Fuzzy_approach_type"),
            col_right=col_or_fallback(df, "D2_Membership_functions_norm", "D2_Membership_functions"),
            stem="fig07_coocurrencia_fis_vs_mf",
            title_es="Coocurrencia Estrategica: Tipo de FIS vs Funciones de Pertenencia",
            title_en="Strategic Co-Occurrence: FIS Type vs Membership Functions",
            xlabel_es="Funciones de pertenencia",
            xlabel_en="Membership functions",
            ylabel_es="Tipo de FIS",
            ylabel_en="FIS Type",
            lang=lang,
        )

        print(f"[OK] Tabla principal CSV: {main_csv}")
        print(f"[OK] Tabla principal TEX: {main_tex}")
        print(f"[OK] Tabla NR CSV: {nr_csv}")
        print(f"[OK] Figuras: {out_fig[lang]}")


if __name__ == "__main__":
    main()
