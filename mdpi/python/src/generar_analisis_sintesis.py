#!/usr/bin/env python3
"""
Genera la figura de flujo analitico y la escribe en:
  - Informe/assets/figuras/metodología/analisis_sintesis.png
  - mdpi/mdpi/assets/figuras/metodologia/analisis_sintesis.png

Uso:
  python scripts/figuras/generar_analisis_sintesis.py
"""

import textwrap
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from paths import REPO_ROOT


def add_card(ax, x, y, w, h, title, body, num, colors, alt=False):
    card_fc = colors["card_alt"] if alt else colors["card"]
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=1.2,
            edgecolor=colors["border"],
            facecolor=card_fc,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (x, y + h - 1.08),
            w,
            1.08,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=0,
            facecolor=colors["accent"],
            alpha=0.16,
        )
    )
    ax.text(
        x + 0.35,
        y + h - 0.56,
        f"{num}. {title}",
        ha="left",
        va="center",
        fontsize=17,
        color=colors["title"],
        fontweight="bold",
        linespacing=1.15,
    )
    ax.text(
        x + 0.35,
        y + h - 1.45,
        textwrap.fill(body, width=34),
        ha="left",
        va="top",
        fontsize=13.5,
        color=colors["body"],
        linespacing=1.35,
    )


def main():
    outputs = (
        REPO_ROOT / "Informe" / "assets" / "figuras" / "metodología" / "analisis_sintesis.png",
        REPO_ROOT / "mdpi" / "mdpi" / "assets" / "figuras" / "metodologia" / "analisis_sintesis.png",
    )

    colors = {
        "bg": "#F5F7FA",
        "card": "#F2F2F2",
        "card_alt": "#ECECEC",
        "border": "#5A5A5A",
        "title": "#1F2A44",
        "body": "#3D4B63",
        "accent": "#ED7D31",
        "muted": "#7A879A",
    }

    fig = plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.gca()
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    fig.patch.set_facecolor(colors["bg"])
    ax.set_facecolor(colors["bg"])

    w, h = 4.45, 2.55
    p1 = (0.6, 5.9)
    p2 = (0.6, 2.4)
    p3 = (5.75, 5.9)
    p4 = (5.75, 2.2)
    p5 = (10.9, 4.05)

    add_card(
        ax,
        *p1,
        w,
        h,
        "Preparación Analítica",
        "Normalización semántica, descomposición y armonización con trazabilidad por estudio.",
        "1",
        colors,
        alt=False,
    )
    add_card(
        ax,
        *p2,
        w,
        h,
        "Evidencia Cuantitativa\ny Visual",
        "Frecuencias (k/n, %), tablas y paneles comparativos por dimensión analítica.",
        "2",
        colors,
        alt=True,
    )
    add_card(
        ax,
        *p3,
        w,
        h,
        "Identificación de Patrones",
        "Tablas cruzadas y coocurrencias para configuraciones y variaciones entre estudios.",
        "3",
        colors,
        alt=False,
    )
    add_card(
        ax,
        *p4,
        w,
        h,
        "Construcción de Perfiles",
        "Perfiles compactos de configuración como insumos reutilizables de diseño.",
        "4",
        colors,
        alt=True,
    )
    add_card(
        ax,
        *p5,
        w,
        h,
        "Integración y Redacción",
        "Narrativa continua y trazable vinculando evidencia, visualización e inferencia analítica.",
        "5",
        colors,
        alt=False,
    )

    arr = dict(
        arrowstyle="Simple,head_width=14,head_length=16",
        linewidth=1.6,
        color=colors["accent"],
        alpha=0.9,
    )
    ax.add_patch(
        FancyArrowPatch(
            (p1[0] + w / 2, p1[1] - 0.06),
            (p2[0] + w / 2, p2[1] + h + 0.06),
            connectionstyle="arc3,rad=0.0",
            **arr,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (p2[0] + w + 0.06, p2[1] + h / 2),
            (p3[0] - 0.06, p3[1] + h / 2),
            connectionstyle="angle3,angleA=0,angleB=90",
            **arr,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (p3[0] + w / 2, p3[1] - 0.06),
            (p4[0] + w / 2, p4[1] + h + 0.06),
            connectionstyle="arc3,rad=0.0",
            **arr,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (p4[0] + w + 0.06, p4[1] + h / 2),
            (p5[0] - 0.06, p5[1] + h / 2),
            connectionstyle="angle3,angleA=0,angleB=90",
            **arr,
        )
    )

    for (x, y), n in zip([p1, p2, p3, p4, p5], ["I", "II", "III", "IV", "V"]):
        ax.add_patch(
            Circle(
                (x + w - 0.5, y + h - 0.57),
                0.26,
                facecolor="white",
                edgecolor="#8AA0B9",
                linewidth=1.2,
            )
        )
        ax.text(
            x + w - 0.5,
            y + h - 0.57,
            n,
            ha="center",
            va="center",
            fontsize=9.5,
            color=colors["muted"],
            fontweight="bold",
        )

    plt.tight_layout(pad=0.2)
    for out in outputs:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=170)
        print(f"Guardado: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
