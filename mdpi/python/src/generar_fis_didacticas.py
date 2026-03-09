#!/usr/bin/env python3
"""
Genera figuras didacticas para la seccion de logica difusa (Tema 2) y
las escribe en ambos arboles de compilacion:
  - Informe/assets/figuras/d2/*.png
  - mdpi/mdpi/assets/figuras/d2/*.png
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from paths import REPO_ROOT


SCRIPT_DIR = Path(__file__).resolve().parent
TARGET_DIRS = (
    REPO_ROOT / "Informe" / "assets" / "figuras" / "d2",
    REPO_ROOT / "mdpi" / "mdpi" / "assets" / "figuras" / "d2",
)


def target_paths(filename: str) -> tuple[Path, ...]:
    return tuple(base / filename for base in TARGET_DIRS)


def save_multi(fig: plt.Figure, filename: str) -> tuple[Path, ...]:
    outputs = target_paths(filename)
    for out_path in outputs:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return outputs


def tri(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    y = np.zeros_like(x)
    i = (x >= a) & (x <= b)
    y[i] = (x[i] - a) / (b - a + 1e-12)
    j = (x >= b) & (x <= c)
    y[j] = (c - x[j]) / (c - b + 1e-12)
    return np.clip(y, 0, 1)


def trap(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    y = np.zeros_like(x)
    i = (x >= a) & (x < b)
    y[i] = (x[i] - a) / (b - a + 1e-12)
    j = (x >= b) & (x <= c)
    y[j] = 1.0
    k = (x > c) & (x <= d)
    y[k] = (d - x[k]) / (d - c + 1e-12)
    return np.clip(y, 0, 1)


def style_axis(ax):
    ax.grid(alpha=0.22, linestyle="--", linewidth=0.7)
    ax.set_facecolor("#F7F8FA")
    for s in ax.spines.values():
        s.set_color("#9AA4B2")


def fig_conjuntos():
    x = np.linspace(0, 200, 1200)
    fig, ax = plt.subplots(figsize=(8.8, 4.9), dpi=170)
    low = trap(x, 0, 0, 35, 70)
    med = tri(x, 45, 90, 140)
    high = trap(x, 110, 150, 200, 200)

    ax.plot(x, low, color="#1F77B4", linewidth=2.4, label="Bajo (trapecio)")
    ax.plot(x, med, color="#ED7D31", linewidth=2.4, label="Medio (triángulo)")
    ax.plot(x, high, color="#2CA02C", linewidth=2.4, label="Alto (trapecio)")

    ax.set_xlabel("Concentración PM2.5")
    ax.set_ylabel("Grado de pertenencia")
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    style_axis(ax)

    fig.tight_layout()
    save_multi(fig, "fig08a_conjuntos_borrosos.png")


def fig_numero_borroso_alpha():
    x = np.linspace(0, 200, 1200)
    fig, ax = plt.subplots(figsize=(8.8, 4.9), dpi=170)
    ntri = tri(x, 40, 90, 145)
    ntrap = trap(x, 25, 55, 110, 165)

    ax.plot(x, ntri, color="#9467BD", linewidth=2.4, label="Número borroso triangular")
    ax.plot(x, ntrap, color="#17BECF", linewidth=2.4, label="Número borroso trapezoidal")

    alpha = 0.5
    ax.axhline(alpha, color="#444", linestyle="--", linewidth=1.2)
    x1, x2 = 57.5, 117.5   # aprox para triangular (alfa=0.5)
    ax.vlines([x1, x2], 0, alpha, colors="#444", linestyles=":", linewidth=1.2)
    ax.text((x1 + x2) / 2, alpha + 0.04, r"Corte $\alpha=0.5$", ha="center", fontsize=9)

    ax.set_xlabel("Universo de discurso")
    ax.set_ylabel("Grado de pertenencia")
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    style_axis(ax)

    fig.tight_layout()
    save_multi(fig, "fig08b_numero_borroso_alpha.png")


def fig_defuzzificacion():
    x = np.linspace(0, 100, 1200)
    c1 = np.minimum(tri(x, 10, 25, 45), 0.55)
    c2 = np.minimum(tri(x, 35, 60, 85), 0.80)
    c3 = np.minimum(tri(x, 65, 85, 98), 0.50)
    agg = np.maximum.reduce([c1, c2, c3])

    num = np.trapezoid(x * agg, x)
    den = np.trapezoid(agg, x) + 1e-12
    cog = num / den

    # Configuración Sugeno/TSK: salida por promedio ponderado de consecuentes.
    alpha = np.array([0.55, 0.80, 0.50])
    z_rule = np.array([22.0, 58.0, 84.0])
    z_sug = float(np.sum(alpha * z_rule) / (np.sum(alpha) + 1e-12))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.2), dpi=170)

    # Panel A: Mamdani
    ax1.fill_between(x, 0, agg, color="#ED7D31", alpha=0.28, label="Salida agregada")
    ax1.plot(x, c1, color="#1F77B4", linewidth=1.8, label="Regla 1 (recortada)")
    ax1.plot(x, c2, color="#2CA02C", linewidth=1.8, label="Regla 2 (recortada)")
    ax1.plot(x, c3, color="#9467BD", linewidth=1.8, label="Regla 3 (recortada)")
    ax1.axvline(cog, color="#D62728", linewidth=2.0, linestyle="--", label=f"Centroide = {cog:.2f}")
    ax1.set_xlabel("Universo de salida (riesgo AQI)")
    ax1.set_ylabel("Grado de pertenencia")
    ax1.set_ylim(-0.02, 1.05)
    style_axis(ax1)
    ax1.legend(loc="upper left", fontsize=8.6, frameon=True)

    # Panel B: Sugeno/TSK
    idx = np.arange(1, 4)
    colors = ["#1F77B4", "#2CA02C", "#9467BD"]
    for i, (a_i, z_i, c_i) in enumerate(zip(alpha, z_rule, colors), start=1):
        ax2.vlines(z_i, 0, a_i, color=c_i, linewidth=4.2, alpha=0.95, label=f"Regla {i}: $\\alpha_{i}$, $z_{i}$")
        ax2.plot([z_i], [a_i], marker="o", color=c_i, markersize=7)
    ax2.axvline(z_sug, color="#D62728", linewidth=2.0, linestyle="--", label=f"Salida ponderada = {z_sug:.2f}")
    ax2.set_xlabel("Consecuente numérico por regla")
    ax2.set_ylabel("Peso de activación")
    ax2.set_ylim(0, 1.05)
    ax2.set_xlim(10, 95)
    ax2.set_xticks(z_rule)
    ax2.set_xticklabels([f"$z_{{{i}}}$={int(v)}" for i, v in zip(idx, z_rule)])
    style_axis(ax2)
    ax2.legend(loc="upper left", fontsize=8.4, frameon=True)

    fig.tight_layout(pad=1.0)
    save_multi(fig, "fig09_defuzzificacion_centroide.png")


def fig_flujo_fis():
    fig = plt.figure(figsize=(14, 3.6), dpi=170)
    ax = plt.gca()
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 3.6)
    ax.axis("off")

    nodes = [
        (0.4, 1.0, 2.2, 1.45, "Entradas\ncrisp"),
        (3.0, 1.0, 2.2, 1.45, "Fuzzificación"),
        (5.6, 1.0, 2.2, 1.45, "Base de\nreglas"),
        (8.2, 1.0, 2.2, 1.45, "Agregación"),
        (10.8, 1.0, 2.2, 1.45, "Defuzzificación"),
    ]
    for (x, y, w, h, t) in nodes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.03,rounding_size=0.12",
                linewidth=1.2,
                edgecolor="#4A4A4A",
                facecolor="#F2F2F2",
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (x, y + h - 0.45),
                w,
                0.45,
                boxstyle="round,pad=0.03,rounding_size=0.12",
                linewidth=0,
                facecolor="#ED7D31",
                alpha=0.16,
            )
        )
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=12, color="#1F2A44", fontweight="bold")

    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + nodes[i][2] + 0.08
        x2 = nodes[i + 1][0] - 0.08
        y = 1.72
        ax.add_patch(
            FancyArrowPatch(
                (x1, y),
                (x2, y),
                arrowstyle="Simple,head_width=9,head_length=10",
                color="#ED7D31",
                linewidth=1.6,
            )
        )

    ax.text(13.5, 1.72, "Salida\ncrisp", ha="center", va="center", fontsize=12, fontweight="bold", color="#1F2A44")
    ax.add_patch(
        FancyArrowPatch(
            (13.1, 1.72),
            (13.35, 1.72),
            arrowstyle="Simple,head_width=9,head_length=10",
            color="#ED7D31",
            linewidth=1.6,
        )
    )

    save_multi(fig, "fig10_flujo_fis.png")


def fig_anfis_capas():
    fig = plt.figure(figsize=(8.8, 5.4), dpi=170)
    ax = plt.gca()
    ax.set_xlim(0, 8.8)
    ax.set_ylim(0, 7.4)
    ax.axis("off")

    nodes = [
        (0.4, 5.3, 3.0, 1.55, "Capa 1\nFuzzificación"),
        (4.4, 5.3, 3.0, 1.55, "Capa 2\nFuerza de regla"),
        (0.4, 3.1, 3.0, 1.55, "Capa 3\nNormalización"),
        (4.4, 3.1, 3.0, 1.55, "Capa 4\nConsecuente"),
        (2.4, 0.9, 3.0, 1.55, "Capa 5\nSalida"),
    ]
    subtitles = [
        r"$\mu_{A_i}(x),\,\mu_{B_i}(y)$",
        r"$w_i=\mu_{A_i}(x)\mu_{B_i}(y)$",
        r"$\bar{w}_i=\frac{w_i}{\sum_j w_j}$",
        r"$f_i=p_i x+q_i y+r_i$",
        r"$z=\sum_i \bar{w}_i f_i$",
    ]

    for (x, y, w, h, t), s in zip(nodes, subtitles):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.03,rounding_size=0.12",
                linewidth=1.2,
                edgecolor="#4A4A4A",
                facecolor="#F2F2F2",
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (x, y + h - 0.48),
                w,
                0.48,
                boxstyle="round,pad=0.03,rounding_size=0.12",
                linewidth=0,
                facecolor="#ED7D31",
                alpha=0.16,
            )
        )
        ax.text(
            x + w / 2,
            y + h * 0.61,
            t,
            ha="center",
            va="center",
            fontsize=11.6,
            color="#1F2A44",
            fontweight="bold",
        )
        ax.text(
            x + w / 2,
            y + h * 0.28,
            s,
            ha="center",
            va="center",
            fontsize=11.2,
            color="#2F4B6E",
        )

    # Secuencia ANFIS en 3 filas: C1 -> C2 -> C3 -> C4 -> C5.
    arrows = [
        ((3.5, 6.05), (4.3, 6.05), "arc3,rad=0.0"),      # C1 -> C2
        ((5.9, 5.2), (1.9, 4.7), "arc3,rad=-0.22"),      # C2 -> C3
        ((3.5, 3.85), (4.3, 3.85), "arc3,rad=0.0"),      # C3 -> C4
        ((5.9, 3.0), (3.9, 2.55), "arc3,rad=-0.12"),     # C4 -> C5
    ]
    for (x1, y1), (x2, y2), conn in arrows:
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="Simple,head_width=8,head_length=9",
                color="#ED7D31",
                linewidth=1.5,
                connectionstyle=conn,
            )
        )

    ax.text(0.35, 7.05, "Entradas: x (contaminante), y (variable ambiental)", fontsize=10.8, color="#3A4C66")
    ax.text(0.35, 0.25, "Parámetros entrenables: MF (premisa) y p,q,r (consecuente)", fontsize=10.8, color="#3A4C66")

    save_multi(fig, "fig11a_anfis_capas.png")


def fig_anfis_superficie():
    x = np.linspace(0, 1, 70)
    y = np.linspace(0, 1, 70)
    X, Y = np.meshgrid(x, y)

    # Activaciones difusas (3 reglas) para una superficie tipo ANFIS.
    w1 = np.exp(-((X - 0.20) ** 2 / 0.06 + (Y - 0.30) ** 2 / 0.08))
    w2 = np.exp(-((X - 0.55) ** 2 / 0.10 + (Y - 0.55) ** 2 / 0.10))
    w3 = np.exp(-((X - 0.82) ** 2 / 0.07 + (Y - 0.75) ** 2 / 0.08))

    f1 = 22 + 33 * X + 12 * Y
    f2 = 35 + 15 * X + 29 * Y
    f3 = 50 + 27 * X + 21 * Y

    Z = (w1 * f1 + w2 * f2 + w3 * f3) / (w1 + w2 + w3 + 1e-12)

    fig = plt.figure(figsize=(8.8, 5.2), dpi=170)
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X * 100, Y * 100, Z, cmap="viridis", linewidth=0, antialiased=True, alpha=0.95)
    ax.set_xlabel("Contaminante (%)", labelpad=8)
    ax.set_ylabel("Variable ambiental (%)", labelpad=8)
    ax.set_zlabel("Salida estimada (nivel AQI)", labelpad=8)
    ax.view_init(elev=28, azim=-130)
    cbar = fig.colorbar(surf, shrink=0.70, pad=0.08)
    cbar.set_label("Nivel de salida", rotation=90)

    fig.tight_layout()
    save_multi(fig, "fig11b_anfis_superficie.png")


def main():
    fig_conjuntos()
    fig_numero_borroso_alpha()
    fig_defuzzificacion()
    fig_flujo_fis()
    fig_anfis_capas()
    fig_anfis_superficie()
    print("Generadas:")
    for out in target_paths("fig08a_conjuntos_borrosos.png"):
        print(f" - {out}")
    for out in target_paths("fig08b_numero_borroso_alpha.png"):
        print(f" - {out}")
    for out in target_paths("fig09_defuzzificacion_centroide.png"):
        print(f" - {out}")
    for out in target_paths("fig10_flujo_fis.png"):
        print(f" - {out}")
    for out in target_paths("fig11a_anfis_capas.png"):
        print(f" - {out}")
    for out in target_paths("fig11b_anfis_superficie.png"):
        print(f" - {out}")


if __name__ == "__main__":
    main()
