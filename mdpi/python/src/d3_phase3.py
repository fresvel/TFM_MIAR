#!/usr/bin/env python3
"""
Fase 3 (D3) - Decisiones de implementacion.

Estado actual:
- Decision 1: Arquitectura de referencia.
- Decision 2: Estrategia temporal de procesamiento.
- Decision 3: Stack de comunicacion/plataforma.
- Decision 4: Visualizacion y alertamiento.
- Decision 5: Contexto de despliegue.
- Decision 6: Instrumentacion y hardware.
- Decision 7: Evidencia operativa de tiempo real.

Genera:
- Tabla de decision 1 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 2 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 3 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 4 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 5 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 6 (k/n/%) en CSV y LaTeX (longtblr), es/en.
- Tabla de decision 7 (k/n/%) en CSV y LaTeX (longtblr), es/en.
"""

from __future__ import annotations

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


def build_decision1_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_arch = col_or_fallback(df, "D3_Platform_architecture_norm", "D3_Platform_architecture")

    arch_by_article: dict[str, set[str]] = {}
    for _, r in df[["Article_ID", col_arch]].iterrows():
        aid = str(r["Article_ID"])
        vals = set(parse_multi(r[col_arch], include_nr=True))
        if not vals:
            vals = {"NR"}
        arch_by_article[aid] = vals

    groups = [
        ("Edge/Cloud", {"IoT_Edge_Cloud", "IoT_Fog_Layered"}),
        ("IoT_2Tier", {"IoT_2Tier"}),
        ("Alternativas", {"WSN_Pipeline", "Sensor_Node_External_Analytics", "Standalone_Node_PC"}),
        ("NR", {"NR"}),
    ]

    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for g_name, g_cats in groups:
        k = 0
        for aid, cats in arch_by_article.items():
            if cats.intersection(g_cats):
                k += 1
        pct = round(100.0 * float(k) / float(n), 1)
        cats_txt = "; ".join(sorted(g_cats))

        if g_name == "Edge/Cloud":
            note_es = "Familia con mayor cobertura; referencia principal para diseno base."
            note_en = "Highest-coverage family; primary reference for baseline design."
        elif g_name == "IoT_2Tier":
            note_es = "Segundo patron dominante; alternativa estable para despliegues locales."
            note_en = "Second dominant pattern; stable alternative for local deployments."
        elif g_name == "Alternativas":
            note_es = "Patrones contextuales (pipeline, nodo+analitica externa, standalone)."
            note_en = "Contextual patterns (pipeline, node+external analytics, standalone)."
        else:
            note_es = "Sin detalle estructural suficiente para clasificar arquitectura."
            note_en = "Insufficient structural detail to classify architecture."

        rows_es.append({
            "Opcion_arquitectura": g_name,
            "Categorias_incluidas": cats_txt,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Architecture_option": g_name,
            "Included_categories": cats_txt,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
        })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def build_decision2_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_proc = col_or_fallback(df, "D3_Processing_mode_norm", "D3_Processing_mode")

    proc_by_article: dict[str, set[str]] = {}
    for _, r in df[["Article_ID", col_proc]].iterrows():
        aid = str(r["Article_ID"])
        vals = set(parse_multi(r[col_proc], include_nr=True))
        if not vals:
            vals = {"NR"}
        proc_by_article[aid] = vals

    groups = [
        ("Tiempo_real_estricto", {"Real_Time_Edge", "Real_Time_Distributed"}),
        ("Cuasi_tiempo_real", {"Near_Real_Time"}),
        ("Hibrido", {"Hybrid"}),
        ("Offline", {"Offline_Analytics"}),
        ("NR", {"NR"}),
    ]

    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for g_name, g_cats in groups:
        k = 0
        for _, cats in proc_by_article.items():
            if cats.intersection(g_cats):
                k += 1
        pct = round(100.0 * float(k) / float(n), 1)
        cats_txt = "; ".join(sorted(g_cats))

        if g_name == "Tiempo_real_estricto":
            note_es = "Operacion de baja latencia en borde/distribuida; patron operativo fuerte."
            note_en = "Low-latency edge/distributed operation; strong operational pattern."
        elif g_name == "Cuasi_tiempo_real":
            note_es = "Modo dominante del corpus para monitoreo continuo con ventanas de actualizacion."
            note_en = "Dominant corpus mode for continuous monitoring with update windows."
        elif g_name == "Hibrido":
            note_es = "Combina componente en linea con analitica diferida/auxiliar."
            note_en = "Combines online operation with deferred/auxiliary analytics."
        elif g_name == "Offline":
            note_es = "Casos puntuales sin bucle operativo en linea."
            note_en = "Isolated cases without online operational loop."
        else:
            note_es = "Sin detalle temporal suficiente para clasificar modo de procesamiento."
            note_en = "Insufficient temporal detail to classify processing mode."

        rows_es.append({
            "Estrategia_temporal": g_name,
            "Categorias_incluidas": cats_txt,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Temporal_strategy": g_name,
            "Included_categories": cats_txt,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
        })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def build_decision3_table(df: pd.DataFrame, lang: str, recurrent_threshold: int = 3) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_stack = col_or_fallback(df, "D3_Communication_and_tech_norm", "D3_Communication_and_tech")

    rows: list[tuple[str, str]] = []
    for _, r in df[["Article_ID", col_stack]].iterrows():
        vals = parse_multi(r[col_stack], include_nr=False)
        for v in vals:
            rows.append((str(r["Article_ID"]), v))

    if not rows:
        if lang == "es":
            return pd.DataFrame(columns=["Tecnologia", "k", "n", "%", "Patron", "Lectura_decision"])
        return pd.DataFrame(columns=["Technology", "k", "n", "%", "Pattern", "Decision_reading"])

    long = pd.DataFrame(rows, columns=["Article_ID", "Tecnologia"]).drop_duplicates()
    counts = (
        long.groupby("Tecnologia")["Article_ID"]
        .nunique()
        .sort_values(ascending=False)
    )

    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for tech, k in counts.items():
        pct = round(100.0 * float(k) / float(n), 1)
        is_recurrent = int(k) >= recurrent_threshold
        if is_recurrent:
            pat_es = "Recurrente"
            pat_en = "Recurrent"
            note_es = "Elemento de stack repetido en multiples estudios; candidato a base comun."
            note_en = "Stack element repeated across multiple studies; candidate for common baseline."
        else:
            pat_es = "Contextual"
            pat_en = "Contextual"
            note_es = "Uso puntual/especializado segun dominio, hardware o ecosistema del estudio."
            note_en = "Point/specialized usage depending on domain, hardware, or study ecosystem."

        rows_es.append({
            "Tecnologia": tech,
            "k": int(k),
            "n": n,
            "%": pct,
            "Patron": pat_es,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Technology": tech,
            "k": int(k),
            "n": n,
            "%": pct,
            "Pattern": pat_en,
            "Decision_reading": note_en,
        })

    # Recurrentes primero, luego contextuales, manteniendo orden por k.
    if lang == "es":
        out = pd.DataFrame(rows_es)
        out["__ord"] = out["Patron"].map({"Recurrente": 0, "Contextual": 1}).fillna(9)
        out = out.sort_values(["__ord", "k", "Tecnologia"], ascending=[True, False, True]).drop(columns="__ord")
        return out.reset_index(drop=True)

    out = pd.DataFrame(rows_en)
    out["__ord"] = out["Pattern"].map({"Recurrent": 0, "Contextual": 1}).fillna(9)
    out = out.sort_values(["__ord", "k", "Technology"], ascending=[True, False, True]).drop(columns="__ord")
    return out.reset_index(drop=True)


