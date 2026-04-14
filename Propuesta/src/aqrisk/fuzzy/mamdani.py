from __future__ import annotations

from dataclasses import dataclass

from aqrisk.fuzzy.constants import (
    AGGREGATION_SAMPLE_STEP,
    AQI_TERMS,
    CONCURRENCE_TERMS,
    INPUT_CURVE_STEP,
    INPUT_RANGE_END,
    INPUT_RANGE_START,
    PERSISTENCE_TERMS,
    RISK_OUTPUT_RANGE,
    RISK_OUTPUT_STEP,
    RISK_RULE_MATRIX,
)
from aqrisk.fuzzy.membership import trapezoidal, triangular


AQI_LABEL_LIMITS = (
    (50, "good"),
    (100, "moderate"),
    (150, "unhealthy_sensitive_groups"),
    (200, "unhealthy"),
    (300, "very_unhealthy"),
)


class MembershipCurveFactory:
    """Creates fuzzy memberships and public curve sets for the engine."""

    def aqi(self, value: float) -> dict[str, float]:
        """Return AQI memberships for a scalar value."""
        return {
            "good": trapezoidal(value, 0, 0, 30, 60),
            "moderate": triangular(value, 40, 75, 110),
            "unhealthy_sensitive_groups": triangular(value, 90, 125, 160),
            "unhealthy": triangular(value, 140, 175, 210),
            "very_unhealthy": triangular(value, 190, 250, 320),
            "hazardous": trapezoidal(value, 280, 350, 500, 500),
        }

    def concurrence(self, value: float) -> dict[str, float]:
        """Return concurrence memberships for a scalar value."""
        return {
            "low": trapezoidal(value, 0, 0, 25, 45),
            "medium": triangular(value, 35, 55, 75),
            "high": trapezoidal(value, 65, 80, 100, 100),
        }

    def persistence(self, value: float) -> dict[str, float]:
        """Return persistence memberships for a scalar value."""
        return {
            "low": trapezoidal(value, 0, 0, 20, 40),
            "medium": triangular(value, 30, 55, 75),
            "high": trapezoidal(value, 65, 80, 100, 100),
        }

    def risk(self, term: str, value: float) -> float:
        """Return the risk membership value for one output term."""
        shapes = {
            "good": lambda candidate: trapezoidal(candidate, 0, 0, 30, 60),
            "moderate": lambda candidate: triangular(candidate, 40, 75, 110),
            "unhealthy_sensitive_groups": lambda candidate: triangular(candidate, 90, 125, 160),
            "unhealthy": lambda candidate: triangular(candidate, 140, 175, 210),
            "very_unhealthy": lambda candidate: triangular(candidate, 190, 250, 320),
            "hazardous": lambda candidate: trapezoidal(candidate, 280, 350, 500, 500),
        }
        return shapes[term](value)

    def curve_set(self, kind: str) -> dict[str, list[dict[str, float]]]:
        """Return curve samples for frontend explainability payloads."""
        builders = {
            "aqi": self.aqi,
            "persistence": self.persistence,
            "concurrence": self.concurrence,
        }

        if kind not in builders:
            if kind != "risk":
                raise ValueError(f"Unknown membership kind: {kind}")
            risk_start, risk_end = RISK_OUTPUT_RANGE
            return {
                term: [
                    {"x": float(point), "membership": round(self.risk(term, point), 4)}
                    for point in range(risk_start, risk_end + 1, AGGREGATION_SAMPLE_STEP)
                ]
                for term in AQI_TERMS
            }

        builder = builders[kind]
        if kind == "aqi":
            domain = range(RISK_OUTPUT_RANGE[0], RISK_OUTPUT_RANGE[1] + 1, AGGREGATION_SAMPLE_STEP)
        else:
            domain = range(INPUT_RANGE_START, INPUT_RANGE_END + 1, INPUT_CURVE_STEP)
        curves: dict[str, list[dict[str, float]]] = {}
        for point in domain:
            memberships = builder(float(point))
            for term, membership in memberships.items():
                curves.setdefault(term, []).append({"x": float(point), "membership": round(membership, 4)})
        return curves


@dataclass(slots=True)
class RuleResult:
    """Represents a single fuzzy rule evaluation."""

    name: str
    aqi_term: str
    concurrence_term: str
    persistence_term: str
    output_term: str
    strength: float


