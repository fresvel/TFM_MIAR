from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    scenario_id: str
    name: str
    description: str
    values: dict[str, list[float]]


SCENARIOS: dict[str, ScenarioDefinition] = {
    "urban_escalation": ScenarioDefinition(
        scenario_id="urban_escalation",
        name="Urban Escalation",
        description="Escenario con incremento progresivo de PM2.5 y O3, con ajuste contextual activo al final.",
        values={
            "pm25": [18.0] * 8 + [24.0] * 8 + [42.0] * 8,
            "pm10": [35.0] * 8 + [52.0] * 8 + [82.0] * 8,
            "co": [0.6] * 8 + [0.8] * 8 + [1.1] * 8,
            "no2": [0.018] * 24,
            "o3": [0.042] * 8 + [0.058] * 8 + [0.074] * 8,
            "so2": [0.004] * 24,
            "temperature": [28.0] * 16 + [31.0] * 8,
            "humidity": [55.0] * 16 + [76.0] * 8,
        },
    ),
    "particulate_pressure": ScenarioDefinition(
        scenario_id="particulate_pressure",
        name="Particulate Pressure",
        description="Escenario dominado por presión particulada sostenida con cobertura completa y sin escalado contextual.",
        values={
            "pm25": [28.0] * 8 + [38.0] * 8 + [58.0] * 8,
            "pm10": [54.0] * 12 + [96.0] * 12,
            "co": [0.5] * 24,
            "no2": [0.014] * 24,
            "o3": [0.032] * 24,
            "so2": [0.003] * 24,
            "temperature": [24.0] * 24,
            "humidity": [58.0] * 24,
        },
    ),
    "moderate_multicontaminant": ScenarioDefinition(
        scenario_id="moderate_multicontaminant",
        name="Moderate Multi-Contaminant",
        description="Escenario con varios contaminantes cercanos al dominante para probar concurrencia alta sin episodio extremo.",
        values={
            "pm25": [20.0] * 24,
            "pm10": [46.0] * 24,
            "co": [4.6] * 24,
            "no2": [0.052] * 24,
            "o3": [0.061] * 24,
            "so2": [0.006] * 24,
            "temperature": [26.0] * 24,
            "humidity": [61.0] * 24,
        },
    ),
}


def list_scenarios() -> list[dict[str, str]]:
    return [
        {
            "scenario_id": item.scenario_id,
            "name": item.name,
            "description": item.description,
        }
        for item in SCENARIOS.values()
    ]


def get_scenario(scenario_id: str) -> ScenarioDefinition:
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {scenario_id}") from exc
