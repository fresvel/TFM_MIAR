#!/usr/bin/env python3
"""
Fase Eval 1 - Analisis transversal util para redaccion de resultados.

Salidas (es):
- Tabla de unidades comparables.
- Tabla de frecuencia de metricas por grupo comparable core (k>=3).
- Tabla resumen para boxplots (n, mediana, min, max).
- Tabla de coocurrencia DataSource vs UnidadComparable.
- Tabla de coocurrencia TargetClass vs PurposeD2.
- Tabla de trazabilidad por estudio.
- Figura de metricas por grupo comparable (hue).
- Figura general de metricas top (sin k=1).
- Figura de boxplots de valores reportados por metrica.
- Figura variante de boxplots por clase comparable (metricas en eje x).
- Figura heatmap DataSource vs UnidadComparable.
- Figura heatmap TargetClass vs PurposeD2.
"""

from __future__ import annotations

from pathlib import Path
import math
import re
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


SPLIT_RE = re.compile(r"[;|,]+")
NA_SET = {"", "NA", "N/A", "N/R"}
BOUNDED_TO_PERCENT_METRICS = {
    "Accuracy",
    "Precision",
    "Recall",
    "F1",
    "AUC",
    "R2",
    "COD",
    "Delivery_Ratio",
    "Reliability",
    "Stability_AAS",
}

UNIT_CONCEPT_LABELS = {
    "AQI_Classification": "Clasificacion de AQI",
    "IAQ_Classification_Control": "Clasificacion de IAQ con control",
    "AQI_IAQ_Estimation": "Estimacion de AQI/IAQ",
    "PM2.5_Prediction": "Prediccion de PM2.5",
}

UNIT_SHORT_LABELS = {
    "AQI_Classification": "Clasificacion AQI",
    "AQI_IAQ_Estimation": "Estimacion AQI/IAQ",
    "IAQ_Classification_Control": "Clasificacion+control IAQ",
    "PM2.5_Prediction": "Prediccion PM2.5",
    "CO_AQI_IAQ_Categorization": "Categorizacion CO-AQI/IAQ",
    "OR_Risk_Classification": "Clasificacion riesgo OR",
    "Hybrid_LoP_mAQI_Prediction": "Prediccion hibrida LoP-mAQI",
    "PM10_Prediction": "Prediccion PM10",
    "PM2.5_Calibration": "Calibracion PM2.5",
    "SIA_Classification": "Clasificacion SIA",
    "VOC_Prediction": "Prediccion VOC",
}

METRIC_CONCEPT_LABELS = {
    "Accuracy": "Exactitud",
    "MAE": "Error absoluto medio (MAE)",
    "MAPE": "Error porcentual absoluto medio (MAPE)",
    "NRMSE": "Raiz del error cuadratico medio normalizado (NRMSE)",
    "R2": "Coeficiente de determinacion (R2)",
}


def concept_label(x: object) -> str:
    s = str(x).strip()
    if not s:
        return s
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def display_unit_label(unit: str) -> str:
    return concept_label(UNIT_SHORT_LABELS.get(unit, unit))


def display_metric_label(metric: str) -> str:
    return concept_label(metric)


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