class MamdaniRiskEngine:
    """Evaluates the main fuzzy rule base and exposes explainability traces."""

    def __init__(self, curve_factory: MembershipCurveFactory | None = None) -> None:
        """Initialize the engine with a membership factory."""
        self.curve_factory = curve_factory or MembershipCurveFactory()
        self.rule_count = len(AQI_TERMS) * len(CONCURRENCE_TERMS) * len(PERSISTENCE_TERMS)

    def trace(
        self,
        aqi_value: int | None,
        persistence_score: float,
        concurrence_score: float,
    ) -> dict[str, object]:
        """Return a full explainability trace for a fuzzy evaluation."""
        aqi = float(aqi_value or 0)
        memberships = {
            "aqi": self.curve_factory.aqi(aqi),
            "persistence": self.curve_factory.persistence(persistence_score),
            "concurrence": self.curve_factory.concurrence(concurrence_score),
        }
        rules = self._evaluate_rules(memberships)
        score = self._defuzzify(rules)
        label = self._label(score)
        triggered = [rule.name for rule in rules if rule.strength > 0]
        return {
            "inputs": {
                "aqi": aqi,
                "persistence": persistence_score,
                "concurrence": concurrence_score,
            },
            "memberships": memberships,
            "rules": [
                {
                    "name": rule.name,
                    "aqi_term": rule.aqi_term,
                    "concurrence_term": rule.concurrence_term,
                    "persistence_term": rule.persistence_term,
                    "output_term": rule.output_term,
                    "strength": round(rule.strength, 4),
                }
                for rule in rules
                if rule.strength > 0
            ],
            "aggregation_samples": self._aggregation_samples(rules),
            "score": round(score, 2),
            "label": label,
            "triggered_rules": triggered,
        }

    def evaluate(
        self,
        aqi_value: int | None,
        persistence_score: float,
        concurrence_score: float,
    ) -> tuple[float, str, list[str]]:
        """Return score, label and triggered rule names for one evaluation."""
        trace = self.trace(aqi_value, persistence_score, concurrence_score)
        return trace["score"], trace["label"], trace["triggered_rules"]

    def _evaluate_rules(self, memberships: dict[str, dict[str, float]]) -> list[RuleResult]:
        """Evaluate the full rule matrix for the active memberships."""
        rules: list[RuleResult] = []
        for aqi_term in AQI_TERMS:
            for concurrence_term in CONCURRENCE_TERMS:
                for persistence_term in PERSISTENCE_TERMS:
                    output_term = RISK_RULE_MATRIX[aqi_term][concurrence_term][persistence_term]
                    strength = min(
                        memberships["aqi"][aqi_term],
                        memberships["concurrence"][concurrence_term],
                        memberships["persistence"][persistence_term],
                    )
                    rules.append(
                        RuleResult(
                            name=f"R_{aqi_term}_{concurrence_term}_{persistence_term}",
                            aqi_term=aqi_term,
                            concurrence_term=concurrence_term,
                            persistence_term=persistence_term,
                            output_term=output_term,
                            strength=strength,
                        )
                    )
        return rules

    def _defuzzify(self, rules: list[RuleResult]) -> float:
        """Compute the centroid of the aggregated clipped output set."""
        numerator = 0.0
        denominator = 0.0
        risk_start, risk_end = RISK_OUTPUT_RANGE
        for point in range(risk_start, risk_end + 1, RISK_OUTPUT_STEP):
            aggregate = 0.0
            for rule in rules:
                clipped = min(rule.strength, self.curve_factory.risk(rule.output_term, point))
                aggregate = max(aggregate, clipped)
            numerator += point * aggregate
            denominator += aggregate
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _label(self, score: float) -> str:
        """Translate the continuous score back into a public risk label."""
        for limit, label in AQI_LABEL_LIMITS:
            if score <= limit:
                return label
        return "hazardous"

    def _aggregation_samples(self, rules: list[RuleResult]) -> list[dict[str, float]]:
        """Sample the aggregated output curve for explainability charts."""
        samples: list[dict[str, float]] = []
        risk_start, risk_end = RISK_OUTPUT_RANGE
        for point in range(risk_start, risk_end + 1, AGGREGATION_SAMPLE_STEP):
            aggregate = 0.0
            for rule in rules:
                clipped = min(rule.strength, self.curve_factory.risk(rule.output_term, point))
                aggregate = max(aggregate, clipped)
            samples.append({"x": float(point), "membership": round(aggregate, 4)})
        return samples
