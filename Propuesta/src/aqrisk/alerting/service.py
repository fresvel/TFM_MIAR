from __future__ import annotations

from aqrisk.domain.models import Alert, AQIResult, FuzzyResult


LABEL_TEXT = {
    "good": "Good",
    "moderate": "Moderate",
    "unhealthy_sensitive_groups": "Unhealthy for Sensitive Groups",
    "unhealthy": "Unhealthy",
    "very_unhealthy": "Very Unhealthy",
    "hazardous": "Hazardous",
}


def build_alert(
    aqi: AQIResult,
    fuzzy: FuzzyResult,
    coverage: float,
    min_coverage: float,
) -> Alert:
    caution = None
    if coverage < min_coverage:
        caution = (
            f"Cobertura de datos inferior al umbral recomendado ({min_coverage:.0f}%)."
        )
    dominant = aqi.dominant_parameter or "sin contaminante dominante"
    title = f"{LABEL_TEXT.get(fuzzy.label, fuzzy.label)} | AQI {aqi.global_aqi if aqi.global_aqi is not None else 'NA'}"
    message = (
        f"Estado base {LABEL_TEXT.get(aqi.category, aqi.category)}. "
        f"Contaminante dominante: {dominant}. "
        f"Riesgo estimado: {LABEL_TEXT.get(fuzzy.label, fuzzy.label)}. "
        f"Reglas activadas: {', '.join(fuzzy.triggered_rules) if fuzzy.triggered_rules else 'ninguna'}."
    )
    return Alert(title=title, message=message, caution=caution)