def build_decision4_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_vis = col_or_fallback(df, "D3_Visualization_alerting_norm", "D3_Visualization_alerting")

    visual_set = {
        "Dashboard",
        "Local_Display",
        "TimeSeries_Plot",
        "AQI_Color_Index",
        "Map_Visualization",
        "Risk_Graph",
        "Model_Visualization",
    }
    alert_set = {
        "Alarm_Module",
        "Medical_Alert",
    }

    # Clasificacion por estrategia de salida a nivel de estudio.
    strategy_rows: list[dict[str, str]] = []
    for _, r in df[["Article_ID", col_vis]].iterrows():
        vals = set(parse_multi(r[col_vis], include_nr=False))
        has_visual = bool(vals.intersection(visual_set))
        has_alert = bool(vals.intersection(alert_set))

        if has_visual and has_alert:
            strategy = "Mixto_visual_alerta"
        elif has_visual:
            strategy = "Dashboard_visual"
        elif has_alert:
            strategy = "Alerta"
        else:
            strategy = "NR"

        strategy_rows.append({"Article_ID": str(r["Article_ID"]), "Strategy": strategy})

    st = pd.DataFrame(strategy_rows)
    counts = st.groupby("Strategy")["Article_ID"].nunique().to_dict()

    order = ["Dashboard_visual", "Alerta", "Mixto_visual_alerta", "NR"]
    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for key in order:
        k = int(counts.get(key, 0))
        pct = round(100.0 * float(k) / float(n), 1)

        if key == "Dashboard_visual":
            crit = "Presencia de salidas visuales (dashboard/plots/display) sin modulo de alerta explicito."
            note_es = "Predomina la capa visual para monitoreo operativo."
            crit_en = "Presence of visual outputs (dashboard/plots/display) without explicit alert module."
            note_en = "Visual layer dominates operational monitoring."
            name_es = "Dashboard_visual"
            name_en = "Dashboard_visual"
        elif key == "Alerta":
            crit = "Presencia de alerta explicita sin componente visual reportado."
            note_es = "Casos puntuales con orientacion a evento/alarma."
            crit_en = "Explicit alert presence without reported visual component."
            note_en = "Isolated cases with event/alarm orientation."
            name_es = "Alerta"
            name_en = "Alert"
        elif key == "Mixto_visual_alerta":
            crit = "Convivencia de salida visual y modulo de alerta en el mismo estudio."
            note_es = "Patron mixto para seguimiento continuo y respuesta operativa."
            crit_en = "Coexistence of visual output and alert module in the same study."
            note_en = "Mixed pattern for continuous monitoring and operational response."
            name_es = "Mixto_visual_alerta"
            name_en = "Mixed_visual_alert"
        else:
            crit = "Sin evidencia suficiente para clasificar estrategia de salida."
            note_es = "NR en visualizacion/alertamiento."
            crit_en = "Insufficient evidence to classify output strategy."
            note_en = "NR in visualization/alerting."
            name_es = "NR"
            name_en = "NR"

        rows_es.append({
            "Estrategia_salida": name_es,
            "Criterio_operativo": crit,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Output_strategy": name_en,
            "Operational_criterion": crit_en,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
        })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def build_decision5_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_ctx = col_or_fallback(df, "D3_Deployment_context_norm", "D3_Deployment_context")

    indoor_tokens = {
        "Indoor",
        "Residential",
        "Educational_Classroom",
        "Healthcare_Facility",
        "Healthcare_Personalized",
        "Campus",
        "Industrial",
    }
    outdoor_tokens = {
        "Outdoor",
        "Urban",
        "Rural",
        "Desert",
    }

    rows: list[dict[str, str]] = []
    for _, r in df[["Article_ID", col_ctx]].iterrows():
        vals = set(parse_multi(r[col_ctx], include_nr=False))
        has_in = bool(vals.intersection(indoor_tokens))
        has_out = bool(vals.intersection(outdoor_tokens))

        if has_in and has_out:
            strategy = "Mixto_interior_exterior"
        elif has_in:
            strategy = "Interior"
        elif has_out:
            strategy = "Exterior"
        else:
            strategy = "NR"

        rows.append({"Article_ID": str(r["Article_ID"]), "Strategy": strategy})

    st = pd.DataFrame(rows)
    counts = st.groupby("Strategy")["Article_ID"].nunique().to_dict()

    order = ["Interior", "Exterior", "Mixto_interior_exterior", "NR"]
    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for key in order:
        k = int(counts.get(key, 0))
        pct = round(100.0 * float(k) / float(n), 1)

        if key == "Interior":
            crit = "Predominio de contextos indoor/residencial/sanitario/industrial sin componente exterior explicito."
            note_es = "Escenario dominante para instrumentacion controlada."
            crit_en = "Predominance of indoor/residential/healthcare/industrial contexts without explicit outdoor component."
            note_en = "Dominant scenario for controlled instrumentation."
            name_es = "Interior"
            name_en = "Indoor"
        elif key == "Exterior":
            crit = "Predominio de contextos outdoor/urban/rural/desert sin componente interior explicito."
            note_es = "Escenario de exposicion ambiental abierta."
            crit_en = "Predominance of outdoor/urban/rural/desert contexts without explicit indoor component."
            note_en = "Open-environment exposure scenario."
            name_es = "Exterior"
            name_en = "Outdoor"
        elif key == "Mixto_interior_exterior":
            crit = "Convivencia de contextos indoor y outdoor en el mismo estudio."
            note_es = "Patron mixto con necesidades de calibracion y operacion heterogeneas."
            crit_en = "Coexistence of indoor and outdoor contexts in the same study."
            note_en = "Mixed pattern with heterogeneous calibration and operation needs."
            name_es = "Mixto_interior_exterior"
            name_en = "Mixed_indoor_outdoor"
        else:
            crit = "Sin evidencia suficiente para clasificar contexto de despliegue."
            note_es = "NR en contexto de despliegue."
            crit_en = "Insufficient evidence to classify deployment context."
            note_en = "NR in deployment context."
            name_es = "NR"
            name_en = "NR"

        rows_es.append({
            "Contexto_despliegue": name_es,
            "Criterio_operativo": crit,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Deployment_context": name_en,
            "Operational_criterion": crit_en,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
        })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def build_decision6_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_hw = col_or_fallback(df, "D3_Hardware_and_sensors_norm", "D3_Hardware_and_sensors")

    base_tokens = {
        "PM_Sensor",
        "TempHumidity_Sensor",
        "CO_Sensor",
        "CO2_Sensor",
        "VOC_Sensor",
        "MCU_Arduino",
        "MCU_ESP32",
        "MCU_Generic",
        "SBC_RaspberryPi",
    }

    rows: list[dict[str, str]] = []
    for _, r in df[["Article_ID", col_hw]].iterrows():
        vals = set(parse_multi(r[col_hw], include_nr=False))
        has_base = bool(vals.intersection(base_tokens))
        has_special = bool(vals.difference(base_tokens))

        if has_base and has_special:
            strategy = "Mixta_base_especializada"
        elif has_base:
            strategy = "Base"
        elif has_special:
            strategy = "Especializada"
        else:
            strategy = "NR"

        rows.append({"Article_ID": str(r["Article_ID"]), "Strategy": strategy})

    st = pd.DataFrame(rows)
    counts = st.groupby("Strategy")["Article_ID"].nunique().to_dict()

    order = ["Base", "Especializada", "Mixta_base_especializada", "NR"]
    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for key in order:
        k = int(counts.get(key, 0))
        pct = round(100.0 * float(k) / float(n), 1)

        if key == "Base":
            crit = "Solo sensores/controladores base reportados en el estudio."
            note_es = "Perfil minimo viable de instrumentacion."
            crit_en = "Only baseline sensors/controllers reported in the study."
            note_en = "Minimum viable instrumentation profile."
            name_es = "Base"
            name_en = "Baseline"
        elif key == "Especializada":
            crit = "Solo componentes especializados (sin base explicita)."
            note_es = "Configuracion orientada a caso especifico."
            crit_en = "Only specialized components (without explicit baseline set)."
            note_en = "Configuration oriented to a specific use case."
            name_es = "Especializada"
            name_en = "Specialized"
        elif key == "Mixta_base_especializada":
            crit = "Convivencia de base de sensado y componentes especializados."
            note_es = "Patron dominante para ampliar cobertura funcional."
            crit_en = "Coexistence of baseline sensing and specialized components."
            note_en = "Dominant pattern to extend functional coverage."
            name_es = "Mixta_base_especializada"
            name_en = "Mixed_baseline_specialized"
        else:
            crit = "Sin evidencia suficiente para clasificar instrumentacion."
            note_es = "NR en hardware/sensores."
            crit_en = "Insufficient evidence to classify instrumentation."
            note_en = "NR in hardware/sensors."
            name_es = "NR"
            name_en = "NR"

        rows_es.append({
            "Configuracion_hardware": name_es,
            "Criterio_operativo": crit,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Hardware_configuration": name_en,
            "Operational_criterion": crit_en,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
        })

    return pd.DataFrame(rows_en if lang == "en" else rows_es)


