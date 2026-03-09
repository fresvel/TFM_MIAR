#!/usr/bin/env python3
"""Generate LaTeX spacing settings from YAML."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Any

import yaml


def _pick(data: dict[str, Any], path: list[str], default: Any = None) -> Any:
    node: Any = data
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def _norm_dim(value: Any, field_name: str, required: bool) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"Missing required value for '{field_name}'.")
        return None
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        dim = value.strip()
        if not dim:
            if required:
                raise ValueError(f"Empty required value for '{field_name}'.")
            return None
        return dim
    raise ValueError(
        f"Invalid value type for '{field_name}': {type(value).__name__}. "
        "Use a string LaTeX dimension or null."
    )


def _norm_hex_color(value: Any, field_name: str, default: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(
            f"Invalid value type for '{field_name}': {type(value).__name__}. "
            "Use a 6-digit hex string, e.g. '79C6EB' or '#79C6EB'."
        )
    color = value.strip()
    if color.startswith("#"):
        color = color[1:]
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", color):
        raise ValueError(
            f"Invalid color for '{field_name}': '{value}'. "
            "Use a 6-digit hex string, e.g. '79C6EB'."
        )
    return color.upper()


def build_tex(yaml_data: dict[str, Any], source_name: str) -> str:
    paragraph_indent = _norm_dim(
        _pick(yaml_data, ["paragraph", "indent"], "0pt"),
        "paragraph.indent",
        required=True,
    )
    paragraph_skip = _norm_dim(
        _pick(yaml_data, ["paragraph", "skip"], r"0.8\baselineskip"),
        "paragraph.skip",
        required=True,
    )

    section_before = _norm_dim(
        _pick(yaml_data, ["headings", "section", "before"], "0pt"),
        "headings.section.before",
        required=True,
    )
    section_after = _norm_dim(
        _pick(yaml_data, ["headings", "section", "after"], "0.15cm"),
        "headings.section.after",
        required=True,
    )
    subsection_before = _norm_dim(
        _pick(yaml_data, ["headings", "subsection", "before"], "0.5cm"),
        "headings.subsection.before",
        required=True,
    )
    subsection_after = _norm_dim(
        _pick(yaml_data, ["headings", "subsection", "after"], "0.2cm"),
        "headings.subsection.after",
        required=True,
    )
    section_title_pad = _norm_dim(
        _pick(yaml_data, ["headings", "section_title_pad"], "0.2cm"),
        "headings.section_title_pad",
        required=True,
    )

    subsub_before = _norm_dim(
        _pick(yaml_data, ["headings", "subsubsection", "before"], None),
        "headings.subsubsection.before",
        required=False,
    )
    subsub_after = _norm_dim(
        _pick(yaml_data, ["headings", "subsubsection", "after"], None),
        "headings.subsubsection.after",
        required=False,
    )
    if (subsub_before is None) != (subsub_after is None):
        raise ValueError(
            "Both 'headings.subsubsection.before' and "
            "'headings.subsubsection.after' must be set together or both null."
        )

    table_around = _norm_dim(
        _pick(yaml_data, ["tables", "around"], None),
        "tables.around",
        required=False,
    )
    caption_before = _norm_dim(
        _pick(yaml_data, ["tables", "caption_before"], None),
        "tables.caption_before",
        required=False,
    )
    caption_after = _norm_dim(
        _pick(yaml_data, ["tables", "caption_after"], None),
        "tables.caption_after",
        required=False,
    )

    optional_commands: list[str] = []
    if subsub_before is not None and subsub_after is not None:
        optional_commands.append(
            rf"\titlespacing*{{\subsubsection}}{{0pt}}{{{subsub_before}}}{{{subsub_after}}}"
        )
    if table_around is not None:
        optional_commands.append(rf"\setlength{{\textfloatsep}}{{{table_around}}}")
        optional_commands.append(rf"\setlength{{\floatsep}}{{{table_around}}}")
        optional_commands.append(rf"\setlength{{\intextsep}}{{{table_around}}}")
    if caption_before is not None:
        optional_commands.append(rf"\setlength{{\abovecaptionskip}}{{{caption_before}}}")
    if caption_after is not None:
        optional_commands.append(rf"\setlength{{\belowcaptionskip}}{{{caption_after}}}")

    default_link_color = "79C6EB"
    internal_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "internal"], default_link_color),
        "links.internal",
        default_link_color,
    )
    figure_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "figure"], default_link_color),
        "links.figure",
        default_link_color,
    )
    table_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "table"], default_link_color),
        "links.table",
        default_link_color,
    )
    annex_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "annex"], default_link_color),
        "links.annex",
        default_link_color,
    )
    bibliography_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "bibliography"], default_link_color),
        "links.bibliography",
        default_link_color,
    )
    url_link_color = _norm_hex_color(
        _pick(yaml_data, ["links", "url"], default_link_color),
        "links.url",
        default_link_color,
    )

    lines = [
        "% Auto-generated file. Do not edit directly.",
        f"% Source: {source_name}",
        rf"\providecommand{{\VIUParagraphIndent}}{{{paragraph_indent}}}",
        rf"\providecommand{{\VIUParagraphSkip}}{{{paragraph_skip}}}",
        rf"\providecommand{{\VIUSectionBeforeSkip}}{{{section_before}}}",
        rf"\providecommand{{\VIUSectionAfterSkip}}{{{section_after}}}",
        rf"\providecommand{{\VIUSubsectionBeforeSkip}}{{{subsection_before}}}",
        rf"\providecommand{{\VIUSubsectionAfterSkip}}{{{subsection_after}}}",
        rf"\providecommand{{\VIUSectionTitlePadLen}}{{{section_title_pad}}}",
        rf"\definecolor{{VIULinkInternalColor}}{{HTML}}{{{internal_link_color}}}",
        rf"\definecolor{{VIULinkFigureColor}}{{HTML}}{{{figure_link_color}}}",
        rf"\definecolor{{VIULinkTableColor}}{{HTML}}{{{table_link_color}}}",
        rf"\definecolor{{VIULinkAnnexColor}}{{HTML}}{{{annex_link_color}}}",
        rf"\definecolor{{VIULinkBibliographyColor}}{{HTML}}{{{bibliography_link_color}}}",
        rf"\definecolor{{VIULinkUrlColor}}{{HTML}}{{{url_link_color}}}",
    ]

    if optional_commands:
        lines.append(r"\newcommand{\VIUApplyOptionalSpacing}{%")
        for cmd in optional_commands:
            lines.append(f"  {cmd}%")
        lines.append("}")
    else:
        lines.append(r"\newcommand{\VIUApplyOptionalSpacing}{}")

    lines.extend(
        [
            r"\newcommand{\VIUApplyLinkColors}{%",
            r"  \hypersetup{%",
            r"    colorlinks=true,%",
            r"    linkcolor=VIULinkInternalColor,%",
            r"    citecolor=VIULinkBibliographyColor,%",
            r"    urlcolor=VIULinkUrlColor,%",
            r"    filecolor=VIULinkUrlColor%",
            r"  }%",
            r"}",
            r"\newcommand{\figref}[1]{\hyperref[#1]{\textcolor{VIULinkFigureColor}{Figura~\ref*{#1}}}}",
            r"\newcommand{\tabref}[1]{\hyperref[#1]{\textcolor{VIULinkTableColor}{Tabla~\ref*{#1}}}}",
            r"\newcommand{\aneref}[1]{\hyperref[#1]{\textcolor{VIULinkAnnexColor}{Anexo~\ref*{#1}}}}",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate spacing TeX config from YAML."
    )
    parser.add_argument("input_yaml", type=Path, help="Input YAML config path")
    parser.add_argument("output_tex", type=Path, help="Output TeX file path")
    args = parser.parse_args()

    yaml_data_raw = yaml.safe_load(args.input_yaml.read_text(encoding="utf-8"))
    yaml_data = yaml_data_raw if isinstance(yaml_data_raw, dict) else {}

    output = build_tex(yaml_data, str(args.input_yaml))
    args.output_tex.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