def save_fig(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def metric_stem(metric: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "_", metric).strip("_").lower()
    return f"fig02_boxplot_metric_{safe}"


def normalize_metric_token(token: str) -> str:
    t = token.strip()
    if t.startswith("Other:"):
        t = t.split("Other:", 1)[1]
    return t


def build_unit_table(df: pd.DataFrame) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    counts = (df[["Article_ID", "Eval_Comparable_unit_norm"]]
              .dropna()
              .drop_duplicates()
              .groupby("Eval_Comparable_unit_norm")["Article_ID"]
              .nunique()
              .sort_values(ascending=False))
    out = pd.DataFrame({
        "Unidad comparable": counts.index,
        "k": counts.values.astype(int),
        "n": n,
    })
    out["%"] = (out["k"] * 100.0 / n).round(1)
    out["Unidad comparable"] = (
        out["Unidad comparable"]
        .map(UNIT_SHORT_LABELS)
        .fillna(out["Unidad comparable"].str.replace("_", " ", regex=False))
    )
    return out


def get_core_units(df: pd.DataFrame, min_k: int = 3) -> list[str]:
    counts = (df[["Article_ID", "Eval_Comparable_unit_norm"]]
              .dropna()
              .drop_duplicates()
              .groupby("Eval_Comparable_unit_norm")["Article_ID"]
              .nunique()
              .sort_values(ascending=False))
    return [u for u, k in counts.items() if int(k) >= min_k]


def build_metric_frequency_core(df: pd.DataFrame, core_units: list[str]) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    rows: list[dict[str, str]] = []
    for _, r in df.iterrows():
        unit = str(r.get("Eval_Comparable_unit_norm", "")).strip()
        if unit not in core_units:
            continue
        for tok in parse_multi(r.get("Eval_Metrics_reported_norm", ""), include_nr=False):
            mt = normalize_metric_token(tok)
            rows.append({"Article_ID": str(r["Article_ID"]), "Unidad_comparable": unit, "Metrica": mt})
    if not rows:
        return pd.DataFrame(columns=["Unidad_comparable", "Metrica", "k", "n", "%"])
    long = pd.DataFrame(rows).drop_duplicates()
    out = (long.groupby(["Unidad_comparable", "Metrica"])["Article_ID"]
           .nunique()
           .reset_index(name="k")
           .sort_values(["k", "Unidad_comparable", "Metrica"], ascending=[False, True, True]))
    out["n"] = n
    out["%"] = (out["k"] * 100.0 / n).round(1)
    return out


def build_metric_frequency_general(df: pd.DataFrame) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    rows: list[dict[str, str]] = []
    for _, r in df.iterrows():
        for tok in parse_multi(r.get("Eval_Metrics_reported_norm", ""), include_nr=False):
            mt = normalize_metric_token(tok)
            rows.append({"Article_ID": str(r["Article_ID"]), "Metrica": mt})
    if not rows:
        return pd.DataFrame(columns=["Metrica", "k", "n", "%"])
    long = pd.DataFrame(rows).drop_duplicates()
    out = (long.groupby("Metrica")["Article_ID"]
           .nunique()
           .reset_index(name="k")
           .sort_values(["k", "Metrica"], ascending=[False, True]))
    out["n"] = n
    out["%"] = (out["k"] * 100.0 / n).round(1)
    return out


def detect_metric(text: str) -> str | None:
    t = text.lower()
    # Orden importante para evitar colisiones NRMSE->RMSE, NMSE->MSE
    if "nrmse" in t:
        return "NRMSE"
    if "nmse" in t:
        return "NMSE"
    if "rmse" in t:
        return "RMSE"
    if "mape" in t:
        return "MAPE"
    if "mae" in t:
        return "MAE"
    if "r^2" in t or "r2" in t:
        return "R2"
    if "mse" in t:
        return "MSE"
    if "accuracy" in t:
        return "Accuracy"
    if "precision" in t:
        return "Precision"
    if "recall" in t:
        return "Recall"
    if "f1" in t:
        return "F1"
    if "auc" in t:
        return "AUC"
    if "throughput" in t:
        return "Throughput"
    if "delivery" in t:
        return "Delivery_Ratio"
    if "reliability" in t:
        return "Reliability"
    if "stability" in t:
        return "Stability_AAS"
    if "cod" in t:
        return "COD"
    return None


def normalize_bounded_metric_value(metric: str, value: float) -> tuple[float, bool]:
    """
    Normaliza a escala 0-100 solo cuando la metrica es acotada y el valor viene en 0-1.
    """
    if metric in BOUNDED_TO_PERCENT_METRICS and 0.0 <= value <= 1.0:
        return value * 100.0, True
    return value, False


def extract_metric_values(df: pd.DataFrame, core_units: list[str]) -> pd.DataFrame:
    expr = re.compile(
        r"([A-Za-z0-9_+./\-]+)\s*(=|>=|<=|>|<|≈)\s*([+\-]?[0-9]+(?:\.[0-9]+)?(?:/[0-9]+(?:\.[0-9]+)?){0,8})"
    )
    rows: list[dict[str, object]] = []

    for _, r in df.iterrows():
        unit = str(r.get("Eval_Comparable_unit_norm", "")).strip()
        if unit not in core_units:
            continue

        s = "" if pd.isna(r.get("Eval_Reported_values")) else str(r.get("Eval_Reported_values")).strip()
        if not s:
            continue

        for seg in [x.strip() for x in s.split(";") if x.strip()]:
            for key, op, value_str in expr.findall(seg):
                metric = detect_metric(key)
                if metric is None:
                    continue

                for one in value_str.split("/"):
                    try:
                        value = float(one)
                    except Exception:
                        continue
                    value_norm, was_norm = normalize_bounded_metric_value(metric, value)
                    rows.append({
                        "Article_ID": str(r["Article_ID"]),
                        "Unidad_comparable": unit,
                        "Metrica": metric,
                        "Operador": op,
                        "Valor": value,
                        "Valor_norm": value_norm,
                        "Norm_01_to_100": int(was_norm),
                    })

    if not rows:
        return pd.DataFrame(columns=["Article_ID", "Unidad_comparable", "Metrica", "Operador", "Valor", "Valor_norm", "Norm_01_to_100"])

    return pd.DataFrame(rows)


def build_boxplot_summary(values_df: pd.DataFrame, metric_filter: list[str]) -> pd.DataFrame:
    if values_df.empty:
        return pd.DataFrame(columns=[
            "Unidad comparable", "Metrica", "n valores", "n articulos", "Mediana", "Min", "Max"
        ])

    d = values_df[values_df["Metrica"].isin(metric_filter)].copy()
    if d.empty:
        return pd.DataFrame(columns=[
            "Unidad comparable", "Metrica", "n valores", "n articulos", "Mediana", "Min", "Max"
        ])

    rows = []
    for (unit, metric), g in d.groupby(["Unidad_comparable", "Metrica"]):
        rows.append({
            "Unidad_comparable": unit,
            "Metrica": metric,
            "n_valores": int(len(g)),
            "n_articulos": int(g["Article_ID"].nunique()),
            "Mediana": round(float(g["Valor_norm"].median()), 4),
            "Min": round(float(g["Valor_norm"].min()), 4),
            "Max": round(float(g["Valor_norm"].max()), 4),
        })

    out = pd.DataFrame(rows).sort_values(["Metrica", "Unidad_comparable"]).reset_index(drop=True)
    out["Unidad comparable"] = (
        out["Unidad_comparable"]
        .map(UNIT_CONCEPT_LABELS)
        .fillna(out["Unidad_comparable"].str.replace("_", " ", regex=False))
    )
    out["Metrica"] = (
        out["Metrica"]
        .map(METRIC_CONCEPT_LABELS)
        .fillna(out["Metrica"].str.replace("_", " ", regex=False))
    )
    out = out.rename(columns={
        "n_valores": "n valores",
        "n_articulos": "n articulos",
    })
    out = out[[
        "Unidad comparable",
        "Metrica",
        "n valores",
        "n articulos",
        "Mediana",
        "Min",
        "Max",
    ]]
    return out


def explode_cross(df: pd.DataFrame, left_col: str, right_col: str) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, r in df[["Article_ID", left_col, right_col]].iterrows():
        left_vals = parse_multi(r[left_col], include_nr=False)
        right_vals = parse_multi(r[right_col], include_nr=False)
        if not left_vals or not right_vals:
            continue
        for lv in left_vals:
            for rv in right_vals:
                rows.append({"Article_ID": str(r["Article_ID"]), "left": lv, "right": rv})
    if not rows:
        return pd.DataFrame(columns=["Article_ID", "left", "right"])
    return pd.DataFrame(rows).drop_duplicates()


def build_cross_table(df: pd.DataFrame, left_col: str, right_col: str, left_name: str, right_name: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    long = explode_cross(df, left_col, right_col)
    if long.empty:
        return pd.DataFrame(columns=[left_name, right_name, "k", "n", "%"])

    out = (long.groupby(["left", "right"])["Article_ID"]
           .nunique()
           .reset_index(name="k")
           .rename(columns={"left": left_name, "right": right_name})
           .sort_values(["k", left_name, right_name], ascending=[False, True, True]))
    out["n"] = n
    out["%"] = (out["k"] * 100.0 / n).round(1)
    return out


def plot_metric_frequency(metric_freq: pd.DataFrame, core_units: list[str], out_dir: Path) -> None:
    if metric_freq.empty:
        return

    d = metric_freq.copy()
    # Enfocar en metricas con presencia >=2 en los grupos core
    totals = d.groupby("Metrica")["k"].sum().sort_values(ascending=False)
    keep = totals[totals >= 2].index.tolist()
    d = d[d["Metrica"].isin(keep)].copy()
    if d.empty:
        return

    metric_order = totals.loc[keep].sort_values(ascending=False).index.tolist()
    metric_order_disp = [display_metric_label(m) for m in metric_order]
    units_present = [u for u in core_units if u in set(d["Unidad_comparable"])]
    if not units_present:
        units_present = sorted(d["Unidad_comparable"].unique().tolist())
    unit_disp = {u: display_unit_label(u) for u in units_present}

    pct_mat = (d.pivot_table(index="Metrica", columns="Unidad_comparable", values="%", aggfunc="sum", fill_value=0.0)
               .reindex(index=metric_order, columns=units_present, fill_value=0.0))
    k_mat = (d.pivot_table(index="Metrica", columns="Unidad_comparable", values="k", aggfunc="sum", fill_value=0)
             .reindex(index=metric_order, columns=units_present, fill_value=0))

    x = np.arange(len(metric_order))
    n_units = len(units_present)
    width = 0.82 / max(n_units, 1)
    offsets = (np.arange(n_units) - (n_units - 1) / 2.0) * width
    palette = sns.color_palette("Set2", max(n_units, 3))

    fig, ax = plt.subplots(figsize=(11.6, 6.2))
    for i, unit in enumerate(units_present):
        vals = pct_mat[unit].values
        ks = k_mat[unit].values
        bars = ax.bar(
            x + offsets[i],
            vals,
            width=width,
            label=unit_disp.get(unit, concept_label(unit)),
            color=palette[i],
            edgecolor="#4d4d4d",
            linewidth=0.55,
        )
        for b, k, p in zip(bars, ks, vals):
            if float(k) <= 0:
                continue
            ax.text(
                b.get_x() + b.get_width() / 2.0,
                b.get_height() + 0.35,
                f"{int(k)} | {float(p):.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_title("Frecuencia de metricas reportadas por grupos comparables (core)")
    ax.set_xlabel("Metrica")
    ax.set_ylabel("% de estudios (n=19)")
    ax.set_xticks(x)
    ax.set_xticklabels([wrap_label(m, width=14) for m in metric_order_disp], rotation=0, ha="center")
    ax.legend(title="Unidad comparable", bbox_to_anchor=(1.01, 1.0), loc="upper left")
    ax.set_ylim(0, max(5.0, float(pct_mat.max().max()) + 8.0))
    fig.tight_layout()
    save_fig(fig, out_dir, "fig01_metricas_por_grupo_comparable")


def plot_metric_frequency_general(metric_general: pd.DataFrame, out_dir: Path) -> None:
    if metric_general.empty:
        return
    d = metric_general[metric_general["k"] > 1].copy()
    if d.empty:
        return
    d = d.sort_values("k", ascending=False).reset_index(drop=True)
    d["Metrica_disp"] = d["Metrica"].map(display_metric_label)
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    bars = ax.bar(
        x,
        d["k"].values,
        color=sns.color_palette("Set2", 8)[2],
        edgecolor="#4d4d4d",
        linewidth=0.6,
    )
    for b, k, p in zip(bars, d["k"].values, d["%"].values):
        ax.text(
            b.get_x() + b.get_width() / 2.0,
            b.get_height() + 0.08,
            f"{int(k)} | {float(p):.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_title("Frecuencia general de metricas reportadas (top, sin k=1)")
    ax.set_xlabel("Metrica")
    ax.set_ylabel("Numero de estudios (k)")
    ax.set_xticks(x)
    ax.set_xticklabels([wrap_label(v, width=14) for v in d["Metrica_disp"].tolist()], rotation=0, ha="center")
    ax.set_ylim(0, float(d["k"].max()) + 1.2)
    fig.tight_layout()
    save_fig(fig, out_dir, "fig00_metricas_top_general")


def plot_metric_boxplots(values_df: pd.DataFrame, core_units: list[str], out_dir: Path) -> None:
    if values_df.empty:
        return

    counts = values_df.groupby("Metrica").size().sort_values(ascending=False)
    metric_candidates = [m for m, k in counts.items() if k >= 4]
    if "R2" in metric_candidates:
        metric_candidates = [m for m in metric_candidates if m != "R2"] + ["R2"]
    if not metric_candidates:
        return

    d = values_df[values_df["Metrica"].isin(metric_candidates)].copy()
    if d.empty:
        return

    for i, metric in enumerate(metric_candidates):
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        sub = d[d["Metrica"] == metric].copy()
        unit_order = [u for u in core_units if u in set(sub["Unidad_comparable"])]
        if not unit_order:
            unit_order = sorted(sub["Unidad_comparable"].unique().tolist())
        sub["Unidad_disp"] = sub["Unidad_comparable"].map(display_unit_label)
        unit_order_disp = [display_unit_label(u) for u in unit_order]
        sns.boxplot(
            data=sub,
            x="Unidad_disp",
            y="Valor_norm",
            order=unit_order_disp,
            color=sns.color_palette("Set2", 8)[i % 8],
            showfliers=False,
            linewidth=0.8,
            ax=ax,
        )
        sns.stripplot(
            data=sub,
            x="Unidad_disp",
            y="Valor_norm",
            order=unit_order_disp,
            color="#2f2f2f",
            size=3,
            jitter=0.18,
            alpha=0.75,
            ax=ax,
        )
        ax.set_title(display_metric_label(metric))
        ax.set_xlabel("")
        ax.set_ylabel("Valor reportado (normalizado a % cuando aplica)")
        style_ticklabels(ax, axis="x", wrap_width=16)
        fig.tight_layout()
        save_fig(fig, out_dir, metric_stem(metric))


def plot_metric_boxplots_by_class(values_df: pd.DataFrame, core_units: list[str], out_dir: Path) -> None:
    if values_df.empty:
        return

    target_units = [
        "AQI_Classification",
        "IAQ_Classification_Control",
        "AQI_IAQ_Estimation",
        "PM2.5_Prediction",
    ]
    d = values_df[values_df["Unidad_comparable"].isin(target_units)].copy()
    if d.empty:
        return

    hue_order = [u for u in target_units if u in set(d["Unidad_comparable"])]
    if not hue_order:
        return

    metric_high = [
        "Accuracy",
        "R2",
        "Precision",
        "Recall",
        "F1",
        "AUC",
        "Delivery_Ratio",
        "Reliability",
        "Stability_AAS",
        "COD",
        "Throughput",
    ]
    metric_low = ["RMSE", "MAE", "MAPE", "MSE", "NRMSE", "NMSE", "Temporal_Delay", "Loss", "Error_Ratio"]

    def _plot_subset(metric_allowlist: list[str], title: str, stem: str, y_max: float | None = None) -> None:
        sub = d[d["Metrica"].isin(metric_allowlist)].copy()
        if sub.empty:
            return
        metric_order = [m for m in metric_allowlist if m in set(sub["Metrica"])]
        if not metric_order:
            return

        fig_w = max(11.5, 1.2 * len(metric_order) + 4.6)
        fig, ax = plt.subplots(figsize=(fig_w, 6.2))
        sns.boxplot(
            data=sub,
            x="Metrica",
            y="Valor_norm",
            order=metric_order,
            hue="Unidad_comparable",
            hue_order=hue_order,
            showfliers=False,
            linewidth=0.8,
            ax=ax,
        )
        sns.stripplot(
            data=sub,
            x="Metrica",
            y="Valor_norm",
            order=metric_order,
            hue="Unidad_comparable",
            hue_order=hue_order,
            dodge=True,
            palette={u: "#2f2f2f" for u in hue_order},
            alpha=0.35,
            size=2.4,
            jitter=0.14,
            ax=ax,
        )
        handles, labels = ax.get_legend_handles_labels()
        keep_labels: list[str] = []
        keep_handles: list[object] = []
        for h, l in zip(handles, labels):
            if l in hue_order and l not in keep_labels:
                keep_labels.append(l)
                keep_handles.append(h)
        if keep_handles:
            ax.legend(
                keep_handles,
                keep_labels,
                title="Unidad comparable",
                bbox_to_anchor=(1.01, 1.0),
                loc="upper left",
                fontsize=10,
                title_fontsize=10,
            )

        ax.set_title(title)
        ax.set_xlabel("Metrica")
        ax.set_ylabel("Valor reportado (normalizado a % cuando aplica)")
        ax.tick_params(axis="x", rotation=25, labelsize=10)
        ax.tick_params(axis="y", labelsize=10)
        if y_max is not None:
            ax.set_ylim(0, y_max)
        fig.tight_layout()
        save_fig(fig, out_dir, stem)

    _plot_subset(
        metric_high,
        "Variante por clase: metricas objetivo 100 (cercanas a 100)",
        "fig02b_boxplots_valores_reportados_clase_obj100",
        y_max=105.0,
    )
    _plot_subset(
        metric_low,
        "Variante por clase: metricas objetivo 0 (cercanas a 0)",
        "fig02c_boxplots_valores_reportados_clase_obj0",
    )


def plot_metric_boxplots_hue(
    values_df: pd.DataFrame,
    core_units: list[str],
    out_dir: Path,
    stem: str,
    title: str,
    metric_allowlist: list[str] | None = None,
    metric_core_filter: list[str] | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    if values_df.empty:
        return

    d = values_df.copy()
    if metric_core_filter is not None:
        d = d[d["Metrica"].isin(metric_core_filter)].copy()
        if d.empty:
            return

    if metric_allowlist is not None:
        # Mantiene orden semantico de metricas por objetivo (meta 100 / meta 0).
        present = [m for m in metric_allowlist if m in set(d["Metrica"])]
        if not present:
            return
        d = d[d["Metrica"].isin(present)].copy()
        metric_order = present
    else:
        metric_order = d.groupby("Metrica").size().sort_values(ascending=False).index.tolist()
        if not metric_order:
            return

    # Evita categorias hue sin datos en la figura.
    hue_order = [u for u in core_units if u in set(d["Unidad_comparable"])]
    if not hue_order:
        hue_order = sorted(d["Unidad_comparable"].unique().tolist())
    if not hue_order:
        return

    fig_w = max(11.2, 1.15 * len(metric_order) + 4.5)
    fig, ax = plt.subplots(figsize=(fig_w, 6.2))
    sns.boxplot(
        data=d,
        x="Metrica",
        y="Valor_norm",
        hue="Unidad_comparable",
        order=metric_order,
        hue_order=hue_order,
        showfliers=False,
        linewidth=0.8,
        ax=ax,
    )
    sns.stripplot(
        data=d,
        x="Metrica",
        y="Valor_norm",
        hue="Unidad_comparable",
        order=metric_order,
        hue_order=hue_order,
        dodge=True,
        palette={u: "#2f2f2f" for u in hue_order},
        alpha=0.35,
        size=2.4,
        jitter=0.14,
        ax=ax,
    )

    handles, labels = ax.get_legend_handles_labels()
    keep_labels: list[str] = []
    keep_handles: list[object] = []
    for h, l in zip(handles, labels):
        if l in hue_order and l not in keep_labels:
            keep_labels.append(l)
            keep_handles.append(h)
    if keep_handles:
        ax.legend(
            keep_handles,
            keep_labels,
            title="Unidad comparable",
            bbox_to_anchor=(1.01, 1.0),
            loc="upper left",
            fontsize=10,
            title_fontsize=10,
        )

    ax.set_title(title)
    ax.set_xlabel("Metrica")
    ax.set_ylabel("Valor reportado (normalizado a % cuando aplica)")
    ax.tick_params(axis="x", rotation=25, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    if y_min is not None or y_max is not None:
        ymin_cur, ymax_cur = ax.get_ylim()
        ymin = y_min if y_min is not None else ymin_cur
        ymax = y_max if y_max is not None else ymax_cur
        # Evita graficas vacias por limites invalidos.
        if ymax > ymin:
            ax.set_ylim(ymin, ymax)
    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def plot_heatmap_from_cross(
    cross_df: pd.DataFrame,
    left_name: str,
    right_name: str,
    title: str,
    out_dir: Path,
    stem: str,
    add_left_totals_col: bool = False,
) -> None:
    if cross_df.empty:
        return

    M = cross_df.pivot_table(index=left_name, columns=right_name, values="k", aggfunc="sum", fill_value=0)
    if M.empty:
        return

    # Orden por masa para mejorar lectura
    M = M.loc[M.sum(axis=1).sort_values(ascending=False).index, M.sum(axis=0).sort_values(ascending=False).index]
    if add_left_totals_col:
        M["Total source type"] = M.sum(axis=1)
    M = M.astype(int)
    M.index = [wrap_label(v, width=18) for v in M.index]
    M.columns = [wrap_label(v, width=16) for v in M.columns]

    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    sns.heatmap(M, annot=True, fmt="d", linewidths=0.4, linecolor="#d0d0d0", cmap="Blues", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(concept_label(right_name))
    ax.set_ylabel(concept_label(left_name))
    style_ticklabels(ax, axis="x", wrap_width=14)
    style_ticklabels(ax, axis="y", wrap_width=18)
    fig.tight_layout()
    save_fig(fig, out_dir, stem)


def build_traceability(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Article_ID",
        "Eval_Comparable_unit_norm",
        "Eval_Metric_family_norm",
        "Eval_Protocol_norm",
        "Evidence_Eval_pages",
    ]
    t = df[cols].copy().sort_values("Article_ID")
    return t.rename(columns={
        "Eval_Comparable_unit_norm": "Unidad_comparable",
        "Eval_Metric_family_norm": "Familia_metrica",
        "Eval_Protocol_norm": "Protocolo",
    })


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir / "assets" / "sintesis" / "dataset.csv"
    df = read_dataset(dataset_path)
    setup_style()

    required = {
        "Eval_Comparable_unit_norm",
        "Eval_Metric_family_norm",
        "Eval_Protocol_norm",
        "Eval_Metrics_reported_norm",
        "Eval_Reported_values",
        "D1_Data_source_type",
        "D1_Target_output_airpollution_class",
        "D2_Inference_purpose_norm",
    }
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Faltan columnas requeridas: {missing}")

    out_tab = script_dir / "salidas" / "tablas" / "eval" / "es"
    out_fig = script_dir / "salidas" / "figuras" / "eval" / "es"
    out_tab.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)

    core_units = get_core_units(df, min_k=3)

    t_units = build_unit_table(df)
    t_metric_freq = build_metric_frequency_core(df, core_units)
    t_metric_general = build_metric_frequency_general(df)
    values_df = extract_metric_values(df, core_units)
    metric_value_counts = values_df.groupby("Metrica").size().sort_values(ascending=False) if not values_df.empty else pd.Series(dtype=int)
    # Mismo criterio de soporte que la figura de boxplots principal.
    metric_core_filter = metric_value_counts[metric_value_counts >= 4].index.tolist()

    # metricas con presencia no trivial para resumen de cajas
    metric_counts = values_df.groupby("Metrica").size().sort_values(ascending=False) if not values_df.empty else pd.Series(dtype=int)
    metric_filter = [m for m, k in metric_counts.items() if k >= 4]
    t_box_summary = build_boxplot_summary(values_df, metric_filter)

    t_ds_unit = build_cross_table(
        df,
        "D1_Data_source_type",
        "Eval_Comparable_unit_norm",
        "Data_source_type",
        "Unidad_comparable",
    )
    t_ds_unit = t_ds_unit[t_ds_unit["k"] > 1].copy().reset_index(drop=True)
    t_target_purpose = build_cross_table(
        df,
        "D1_Target_output_airpollution_class",
        "D2_Inference_purpose_norm",
        "Target_output_class",
        "D2_inference_purpose",
    )
    t_trace = build_traceability(df)

    # CSV
    t_units.to_csv(out_tab / "eval_unidades_comparables_es.csv", index=False, encoding="utf-8-sig")
    t_metric_freq.to_csv(out_tab / "eval_metricas_por_unidad_core_es.csv", index=False, encoding="utf-8-sig")
    t_metric_general.to_csv(out_tab / "eval_metricas_top_general_es.csv", index=False, encoding="utf-8-sig")
    t_box_summary.to_csv(out_tab / "eval_boxplot_resumen_valores_es.csv", index=False, encoding="utf-8-sig")
    t_ds_unit.to_csv(out_tab / "eval_datasource_vs_unidad_es.csv", index=False, encoding="utf-8-sig")
    t_target_purpose.to_csv(out_tab / "eval_targetclass_vs_purpose_es.csv", index=False, encoding="utf-8-sig")
    t_trace.to_csv(out_tab / "eval_trazabilidad_unidades_es.csv", index=False, encoding="utf-8-sig")

    # TEX
    write_longtblr(
        t_units,
        out_tab / "eval_unidades_comparables_es.tex",
        "X[2.5,l,m] X[0.6,c,m] X[0.6,c,m] X[0.8,c,m]",
        "tab:eval_unidades_comparables",
        r"Resultados de desempeno: unidades comparables de evaluacion (k/n/\%; n=19). Elaboracion propia.",
    )
    write_longtblr(
        t_metric_freq,
        out_tab / "eval_metricas_por_unidad_core_es.tex",
        "X[2.0,l,m] X[1.4,l,m] X[0.6,c,m] X[0.6,c,m] X[0.8,c,m]",
        "tab:eval_metricas_por_unidad_core",
        r"Resultados de desempeno: frecuencia de metricas en grupos comparables core (k/n/\%; n=19). Elaboracion propia.",
    )
    write_longtblr(
        t_box_summary,
        out_tab / "eval_boxplot_resumen_valores_es.tex",
        "X[2.0,l,m] X[1.4,l,m] X[0.7,c,m] X[0.7,c,m] X[0.8,c,m] X[0.8,c,m] X[0.8,c,m]",
        "tab:eval_boxplot_resumen_valores",
        r"Resultados de desempeno: resumen estadistico para valores reportados por metrica y unidad comparable (normalizacion 0-1 a 0-100 en metricas acotadas). Elaboracion propia.",
    )
    write_longtblr(
        t_ds_unit,
        out_tab / "eval_datasource_vs_unidad_es.tex",
        "X[1.8,l,m] X[2.0,l,m] X[0.6,c,m] X[0.6,c,m] X[0.8,c,m]",
        "tab:eval_datasource_vs_unidad",
        r"Resultados de desempeno: coocurrencia entre origen de datos y unidad comparable (solo celdas con k>1; k/n/\%; n=19). Elaboracion propia.",
    )
    write_longtblr(
        t_target_purpose,
        out_tab / "eval_targetclass_vs_purpose_es.tex",
        "X[2.1,l,m] X[2.3,l,m] X[0.6,c,m] X[0.6,c,m] X[0.8,c,m]",
        "tab:eval_targetclass_vs_purpose",
        r"Resultados de desempeno: coocurrencia entre objetivo agregado D1 y proposito de inferencia D2 (k/n/\%; n=19). Elaboracion propia.",
    )
    write_longtblr(
        t_trace,
        out_tab / "eval_trazabilidad_unidades_es.tex",
        "X[0.8,c,m] X[2.1,l,m] X[1.4,l,m] X[1.2,l,m] X[1.8,l,m]",
        "tab:eval_trazabilidad_unidades",
        r"Resultados de desempeno: trazabilidad por estudio para unidad comparable, familia de metrica y protocolo. Elaboracion propia.",
    )

    # Figuras
    plot_metric_frequency_general(t_metric_general, out_fig)
    plot_metric_frequency(t_metric_freq, core_units, out_fig)
    plot_metric_boxplots(values_df, core_units, out_fig)
    plot_heatmap_from_cross(
        t_ds_unit,
        "Data_source_type",
        "Unidad_comparable",
        "Coocurrencia: origen de datos vs unidad comparable (k>1)",
        out_fig,
        "fig03_cooc_datasource_vs_unidad",
        add_left_totals_col=True,
    )
    print(f"[OK] Tablas eval es: {out_tab}")
    print(f"[OK] Figuras eval es: {out_fig}")


if __name__ == "__main__":
    main()