def build_decision7_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    n = int(df["Article_ID"].nunique())
    col_rt = col_or_fallback(df, "D3_Real_time_characteristics_norm", "D3_Real_time_characteristics")

    latency_tokens = {"Temporal_Delay_Evaluated", "Clock_Synchronization"}
    continuous_tokens = {"Continuous_Loop"}
    interval_tokens = {"Interval_Sampling"}
    general_tokens = {
        "RealTime_Data_Collection",
        "Streaming_Upload",
        "RealTime_Data_Correction",
        "Route_Update_Event",
        "Threshold_Alerting",
    }

    # Jerarquia de evidencia (mas fuerte -> mas general).
    rows: list[dict[str, str]] = []
    for _, r in df[["Article_ID", col_rt]].iterrows():
        vals = set(parse_multi(r[col_rt], include_nr=False))

        if vals.intersection(latency_tokens):
            strategy = "Latencia_sincronizacion_explicita"
        elif vals.intersection(continuous_tokens):
            strategy = "Bucle_continuo"
        elif vals.intersection(interval_tokens):
            strategy = "Muestreo_por_intervalo"
        elif vals.intersection(general_tokens):
            strategy = "Declaracion_general_operativa"
        else:
            strategy = "NR"

        rows.append({"Article_ID": str(r["Article_ID"]), "Strategy": strategy})

    st = pd.DataFrame(rows)
    counts = st.groupby("Strategy")["Article_ID"].nunique().to_dict()

    order = [
        "Latencia_sincronizacion_explicita",
        "Bucle_continuo",
        "Muestreo_por_intervalo",
        "Declaracion_general_operativa",
        "NR",
    ]
    rows_es: list[dict[str, object]] = []
    rows_en: list[dict[str, object]] = []
    for key in order:
        k = int(counts.get(key, 0))
        pct = round(100.0 * float(k) / float(n), 1)

        if key == "Latencia_sincronizacion_explicita":
            crit = "Reporte explicito de latencia y/o sincronizacion temporal."
            note_es = "Mayor robustez de evidencia operativa en tiempo real."
            crit_en = "Explicit report of latency and/or temporal synchronization."
            note_en = "Highest robustness of real-time operational evidence."
            name_es = "Latencia_sincronizacion_explicita"
            name_en = "Explicit_latency_synchronization"
        elif key == "Bucle_continuo":
            crit = "Operacion continua reportada como ciclo de monitoreo."
            note_es = "Patron dominante de operacion en linea."
            crit_en = "Continuous operation reported as monitoring loop."
            note_en = "Dominant online operation pattern."
            name_es = "Bucle_continuo"
            name_en = "Continuous_loop"
        elif key == "Muestreo_por_intervalo":
            crit = "Operacion temporal por ventanas/intervalos de adquisicion."
            note_es = "Modo cuasi-tiempo real con cadencia definida."
            crit_en = "Temporal operation by acquisition windows/intervals."
            note_en = "Near-real-time mode with defined cadence."
            name_es = "Muestreo_por_intervalo"
            name_en = "Interval_sampling"
        elif key == "Declaracion_general_operativa":
            crit = "Solo evidencia general de operacion en tiempo real, sin metrica temporal explicita."
            note_es = "Soporte operativo util pero menos comparable."
            crit_en = "Only general real-time operation evidence, without explicit temporal metric."
            note_en = "Useful operational support but less comparable."
            name_es = "Declaracion_general_operativa"
            name_en = "General_operational_statement"
        else:
            crit = "Sin evidencia suficiente para clasificar operacion temporal."
            note_es = "NR en caracteristicas de tiempo real."
            crit_en = "Insufficient evidence to classify temporal operation."
            note_en = "NR in real-time characteristics."
            name_es = "NR"
            name_en = "NR"

        rows_es.append({
            "Evidencia_tiempo_real": name_es,
            "Criterio_operativo": crit,
            "k": k,
            "n": n,
            "%": pct,
            "Lectura_decision": note_es,
        })
        rows_en.append({
            "Real_time_evidence": name_en,
            "Operational_criterion": crit_en,
            "k": k,
            "n": n,
            "%": pct,
            "Decision_reading": note_en,
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
        t = build_decision1_table(df, lang=lang)

        csv_path = out_tab[lang] / f"d3_decision1_arquitectura_referencia_{lang}.csv"
        tex_path = out_tab[lang] / f"d3_decision1_arquitectura_referencia_{lang}.tex"
        t.to_csv(csv_path, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t,
                tex_path,
                "X[1.0,l,m] X[1.6,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[2.3,l,m]",
                "tab:d3_decision1_arquitectura_referencia",
                r"D3 -- Decision 1: arquitectura de referencia (agrupacion inferida de familias; k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t,
                tex_path,
                "X[1.0,l,m] X[1.6,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[2.3,l,m]",
                "tab:d3_decision1_architecture_reference",
                "D3 -- Decision 1: reference architecture (inferred family grouping; k/n/%; n=19).",
            )

        print(f"[OK] Decision 1 CSV: {csv_path}")
        print(f"[OK] Decision 1 TEX: {tex_path}")

        t2 = build_decision2_table(df, lang=lang)
        csv_path2 = out_tab[lang] / f"d3_decision2_estrategia_temporal_{lang}.csv"
        tex_path2 = out_tab[lang] / f"d3_decision2_estrategia_temporal_{lang}.tex"
        t2.to_csv(csv_path2, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t2,
                tex_path2,
                "X[1.0,l,m] X[1.6,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[2.3,l,m]",
                "tab:d3_decision2_estrategia_temporal",
                r"D3 -- Decision 2: estrategia temporal de procesamiento (agrupacion inferida; k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t2,
                tex_path2,
                "X[1.0,l,m] X[1.6,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[2.3,l,m]",
                "tab:d3_decision2_temporal_strategy",
                "D3 -- Decision 2: temporal processing strategy (inferred grouping; k/n/%; n=19).",
            )

        print(f"[OK] Decision 2 CSV: {csv_path2}")
        print(f"[OK] Decision 2 TEX: {tex_path2}")

        t3 = build_decision3_table(df, lang=lang, recurrent_threshold=3)
        csv_path3 = out_tab[lang] / f"d3_decision3_stack_comunicacion_{lang}.csv"
        tex_path3 = out_tab[lang] / f"d3_decision3_stack_comunicacion_{lang}.tex"
        t3.to_csv(csv_path3, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t3,
                tex_path3,
                "X[1.2,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[0.8,l,m] X[2.2,l,m]",
                "tab:d3_decision3_stack_comunicacion",
                r"D3 -- Decision 3: stack de comunicacion/plataforma (criterio recurrente: k>=3 estudios; k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t3,
                tex_path3,
                "X[1.2,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[0.8,l,m] X[2.2,l,m]",
                "tab:d3_decision3_communication_stack",
                "D3 -- Decision 3: communication/platform stack (recurrent criterion: k>=3 studies; k/n/%; n=19).",
            )

        print(f"[OK] Decision 3 CSV: {csv_path3}")
        print(f"[OK] Decision 3 TEX: {tex_path3}")

        t4 = build_decision4_table(df, lang=lang)
        csv_path4 = out_tab[lang] / f"d3_decision4_visualizacion_alertamiento_{lang}.csv"
        tex_path4 = out_tab[lang] / f"d3_decision4_visualizacion_alertamiento_{lang}.tex"
        t4.to_csv(csv_path4, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t4,
                tex_path4,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision4_visualizacion_alertamiento",
                r"D3 -- Decision 4: estrategia de visualizacion y alertamiento (k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t4,
                tex_path4,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision4_visualization_alerting",
                "D3 -- Decision 4: visualization and alerting strategy (k/n/%; n=19).",
            )

        print(f"[OK] Decision 4 CSV: {csv_path4}")
        print(f"[OK] Decision 4 TEX: {tex_path4}")

        t5 = build_decision5_table(df, lang=lang)
        csv_path5 = out_tab[lang] / f"d3_decision5_contexto_despliegue_{lang}.csv"
        tex_path5 = out_tab[lang] / f"d3_decision5_contexto_despliegue_{lang}.tex"
        t5.to_csv(csv_path5, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t5,
                tex_path5,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision5_contexto_despliegue",
                r"D3 -- Decision 5: contexto de despliegue (k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t5,
                tex_path5,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision5_deployment_context",
                "D3 -- Decision 5: deployment context (k/n/%; n=19).",
            )

        print(f"[OK] Decision 5 CSV: {csv_path5}")
        print(f"[OK] Decision 5 TEX: {tex_path5}")

        t6 = build_decision6_table(df, lang=lang)
        csv_path6 = out_tab[lang] / f"d3_decision6_instrumentacion_hardware_{lang}.csv"
        tex_path6 = out_tab[lang] / f"d3_decision6_instrumentacion_hardware_{lang}.tex"
        t6.to_csv(csv_path6, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t6,
                tex_path6,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision6_instrumentacion_hardware",
                r"D3 -- Decision 6: instrumentacion y hardware (k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t6,
                tex_path6,
                "X[1.0,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.8,l,m]",
                "tab:d3_decision6_instrumentation_hardware",
                "D3 -- Decision 6: instrumentation and hardware (k/n/%; n=19).",
            )

        print(f"[OK] Decision 6 CSV: {csv_path6}")
        print(f"[OK] Decision 6 TEX: {tex_path6}")

        t7 = build_decision7_table(df, lang=lang)
        csv_path7 = out_tab[lang] / f"d3_decision7_evidencia_tiempo_real_{lang}.csv"
        tex_path7 = out_tab[lang] / f"d3_decision7_evidencia_tiempo_real_{lang}.tex"
        t7.to_csv(csv_path7, index=False, encoding="utf-8-sig")

        if lang == "es":
            write_longtblr(
                t7,
                tex_path7,
                "X[1.1,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.7,l,m]",
                "tab:d3_decision7_evidencia_tiempo_real",
                r"D3 -- Decision 7: evidencia operativa de tiempo real (jerarquia de evidencia; k/n/\%; n=19). Elaboracion propia.",
            )
        else:
            write_longtblr(
                t7,
                tex_path7,
                "X[1.1,l,m] X[2.0,l,m] X[0.45,c,m] X[0.45,c,m] X[0.55,c,m] X[1.7,l,m]",
                "tab:d3_decision7_real_time_evidence",
                "D3 -- Decision 7: real-time operational evidence (evidence hierarchy; k/n/%; n=19).",
            )

        print(f"[OK] Decision 7 CSV: {csv_path7}")
        print(f"[OK] Decision 7 TEX: {tex_path7}")


if __name__ == "__main__":
    main()
