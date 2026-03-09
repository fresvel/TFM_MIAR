#!/usr/bin/env python3
"""
Fase 3 - Sintesis D1

Genera figuras en dos variantes de idioma:
- Espanol: para uso en el informe
- English: carpeta ordenada para trabajo en Python

Tambien genera tablas LaTeX:
- Tabla resumen D1 (k/n/%)
- Tabla de trazabilidad minima D1
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import re
import shutil
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# =========================
# ESTILO
# =========================
def setup_style():
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


def save_fig(fig, out_dir: Path, stem: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def read_dataset_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig")


# =========================
# UTILIDADES
# =========================
_SPLIT_RE = re.compile(r"[;,\|/]+")


def parse_list_cell(x):
    if isinstance(x, pd.Series):
        x = "; ".join(str(v) for v in x.tolist())
    if pd.isna(x):
        return []
    s = str(x).strip()
    if not s or s.upper() in {"NR", "N/R", "NA", "N/A"}:
        return []
    return [p.strip() for p in _SPLIT_RE.split(s) if p.strip()]


def unique_items(items):
    return list(dict.fromkeys(items))


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


def onehot(df: pd.DataFrame, id_col: str, col: str) -> pd.DataFrame:
    rows = []
    for _, r in df[[id_col, col]].iterrows():
        for item in unique_items(parse_list_cell(r[col])):
            rows.append((r[id_col], item))
    long = pd.DataFrame(rows, columns=[id_col, "item"])
    if long.empty:
        return pd.DataFrame(index=df[id_col].unique())
    return (pd.crosstab(long[id_col], long["item"]) > 0).astype(int)


# =========================
# FIGURAS
# =========================
def plot_joint_frequency_grouped(
    df,
    id_col,
    col_poll,
    col_env,
    out_dir,
    title,
    xlabel,
    poll_group_label,
    env_group_label,
    top_poll=15,
    top_env=15,
    gap_size=2,
):
    poll = []
    env = []
    for _, r in df[[id_col, col_poll, col_env]].iterrows():
        poll.extend(unique_items(parse_list_cell(r[col_poll])))
        env.extend(unique_items(parse_list_cell(r[col_env])))

    if not poll and not env:
        return

    poll_counts = pd.Series(poll).value_counts().head(top_poll).sort_values(ascending=True)
    env_counts = pd.Series(env).value_counts().head(top_env).sort_values(ascending=True)

    gap_labels = ["" for _ in range(gap_size)]
    gap_values = [0 for _ in range(gap_size)]
    labels = list(poll_counts.index) + gap_labels + list(env_counts.index)
    values = list(poll_counts.values) + gap_values + list(env_counts.values)

    set2 = sns.color_palette("Set2", 8)
    colors = (
        [set2[0]] * len(poll_counts)
        + [(1, 1, 1)] * gap_size
        + [set2[1]] * len(env_counts)
    )

    fig, ax = plt.subplots(figsize=(9.6, 6.8))
    ax.barh(range(len(labels)), values, color=colors, edgecolor="#4d4d4d", linewidth=0.6)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([wrap_label(x, width=22) for x in labels])

    for i, v in enumerate(values):
        if v and v > 0:
            ax.text(v + 0.2, i, str(int(v)), va="center")

    if len(poll_counts) > 0:
        ax.text(0.02, 0.02, concept_label(poll_group_label), transform=ax.transAxes, fontsize=10, fontweight="semibold")
    if len(env_counts) > 0:
        ax.text(0.72, 0.02, concept_label(env_group_label), transform=ax.transAxes, fontsize=10, fontweight="semibold")

    fig.tight_layout()
    save_fig(fig, out_dir, "fig01_frecuencia_entradas")


def plot_grouped_bar(
    df,
    id_col,
    items_col,
    output_col,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
):
    rows = []
    for _, r in df[[id_col, items_col, output_col]].iterrows():
        out = str(r[output_col]).strip()
        if pd.isna(r[output_col]) or not out or out in {"NR", "N/R", "NA", "N/A"}:
            continue
        for item in unique_items(parse_list_cell(r[items_col])):
            rows.append((out, item))

    if not rows:
        return

    long = pd.DataFrame(rows, columns=["Output", "Item"])
    long["Output"] = long["Output"].map(concept_label)
    long["Item"] = long["Item"].map(concept_label)
    ct = long.value_counts().reset_index(name="n")

    fig, ax = plt.subplots(figsize=(12.2, 5.6))
    sns.barplot(
        data=ct,
        x="Output",
        y="n",
        hue="Item",
        edgecolor="#4d4d4d",
        linewidth=0.6,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    style_ticklabels(ax, axis="x", wrap_width=14)

    legend = ax.get_legend()
    if legend is not None:
        legend.set_title(concept_label("Categoria"))
        for txt in legend.get_texts():
            txt.set_text(wrap_label(txt.get_text(), width=18))

    for p in ax.patches:
        h = p.get_height()
        if h and h > 0:
            ax.text(p.get_x() + p.get_width() / 2, h + 0.15, f"{int(h)}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_heatmap_row_pct_with_counts_swapped(
    df,
    id_col,
    data_source_col,
    preprocessing_col,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
    top_src=15,
    top_prep=15,
):
    rows = []
    for _, r in df[[id_col, data_source_col, preprocessing_col]].iterrows():
        src_list = unique_items(parse_list_cell(r[data_source_col]))
        prep_list = unique_items(parse_list_cell(r[preprocessing_col]))
        for src in src_list:
            for prep in prep_list:
                rows.append((prep, src))

    if not rows:
        return

    long = pd.DataFrame(rows, columns=["A", "B"])
    ct = pd.crosstab(long["A"], long["B"])
    a_order = ct.sum(axis=1).sort_values(ascending=False).head(top_prep).index
    b_order = ct.sum(axis=0).sort_values(ascending=False).head(top_src).index
    ct = ct.loc[a_order, b_order]

    row_sums = ct.sum(axis=1).replace(0, 1)
    pct = ct.div(row_sums, axis=0) * 100.0
    annot = ct.astype(int).astype(str)

    pct.index = [wrap_label(x, width=18) for x in pct.index]
    pct.columns = [wrap_label(x, width=16) for x in pct.columns]
    annot.index = pct.index
    annot.columns = pct.columns

    fig, ax = plt.subplots(figsize=(10.2, 6.2))
    sns.heatmap(
        pct,
        annot=annot,
        fmt="",
        cmap="Blues",
        linewidths=0.4,
        linecolor="#d0d0d0",
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_cooccurrence_top(
    df,
    id_col,
    col_a,
    col_b,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
    top_n=12,
):
    A = onehot(df, id_col, col_a)
    B = onehot(df, id_col, col_b)
    idx = A.index.intersection(B.index)
    if idx.empty:
        return

    M = A.loc[idx].T.dot(B.loc[idx])
    row_order = M.sum(axis=1).sort_values(ascending=False).head(top_n).index
    col_order = M.sum(axis=0).sort_values(ascending=False).head(top_n).index
    M2 = M.loc[row_order, col_order]
    M2.index = [wrap_label(x, width=18) for x in M2.index]
    M2.columns = [wrap_label(x, width=16) for x in M2.columns]

    fig, ax = plt.subplots(figsize=(9.8, 6.2))
    sns.heatmap(M2, annot=True, fmt="d", linewidths=0.4, linecolor="#d0d0d0", cmap="Blues", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_pollutant_cooccurrence(
    df,
    id_col,
    col_poll,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
    top_n=12,
):
    A = onehot(df, id_col, col_poll)
    if A.empty or A.shape[1] == 0:
        return

    M = A.T.dot(A)
    for idx in M.index:
        if idx in M.columns:
            M.loc[idx, idx] = 0

    row_sums = M.sum(axis=1)
    keep = row_sums[row_sums > 0].index
    if len(keep) == 0:
        return

    M = M.loc[keep, keep]
    order = M.sum(axis=1).sort_values(ascending=False).head(top_n).index
    M2 = M.loc[order, order]
    M2.index = [wrap_label(x, width=18) for x in M2.index]
    M2.columns = [wrap_label(x, width=18) for x in M2.columns]

    fig, ax = plt.subplots(figsize=(9.8, 6.2))
    sns.heatmap(M2, annot=True, fmt="d", linewidths=0.4, linecolor="#d0d0d0", cmap="Blues", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_pollutant_count_per_study(
    df,
    col_poll,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
):
    per_study = (
        df[col_poll]
        .apply(lambda x: len(unique_items(parse_list_cell(x))))
        .astype(int)
    )
    dist = per_study.value_counts().sort_index()
    if dist.empty:
        return

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    sns.barplot(
        x=dist.index.astype(str),
        y=dist.values,
        edgecolor="#4d4d4d",
        linewidth=0.6,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for i, v in enumerate(dist.values):
        ax.text(i, v + 0.1, str(int(v)), ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_output_relationship(
    df,
    id_col,
    items_col,
    output_col,
    out_dir,
    stem,
    title,
    xlabel,
    ylabel,
    top_n_items=12,
    top_n_outputs=12,
    invert_axes=False,
):
    rows = []
    for _, r in df[[id_col, items_col, output_col]].iterrows():
        out = str(r[output_col]).strip()
        if pd.isna(r[output_col]) or out in {"NR", "N/R", "NA", "N/A", ""}:
            continue
        for item in unique_items(parse_list_cell(r[items_col])):
            rows.append((item, out))

    if not rows:
        return

    long = pd.DataFrame(rows, columns=["item", "output"])
    ct = pd.crosstab(long["item"], long["output"])
    item_order = ct.sum(axis=1).sort_values(ascending=False).head(top_n_items).index
    out_order = ct.sum(axis=0).sort_values(ascending=False).head(top_n_outputs).index
    ct2 = ct.loc[item_order, out_order]
    if invert_axes:
        ct2 = ct2.T

    ct2.index = [wrap_label(x, width=18) for x in ct2.index]
    ct2.columns = [wrap_label(x, width=18) for x in ct2.columns]

    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    sns.heatmap(ct2, annot=True, fmt="d", linewidths=0.4, linecolor="#d0d0d0", cmap="Blues", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)

    fig.tight_layout()
    save_fig(fig, out_dir, stem)


# =========================
# TABLAS LATEX (PUNTOS 2 y 5)
# =========================
def latex_escape_text(x):
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


def write_latex_table(
    df: pd.DataFrame,
    out_path: Path,
    colspec: str,
    label: str,
    caption: str,
):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out = df.copy()
    for c in df_out.columns:
        df_out[c] = df_out[c].map(latex_escape_text)
    df_out.columns = [latex_escape_text(c) for c in df_out.columns]

    lines = [
        r"\begin{longtblr}[",
        r"  entry=none,",
        rf"  label={{{label}}},",
        rf"  caption={{{caption}}}",
        r"]{",
        rf"  colspec={{{colspec}}},",
        r"  width=\textwidth,",
        r"  row{1}={font=\bfseries}",
        r"}",
    ]
    lines.append(" & ".join(df_out.columns) + r" \\")
    for row in df_out.itertuples(index=False, name=None):
        lines.append(" & ".join(str(v) for v in row) + r" \\")
    lines.append(r"\end{longtblr}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_summary_table(df: pd.DataFrame, id_col: str, col_poll: str, col_env: str, lang: str) -> pd.DataFrame:
    n = int(df[id_col].nunique())
    poll_oh = onehot(df, id_col, col_poll)
    env_oh = onehot(df, id_col, col_env)

    poll_counts = poll_oh.sum(axis=0).sort_values(ascending=False) if not poll_oh.empty else pd.Series(dtype=int)
    env_counts = env_oh.sum(axis=0).sort_values(ascending=False) if not env_oh.empty else pd.Series(dtype=int)

    rows = []
    top_n = 10
    for name, k in poll_counts.head(top_n).items():
        rows.append(("Contaminante" if lang == "es" else "Pollutant", name, int(k), n, round(100.0 * float(k) / n, 1)))
    for name, k in env_counts.head(top_n).items():
        rows.append(("Variable ambiental" if lang == "es" else "Environmental variable", name, int(k), n, round(100.0 * float(k) / n, 1)))

    if lang == "es":
        cols = ["Dimension", "Variable", "k", "n", "Porcentaje"]
    else:
        cols = ["Dimension", "Variable", "k", "n", "Percent"]
    return pd.DataFrame(rows, columns=cols)


def build_traceability_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    idx = df.set_index("Article_ID", drop=False)
    specs = [
        ("A135", "D1_Pollutants_inputs"),
        ("A028", "D1_Pollutants_inputs"),
        ("A149", "D1_Env_variables_inputs"),
        ("A084", "D1_Pollutants_inputs"),
    ]
    rows = []
    for aid, field in specs:
        if aid not in idx.index:
            continue
        r = idx.loc[aid]
        val = r.get(field, "")
        ev = r.get("Evidence_D1_pages", "")
        if lang == "es":
            rows.append((aid, field, val, ev))
        else:
            rows.append((aid, field, val, ev))

    if lang == "es":
        cols = ["Article_ID", "Campo", "Valor_resumido", "Evidence_D1_pages"]
    else:
        cols = ["Article_ID", "Field", "Summarized_value", "Evidence_D1_pages"]
    return pd.DataFrame(rows, columns=cols)


def generate_latex_tables(df: pd.DataFrame, out_dir: Path, lang: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary_table(df, "Article_ID", "D1_Pollutants_inputs", "D1_Env_variables_inputs", lang)
    trace = build_traceability_table(df, lang)

    if lang == "es":
        write_latex_table(
            summary,
            out_dir / f"d1_tabla_resumen_{lang}.tex",
            "X[1.35,l,m] X[1.75,l,m] X[0.55,c,m] X[0.55,c,m] X[0.8,c,m]",
            "tab:d1_resumen_frecuencias",
            r"Directriz D1: resumen de frecuencias de contaminantes y variables ambientales (k/n/\%). Elaboración propia.",
        )
        write_latex_table(
            trace,
            out_dir / f"d1_tabla_trazabilidad_minima_{lang}.tex",
            "X[0.9,l,m] X[1.35,l,m] X[2.8,l,m] X[0.95,l,m]",
            "tab:d1_trazabilidad_minima",
            r"Directriz D1: trazabilidad mínima de evidencia por estudio y campo. Elaboración propia.",
        )
    else:
        write_latex_table(
            summary,
            out_dir / f"d1_tabla_resumen_{lang}.tex",
            "X[1.35,l,m] X[1.75,l,m] X[0.55,c,m] X[0.55,c,m] X[0.8,c,m]",
            "tab:d1_summary_frequencies",
            "Guideline D1: frequency summary of pollutants and environmental variables (k/n/%).",
        )
        write_latex_table(
            trace,
            out_dir / f"d1_tabla_trazabilidad_minima_{lang}.tex",
            "X[0.9,l,m] X[1.35,l,m] X[2.8,l,m] X[0.95,l,m]",
            "tab:d1_minimum_traceability",
            "Guideline D1: minimum evidence traceability by study and field.",
        )


# =========================
# MAIN
# =========================
def main():
    script_dir = Path(__file__).resolve().parent
    dataset = read_dataset_csv(script_dir / "assets" / "sintesis" / "dataset.csv")

    setup_style()

    base_out = script_dir / "salidas"
    out_fig = {
        "es": base_out / "figuras" / "d1" / "es",
        "en": base_out / "figuras" / "d1" / "en",
    }
    out_tab = {
        "es": base_out / "tablas" / "d1" / "es",
        "en": base_out / "tablas" / "d1" / "en",
    }

    labels = {
        "es": {
            "fig01_title": "Frecuencia de Variables de Entrada",
            "fig01_xlabel": "Numero de estudios",
            "fig01_poll": "Contaminantes",
            "fig01_env": "Ambientales",
            "fig02_title": "Variables Ambientales por Clase de Salida",
            "fig03_title": "Contaminantes por Clase de Salida",
            "fig04_title": "Preprocesamiento vs Fuente de Datos",
            "fig05_title": "Relacion: Contaminantes vs Variables Ambientales",
            "fig06_title": "Relacion: Tipo de Salida vs Contaminantes",
            "fig07_title": "Relacion: Variables Ambientales vs Tipo de Salida",
            "fig08_title": "Coocurrencia entre Contaminantes Atmosfericos",
            "fig09_title": "Numero de Contaminantes por Estudio",
            "x_output": "Clase de salida",
            "y_studies": "Numero de estudios",
            "x_data_source": "Fuente de datos",
            "y_preprocess": "Preprocesamiento",
            "x_cont": "Contaminantes",
            "y_cont": "Contaminantes",
            "x_num_cont": "Numero de contaminantes por estudio",
        },
        "en": {
            "fig01_title": "Input Variables Frequency",
            "fig01_xlabel": "Number of studies",
            "fig01_poll": "Pollutants",
            "fig01_env": "Environmental",
            "fig02_title": "Environmental Variables by Output Class",
            "fig03_title": "Pollutants by Output Class",
            "fig04_title": "Preprocessing vs Data Source",
            "fig05_title": "Relationship: Pollutants vs Environmental Variables",
            "fig06_title": "Relationship: Output Type vs Pollutants",
            "fig07_title": "Relationship: Environmental Variables vs Output Type",
            "fig08_title": "Co-occurrence among Air Pollutants",
            "fig09_title": "Number of Pollutants per Study",
            "x_output": "Output class",
            "y_studies": "Number of studies",
            "x_data_source": "Data source",
            "y_preprocess": "Preprocessing",
            "x_cont": "Pollutants",
            "y_cont": "Pollutants",
            "x_num_cont": "Number of pollutants per study",
        },
    }

    id_col = "Article_ID"
    col_poll = "D1_Pollutants_inputs"
    col_env = "D1_Env_variables_inputs"
    col_out = "D1_Target_output_airpollution_class"
    col_src = "D1_Data_source_type"
    col_prep = "D1_Preprocessing"

    for lang in ("es", "en"):
        cfg = labels[lang]
        f_out = out_fig[lang]
        f_out.mkdir(parents=True, exist_ok=True)

        plot_joint_frequency_grouped(
            dataset, id_col, col_poll, col_env, f_out,
            title=cfg["fig01_title"],
            xlabel=cfg["fig01_xlabel"],
            poll_group_label=cfg["fig01_poll"],
            env_group_label=cfg["fig01_env"],
            top_poll=15, top_env=15, gap_size=2,
        )
        plot_grouped_bar(
            dataset, id_col, col_env, col_out, f_out,
            "fig02_ambientales_vs_salida",
            cfg["fig02_title"],
            cfg["x_output"],
            cfg["y_studies"],
        )
        plot_grouped_bar(
            dataset, id_col, col_poll, col_out, f_out,
            "fig03_contaminantes_vs_salida",
            cfg["fig03_title"],
            cfg["x_output"],
            cfg["y_studies"],
        )
        plot_heatmap_row_pct_with_counts_swapped(
            dataset, id_col, col_src, col_prep, f_out,
            "fig04_preprocesamiento_vs_fuente",
            cfg["fig04_title"],
            cfg["x_data_source"],
            cfg["y_preprocess"],
            top_src=15, top_prep=15,
        )
        plot_cooccurrence_top(
            dataset, id_col, col_poll, col_env, f_out,
            "fig05_coocurrencia_top",
            cfg["fig05_title"],
            "Variables ambientales" if lang == "es" else "Environmental variables",
            "Contaminantes" if lang == "es" else "Pollutants",
            top_n=12,
        )
        plot_output_relationship(
            dataset, id_col, col_poll, col_out, f_out,
            "fig06_relacion_salida_vs_contaminantes",
            cfg["fig06_title"],
            cfg["x_cont"],
            cfg["x_output"],
            top_n_items=12, top_n_outputs=12, invert_axes=True,
        )
        plot_output_relationship(
            dataset, id_col, col_env, col_out, f_out,
            "fig07_relacion_ambiente_vs_salida",
            cfg["fig07_title"],
            cfg["x_output"],
            "Variables ambientales" if lang == "es" else "Environmental variables",
            top_n_items=12, top_n_outputs=12, invert_axes=False,
        )
        plot_pollutant_cooccurrence(
            dataset, id_col, col_poll, f_out,
            "fig08_coocurrencia_contaminantes",
            cfg["fig08_title"],
            cfg["x_cont"],
            cfg["y_cont"],
            top_n=12,
        )
        plot_pollutant_count_per_study(
            dataset, col_poll, f_out,
            "fig09_numero_contaminantes_por_estudio",
            cfg["fig09_title"],
            cfg["x_num_cont"],
            cfg["y_studies"],
        )

        generate_latex_tables(dataset, out_tab[lang], lang)

    # Copia de conveniencia para flujo actual
    legacy_dir = script_dir / "figuras_fase3"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    for png in (out_fig["es"]).glob("*.png"):
        shutil.copy2(png, legacy_dir / png.name)

    print(f"[OK] Figuras ES: {out_fig['es']}")
    print(f"[OK] Figuras EN: {out_fig['en']}")
    print(f"[OK] Tablas ES:  {out_tab['es']}")
    print(f"[OK] Tablas EN:  {out_tab['en']}")
    print(f"[OK] Legacy ES:  {legacy_dir}")


if __name__ == "__main__":
    main()
