#!/usr/bin/env python3
"""
Genera graficas descriptivas de perfil del corpus para la SLR.

Salida:
  mdpi/python/outputs/figuras/perfil/*.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import re
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
from paths import OUTPUTS_DIR, SCREENING_DIR, SYNTHESIS_DATA_DIR

try:
    import seaborn as sns  # type: ignore
    HAS_SEABORN = True
except Exception:
    HAS_SEABORN = False


def setup_style() -> List[Tuple[float, float, float, float]]:
    """Configura estilo tipo articulo cientifico y devuelve colores Set2."""
    colors = list(plt.get_cmap("Set2").colors)

    if HAS_SEABORN:
        sns.set_theme(style="whitegrid", context="paper", palette="Set2")
    else:
        # Fallback visual muy cercano a seaborn whitegrid.
        plt.style.use("seaborn-v0_8-whitegrid")

    plt.rcParams.update(
        {
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
        }
    )
    return colors


def save_fig(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def cleanup_previous_pdfs(out_dir: Path) -> None:
    """Elimina PDFs previos para mantener solo salidas PNG."""
    if not out_dir.exists():
        return
    for pdf in out_dir.glob("*.pdf"):
        pdf.unlink()


def annotate_bars(ax: plt.Axes, fmt: str = "{:.0f}", horizontal: bool = False) -> None:
    for p in ax.patches:
        if horizontal:
            w = p.get_width()
            y = p.get_y() + p.get_height() / 2
            ax.text(w + 0.3, y, fmt.format(w), va="center", ha="left")
        else:
            h = p.get_height()
            x = p.get_x() + p.get_width() / 2
            ax.text(x, h + 0.2, fmt.format(h), va="bottom", ha="center")


def concept_label(x: object) -> str:
    s = str(x).strip()
    if not s:
        return s
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def wrap_label(x: object, width: int = 18) -> str:
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


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def plot_prisma_fases(prisma: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    lookup: Dict[str, str] = {
        "database_results": "Identificados",
        "records_removed": "Duplicados eliminados",
        "records_screened": "Cribados",
        "records_excluded": "Excluidos (cribado)",
        "reports_sought": "Buscados full-text",
        "reports_notretrieved": "No recuperados",
        "reports_assessed": "Evaluados full-text",
        "reports_excluded": "Excluidos (full-text)",
        "new_studies": "Incluidos",
    }
    order = list(lookup.keys())

    values = []
    for key in order:
        row = prisma.loc[prisma["box"] == key, "n"]
        n = int(float(row.iloc[0])) if not row.empty and str(row.iloc[0]).strip() else 0
        values.append((lookup[key], n))

    total_identificados = values[0][1] if values else 1
    labels = [wrap_label(x[0], width=18) for x in values]
    counts = [x[1] for x in values]
    pcts = [100.0 * c / total_identificados for c in counts]

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    bar_colors = [colors[i % len(colors)] for i in range(len(labels))]
    bars = ax.barh(labels, counts, color=bar_colors, edgecolor="#4d4d4d", linewidth=0.6)
    ax.invert_yaxis()
    ax.set_xlabel("Numero de registros/reportes")

    max_x = max(counts) if counts else 1
    ax.set_xlim(0, max_x * 1.24)

    for b, n, pct in zip(bars, counts, pcts):
        x = b.get_width()
        y = b.get_y() + b.get_height() / 2
        ax.text(x + max_x * 0.015, y, f"{n} ({pct:.1f}%)", va="center", ha="left")

    save_fig(fig, out_dir, "fig01_prisma_fases")


def plot_year_distribution(dataset: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    counts = dataset["Year"].astype(str).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(counts.index, counts.values, color=colors[0], edgecolor="#4d4d4d", linewidth=0.6)
    ax.set_xlabel("Anio de publicacion")
    ax.set_ylabel("Numero de estudios")
    annotate_bars(ax)
    save_fig(fig, out_dir, "fig02_distribucion_anual")


def plot_study_type(dataset: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    mapping = {
        "Experiments": "Experimental",
        "Correlation (observational studies)": "Correlacional/observacional",
        "Quantitative Empirical Studies (no specific type)": "Cuantitativo empirico (sin subtipo)",
    }
    s = dataset["Study_type_quant"].map(lambda x: mapping.get(str(x), str(x)))
    counts = s.value_counts()
    labels = [wrap_label(x, width=22) for x in counts.index]

    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    cols = [colors[i % len(colors)] for i in range(len(counts))]
    ax.barh(labels, counts.values, color=cols, edgecolor="#4d4d4d", linewidth=0.6)
    ax.invert_yaxis()
    ax.set_xlabel("Numero de estudios")
    annotate_bars(ax, horizontal=True)
    save_fig(fig, out_dir, "fig03_tipo_estudio")


def plot_retrieval_status(screened: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    sought = screened.loc[screened["Screening_result"].str.strip() == "Sought for retrieval"].copy()
    status = sought["Retrieval_result"].fillna("").str.strip()
    preferred_order = ["Retrieved", "Requested", "Not retrieved", "Retracted", "ResearchGate"]
    mapping = {
        "Retrieved": "Obtenido",
        "Requested": "Solicitado",
        "Not retrieved": "No recuperado",
        "Retracted": "Retractado",
        "ResearchGate": "Gestionado por ResearchGate",
    }
    counts_raw = status.value_counts()
    ordered_present = [s for s in preferred_order if s in counts_raw.index]
    ordered_present += [s for s in counts_raw.index if s not in ordered_present]
    counts = counts_raw.reindex(ordered_present).fillna(0).astype(int)
    labels = [wrap_label(mapping.get(x, x), width=16) for x in counts.index]

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    cols = [colors[i % len(colors)] for i in range(len(counts))]
    bars = ax.bar(labels, counts.values, color=cols, edgecolor="#4d4d4d", linewidth=0.6)
    ax.set_ylabel("Numero de reportes")
    ax.set_xlabel("Estado de recuperacion")
    ax.tick_params(axis="x", rotation=0)

    total = counts.sum() if counts.sum() else 1
    for b, n in zip(bars, counts.values):
        pct = 100.0 * n / total
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.25, f"{n} ({pct:.1f}%)", ha="center", va="bottom")

    save_fig(fig, out_dir, "fig04_estado_retrieval")


def plot_quality_band(qa: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    order = ["Alta", "Media", "Baja"]
    counts = qa["QA_Quality_band"].fillna("").str.strip().value_counts().reindex(order).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    cols = [colors[2], colors[1], colors[3]]
    bars = ax.bar(counts.index, counts.values, color=cols, edgecolor="#4d4d4d", linewidth=0.6)
    ax.set_xlabel("Banda de calidad")
    ax.set_ylabel("Numero de estudios")

    total = counts.sum() if counts.sum() else 1
    for b, n in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2, f"{n} ({100*n/total:.1f}%)", ha="center", va="bottom")

    save_fig(fig, out_dir, "fig05_bandas_calidad")


def plot_pollutants_profile(dataset: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    pollutant_patterns = [
        ("CO", re.compile(r"(?<![A-Z0-9])CO(?!2)(?![A-Z0-9])", re.IGNORECASE)),
        ("PM2.5", re.compile(r"PM\\s*2\\.?5|PM25", re.IGNORECASE)),
        ("CO2", re.compile(r"CO\\s*2", re.IGNORECASE)),
        ("PM10", re.compile(r"PM\\s*10", re.IGNORECASE)),
        ("SO2", re.compile(r"SO\\s*2", re.IGNORECASE)),
        ("NO2", re.compile(r"NO\\s*2", re.IGNORECASE)),
        ("O3", re.compile(r"(?<![A-Z0-9])O\\s*3(?![A-Z0-9])", re.IGNORECASE)),
        ("TVOC", re.compile(r"TVOC|VOCS?|VOLATILE\\s+ORGANIC", re.IGNORECASE)),
    ]

    series = dataset["D1_Pollutants_inputs"].fillna("").astype(str)
    total = len(dataset) if len(dataset) else 1
    counts = []
    for label, pattern in pollutant_patterns:
        n = int(series.map(lambda x: bool(pattern.search(x))).sum())
        if n > 0:
            counts.append((label, n))

    if not counts:
        fig, ax = plt.subplots(figsize=(6.8, 3.8))
        ax.text(0.5, 0.5, "No se detectaron contaminantes estandarizables en D1", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_dir, "fig06_perfil_contaminantes")
        return

    counts.sort(key=lambda x: (-x[1], x[0]))
    labels = [c[0] for c in counts]
    values = [c[1] for c in counts]

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    cols = [colors[i % len(colors)] for i in range(len(values))]
    bars = ax.barh(labels, values, color=cols, edgecolor="#4d4d4d", linewidth=0.6)
    ax.invert_yaxis()
    ax.set_xlabel("Numero de estudios")

    max_x = max(values) if values else 1
    ax.set_xlim(0, max_x * 1.24)
    for b, n in zip(bars, values):
        pct = 100.0 * n / total
        y = b.get_y() + b.get_height() / 2
        ax.text(n + max_x * 0.015, y, f"{n} ({pct:.1f}%)", va="center", ha="left")

    save_fig(fig, out_dir, "fig06_perfil_contaminantes")


def plot_nr_fields(dataset: pd.DataFrame, out_dir: Path, colors: List[Tuple[float, float, float, float]]) -> None:
    # Campos analiticos (excluye metadatos basicos)
    analytical_cols = [
        c
        for c in dataset.columns
        if c.startswith(("D1_", "D2_", "D3_", "Eval_", "Main_", "Evidence_", "QA_", "Sensitivity_"))
    ]
    nr_mask = dataset[analytical_cols].fillna("").apply(lambda col: col.map(lambda x: str(x).strip() == "NR"))
    nr_counts = nr_mask.sum(axis=0)
    nr_counts = nr_counts[nr_counts > 0].sort_values(ascending=False).head(12)

    if nr_counts.empty:
        # Grafica de completitud total en caso de no existir NR.
        fig, ax = plt.subplots(figsize=(6.8, 3.8))
        ax.text(0.5, 0.5, "No se detectaron valores NR en campos analiticos", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_dir, "fig07_nr_campos_criticos")
        return

    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    cols = [colors[i % len(colors)] for i in range(len(nr_counts))]
    axis_labels = [wrap_label(c, width=24) for c in nr_counts.index]
    ax.barh(axis_labels, nr_counts.values, color=cols, edgecolor="#4d4d4d", linewidth=0.6)
    ax.invert_yaxis()
    ax.set_xlabel("Conteo de NR (n=19 estudios)")
    annotate_bars(ax, horizontal=True)
    save_fig(fig, out_dir, "fig07_nr_campos_criticos")


def main() -> None:
    out_dir = OUTPUTS_DIR / "figuras" / "perfil"
    cleanup_previous_pdfs(out_dir)

    dataset = read_csv(SYNTHESIS_DATA_DIR / "dataset.csv")
    prisma = read_csv(SYNTHESIS_DATA_DIR / "prisma.csv")
    screened = read_csv(SCREENING_DIR / "01_screening" / "articles_screened.csv")
    qa = read_csv(SCREENING_DIR / "03_calidad" / "articles_quality_assessment.csv")

    colors = setup_style()

    plot_prisma_fases(prisma, out_dir, colors)
    plot_year_distribution(dataset, out_dir, colors)
    plot_study_type(dataset, out_dir, colors)
    plot_retrieval_status(screened, out_dir, colors)
    plot_quality_band(qa, out_dir, colors)
    plot_pollutants_profile(dataset, out_dir, colors)
    plot_nr_fields(dataset, out_dir, colors)

    print(f"[OK] Graficas generadas en: {out_dir}")
    if not HAS_SEABORN:
        print("[WARN] seaborn no esta instalado; se uso fallback visual con Matplotlib + paleta Set2.")


if __name__ == "__main__":
    main()
