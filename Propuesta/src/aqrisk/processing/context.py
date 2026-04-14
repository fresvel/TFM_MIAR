from __future__ import annotations

from aqrisk.domain.models import AQIResult, InputSnapshot


EPA_LABELS = (
    "good",
    "moderate",
    "unhealthy_sensitive_groups",
    "unhealthy",
    "very_unhealthy",
    "hazardous",
)

TEMPERATURE_TERMS = ("low", "normal", "high")
HUMIDITY_TERMS = ("low", "medium", "high")

CONTEXT_RULE_MATRIX: dict[str, dict[str, int]] = {
    "low": {"low": 0, "medium": 0, "high": 0},
    "normal": {"low": 0, "medium": 0, "high": 1},
    "high": {"low": 0, "medium": 1, "high": 1},
}

TEMPERATURE_LOW_MAX = 10
TEMPERATURE_NORMAL_MAX_EXCLUSIVE = 30
HUMIDITY_LOW_MAX_EXCLUSIVE = 40
HUMIDITY_MEDIUM_MAX_EXCLUSIVE = 70
PARTICULATE_GATE_THRESHOLD = 100
AQI_GATE_THRESHOLD = 101

CATEGORY_SCORE_MIDPOINTS = {
    "good": 25.0,
    "moderate": 75.0,
    "unhealthy_sensitive_groups": 125.0,
    "unhealthy": 175.0,
    "very_unhealthy": 250.0,
    "hazardous": 350.0,
}


class ContextualRiskAdjuster:
    """Applies the contextual risk modulation layer and exposes its trace."""

    def __init__(self) -> None:
        """Initialize the contextual adjuster."""
        self.rule_count = len(TEMPERATURE_TERMS) * len(HUMIDITY_TERMS)

    @staticmethod
    def latest_parameter_value(snapshot: InputSnapshot, parameter: str) -> float | None:
        """Return the latest value for a contextual parameter."""
        series = snapshot.series.get(parameter)
        if not series or not series.observations:
            return None
        return series.observations[-1].value

    @staticmethod
    def classify_temperature(value: float) -> str:
        """Map temperature into contextual linguistic terms."""
        if value <= TEMPERATURE_LOW_MAX:
            return "low"
        if value < TEMPERATURE_NORMAL_MAX_EXCLUSIVE:
            return "normal"
        return "high"

    @staticmethod
    def classify_humidity(value: float) -> str:
        """Map humidity into contextual linguistic terms."""
        if value < HUMIDITY_LOW_MAX_EXCLUSIVE:
            return "low"
        if value < HUMIDITY_MEDIUM_MAX_EXCLUSIVE:
            return "medium"
        return "high"

    @staticmethod
    def category_midpoint(label: str) -> float:
        """Return the representative AQI midpoint for a category label."""
        return CATEGORY_SCORE_MIDPOINTS[label]

    def apply(
        self,
        label: str,
        score: float,
        snapshot: InputSnapshot,
        aqi: AQIResult,
    ) -> tuple[float, str, list[str]]:
        """Apply contextual modulation to the principal fuzzy output."""
        temperature = self.latest_parameter_value(snapshot, "temperature")
        humidity = self.latest_parameter_value(snapshot, "humidity")

        if temperature is None or humidity is None:
            return score, label, []

        temperature_term = self.classify_temperature(temperature)
        humidity_term = self.classify_humidity(humidity)
        escalation = CONTEXT_RULE_MATRIX[temperature_term][humidity_term]
        adjustments = [f"CTX_{temperature_term}_{humidity_term}"] if escalation > 0 else []

        if escalation == 0:
            return score, label, adjustments

        particulate_index = max(aqi.subindices.get("pm25", 0), aqi.subindices.get("pm10", 0))
        if particulate_index < PARTICULATE_GATE_THRESHOLD and aqi.global_aqi is not None and aqi.global_aqi < AQI_GATE_THRESHOLD:
            return score, label, []

        base_index = EPA_LABELS.index(label)
        adjusted_index = min(base_index + escalation, len(EPA_LABELS) - 1)
        adjusted_label = EPA_LABELS[adjusted_index]
        adjusted_score = self.category_midpoint(adjusted_label)
        return adjusted_score, adjusted_label, adjustments

    def build_context_trace(
        self,
        result: dict[str, object],
        principal_trace: dict[str, object],
    ) -> dict[str, object]:
        """Build the explainability payload for the contextual layer."""
        temperature = self._latest_result_value(result, "temperature")
        humidity = self._latest_result_value(result, "humidity")
        payload: dict[str, object] = {
            "adjustments": result["context_adjustments"],
            "temperature": temperature,
            "humidity": humidity,
            "temperature_term": None,
            "humidity_term": None,
            "rule": None,
            "escalation": 0,
            "applied": False,
            "reason": "sin_datos_contextuales",
        }

        if temperature is None or humidity is None:
            return payload

        temperature_term = self.classify_temperature(float(temperature))
        humidity_term = self.classify_humidity(float(humidity))
        escalation = CONTEXT_RULE_MATRIX[temperature_term][humidity_term]
        particulate_index = max(
            result.get("aqi", {}).get("subindices", {}).get("pm25", 0),
            result.get("aqi", {}).get("subindices", {}).get("pm10", 0),
        )
        global_aqi = result.get("aqi", {}).get("global_aqi")
        blocked_by_particulate_gate = (
            escalation > 0
            and particulate_index < PARTICULATE_GATE_THRESHOLD
            and global_aqi is not None
            and global_aqi < AQI_GATE_THRESHOLD
        )

        payload.update(
            {
                "temperature_term": temperature_term,
                "humidity_term": humidity_term,
                "rule": f"CTX_{temperature_term}_{humidity_term}",
                "escalation": escalation,
                "particulate_index": particulate_index,
                "principal_score": principal_trace["score"],
                "principal_label": principal_trace["label"],
                "final_score": result["fuzzy"]["score"],
                "final_label": result["fuzzy"]["label"],
            }
        )

        if escalation == 0:
            payload["reason"] = "regla_contextual_sin_escalado"
            return payload
        if blocked_by_particulate_gate:
            payload["reason"] = "escalado_bloqueado_por_umbral_particulado"
            return payload

        payload["applied"] = True
        payload["reason"] = "escalado_contextual_aplicado"
        return payload

    @staticmethod
    def _latest_result_value(result: dict[str, object], parameter: str) -> float | None:
        """Return the latest contextual value from a serialized module result."""
        series = result.get("snapshot", {}).get("series", {}).get(parameter)
        if not series:
            return None
        observations = series.get("observations", [])
        if not observations:
            return None
        return observations[-1].get("value")
