from __future__ import annotations

from dataclasses import dataclass

from aqrisk.fuzzy.membership import trapezoidal, triangular


AQI_TERMS = [
    "good",
    "moderate",
    "unhealthy_sensitive_groups",
    "unhealthy",
    "very_unhealthy",
    "hazardous",
]
CONCURRENCE_TERMS = ["low", "medium", "high"]
PERSISTENCE_TERMS = ["low", "medium", "high"]

RULE_MATRIX: dict[str, dict[str, dict[str, str]]] = {
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


def _aqi_memberships(value: float) -> dict[str, float]:
    return {
        "good": trapezoidal(value, 0, 0, 30, 60),
        "moderate": triangular(value, 40, 75, 110),
        "unhealthy_sensitive_groups": triangular(value, 90, 125, 160),
        "unhealthy": triangular(value, 140, 175, 210),
        "very_unhealthy": triangular(value, 190, 250, 320),
        "hazardous": trapezoidal(value, 280, 350, 500, 500),
    }


def _concurrence_memberships(value: float) -> dict[str, float]:
    return {
        "low": trapezoidal(value, 0, 0, 25, 45),
        "medium": triangular(value, 35, 55, 75),
        "high": trapezoidal(value, 65, 80, 100, 100),
    }


def _persistence_memberships(value: float) -> dict[str, float]:
    return {
        "low": trapezoidal(value, 0, 0, 20, 40),
        "medium": triangular(value, 30, 55, 75),
        "high": trapezoidal(value, 65, 80, 100, 100),
    }


def _risk_membership(term: str, x: float) -> float:
    shapes = {
        "good": lambda v: trapezoidal(v, 0, 0, 30, 60),
        "moderate": lambda v: triangular(v, 40, 75, 110),
        "unhealthy_sensitive_groups": lambda v: triangular(v, 90, 125, 160),
        "unhealthy": lambda v: triangular(v, 140, 175, 210),
        "very_unhealthy": lambda v: triangular(v, 190, 250, 320),
        "hazardous": lambda v: trapezoidal(v, 280, 350, 500, 500),
    }
    return shapes[term](x)


@dataclass(slots=True)
class RuleResult:
    name: str
    aqi_term: str
    concurrence_term: str
    persistence_term: str
    output_term: str
    strength: float


class MamdaniRiskEngine:
    def trace(
        self,
        aqi_value: int | None,
        persistence_score: float,
        concurrence_score: float,
    ) -> dict[str, object]:
        aqi = float(aqi_value or 0)
        memberships = {
            "aqi": _aqi_memberships(aqi),
            "persistence": _persistence_memberships(persistence_score),
            "concurrence": _concurrence_memberships(concurrence_score),
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
        trace = self.trace(aqi_value, persistence_score, concurrence_score)
        return trace["score"], trace["label"], trace["triggered_rules"]

    def _evaluate_rules(self, memberships: dict[str, dict[str, float]]) -> list[RuleResult]:
        rules: list[RuleResult] = []
        for aqi_term in AQI_TERMS:
            for concurrence_term in CONCURRENCE_TERMS:
                for persistence_term in PERSISTENCE_TERMS:
                    output_term = RULE_MATRIX[aqi_term][concurrence_term][persistence_term]
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
        numerator = 0.0
        denominator = 0.0
        for point in range(0, 501):
            aggregate = 0.0
            for rule in rules:
                clipped = min(rule.strength, _risk_membership(rule.output_term, point))
                aggregate = max(aggregate, clipped)
            numerator += point * aggregate
            denominator += aggregate
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _label(self, score: float) -> str:
        if score <= 50:
            return "good"
        if score <= 100:
            return "moderate"
        if score <= 150:
            return "unhealthy_sensitive_groups"
        if score <= 200:
            return "unhealthy"
        if score <= 300:
            return "very_unhealthy"
        return "hazardous"

    def _aggregation_samples(self, rules: list[RuleResult]) -> list[dict[str, float]]:
        samples: list[dict[str, float]] = []
        for point in range(0, 501, 10):
            aggregate = 0.0
            for rule in rules:
                clipped = min(rule.strength, _risk_membership(rule.output_term, point))
                aggregate = max(aggregate, clipped)
            samples.append({"x": float(point), "membership": round(aggregate, 4)})
        return samples


def membership_curve_set(kind: str) -> dict[str, list[dict[str, float]]]:
    builders = {
        "aqi": _aqi_memberships,
        "persistence": _persistence_memberships,
        "concurrence": _concurrence_memberships,
    }
    if kind not in builders:
        if kind != "risk":
            raise ValueError(f"Unknown membership kind: {kind}")
        return {
            term: [{"x": float(point), "membership": round(_risk_membership(term, point), 4)} for point in range(0, 501, 10)]
            for term in AQI_TERMS
        }

    builder = builders[kind]
    if kind == "aqi":
        domain = range(0, 501, 10)
    else:
        domain = range(0, 101, 5)
    curves: dict[str, list[dict[str, float]]] = {}
    for point in domain:
        memberships = builder(float(point))
        for term, value in memberships.items():
            curves.setdefault(term, []).append({"x": float(point), "membership": round(value, 4)})
    return curves
