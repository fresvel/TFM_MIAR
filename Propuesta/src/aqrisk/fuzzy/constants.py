from __future__ import annotations


AQI_TERMS = (
    "good",
    "moderate",
    "unhealthy_sensitive_groups",
    "unhealthy",
    "very_unhealthy",
    "hazardous",
)
CONCURRENCE_TERMS = ("low", "medium", "high")
PERSISTENCE_TERMS = ("low", "medium", "high")

RISK_OUTPUT_RANGE = (0, 500)
RISK_OUTPUT_STEP = 1
AGGREGATION_SAMPLE_STEP = 10
INPUT_RANGE_START = 0
INPUT_RANGE_END = 100
INPUT_CURVE_STEP = 5

RISK_RULE_MATRIX: dict[str, dict[str, dict[str, str]]] = {
    "good": {
        "low": {"low": "good", "medium": "good", "high": "moderate"},
        "medium": {"low": "good", "medium": "moderate", "high": "moderate"},
        "high": {"low": "moderate", "medium": "moderate", "high": "unhealthy_sensitive_groups"},
    },
    "moderate": {
        "low": {"low": "moderate", "medium": "moderate", "high": "unhealthy_sensitive_groups"},
        "medium": {"low": "moderate", "medium": "unhealthy_sensitive_groups", "high": "unhealthy_sensitive_groups"},
        "high": {"low": "unhealthy_sensitive_groups", "medium": "unhealthy_sensitive_groups", "high": "unhealthy"},
    },
    "unhealthy_sensitive_groups": {
        "low": {"low": "unhealthy_sensitive_groups", "medium": "unhealthy_sensitive_groups", "high": "unhealthy"},
        "medium": {"low": "unhealthy_sensitive_groups", "medium": "unhealthy", "high": "unhealthy"},
        "high": {"low": "unhealthy", "medium": "unhealthy", "high": "very_unhealthy"},
    },
    "unhealthy": {
        "low": {"low": "unhealthy", "medium": "unhealthy", "high": "very_unhealthy"},
        "medium": {"low": "unhealthy", "medium": "very_unhealthy", "high": "very_unhealthy"},
        "high": {"low": "very_unhealthy", "medium": "very_unhealthy", "high": "hazardous"},
    },
    "very_unhealthy": {
        "low": {"low": "very_unhealthy", "medium": "very_unhealthy", "high": "hazardous"},
        "medium": {"low": "very_unhealthy", "medium": "hazardous", "high": "hazardous"},
        "high": {"low": "hazardous", "medium": "hazardous", "high": "hazardous"},
    },
    "hazardous": {
        "low": {"low": "hazardous", "medium": "hazardous", "high": "hazardous"},
        "medium": {"low": "hazardous", "medium": "hazardous", "high": "hazardous"},
        "high": {"low": "hazardous", "medium": "hazardous", "high": "hazardous"},
    },
}
