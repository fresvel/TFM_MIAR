from __future__ import annotations

from aqrisk.domain.models import AQIResult, InputSnapshot


EPA_LABELS = [
    "good",
    "moderate",
    "unhealthy_sensitive_groups",
    "unhealthy",
    "very_unhealthy",
    "hazardous",
]

TEMPERATURE_TERMS = ["low", "normal", "high"]
HUMIDITY_TERMS = ["low", "medium", "high"]

CONTEXT_RULE_MATRIX: dict[str, dict[str, int]] = {
    "low": {
        "low": 0,
        "medium": 0,
        "high": 0,
    },
    "normal": {
        "low": 0,
        "medium": 0,
        "high": 1,
    },
    "high": {
        "low": 0,
        "medium": 1,
        "high": 1,
    },
}


def latest_parameter_value(snapshot: InputSnapshot, parameter: str) -> float | None:
    series = snapshot.series.get(parameter)
    if not series or not series.observations:
        return None
    return series.observations[-1].value


def apply_context_adjustment(
    label: str,
    score: float,
    snapshot: InputSnapshot,
    aqi: AQIResult,
) -> tuple[float, str, list[str]]:
    temperature = latest_parameter_value(snapshot, "temperature")
    humidity = latest_parameter_value(snapshot, "humidity")

    if temperature is None or humidity is None:
        return score, label, []

    temperature_term = classify_temperature(temperature)
    humidity_term = classify_humidity(humidity)
    escalation = CONTEXT_RULE_MATRIX[temperature_term][humidity_term]
    adjustments = [f"CTX_{temperature_term}_{humidity_term}"] if escalation > 0 else []

    if escalation == 0:
        return score, label, adjustments

    particulate_index = max(aqi.subindices.get("pm25", 0), aqi.subindices.get("pm10", 0))
    if particulate_index < 100 and aqi.global_aqi is not None and aqi.global_aqi < 101:
        return score, label, []

    base_index = EPA_LABELS.index(label)
    adjusted_index = min(base_index + escalation, len(EPA_LABELS) - 1)
    adjusted_label = EPA_LABELS[adjusted_index]
    adjusted_score = _category_midpoint(adjusted_label)
    return adjusted_score, adjusted_label, adjustments


def classify_temperature(value: float) -> str:
    if value <= 10:
        return "low"
    if value < 30:
        return "normal"
    return "high"


def classify_humidity(value: float) -> str:
    if value < 40:
        return "low"
    if value < 70:
        return "medium"
    return "high"


def _category_midpoint(label: str) -> float:
    midpoints = {
        "good": 25.0,
        "moderate": 75.0,
        "unhealthy_sensitive_groups": 125.0,
        "unhealthy": 175.0,
        "very_unhealthy": 250.0,
        "hazardous": 350.0,
    }
    return midpoints[label]
