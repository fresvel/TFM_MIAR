from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SensorDescriptor:
    sensor_id: int
    parameter: str
    units: str


@dataclass(slots=True)
class HourlyObservation:
    sensor_id: int
    parameter: str
    value: float
    unit: str
    datetime_from: datetime
    datetime_to: datetime
    coverage: float | None = None


@dataclass(slots=True)
class ParameterSeries:
    parameter: str
    unit: str
    observations: list[HourlyObservation]


@dataclass(slots=True)
class InputSnapshot:
    source: str
    location_id: int | None
    location_name: str
    generated_at: datetime
    series: dict[str, ParameterSeries]
    coverage_global: float


@dataclass(slots=True)
class AQIResult:
    subindices: dict[str, int]
    global_aqi: int | None
    dominant_parameter: str | None
    category: str
    supported_parameters: list[str] = field(default_factory=list)
    unsupported_parameters: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FuzzyResult:
    score: float
    label: str
    triggered_rules: list[str]


@dataclass(slots=True)
class Alert:
    title: str
    message: str
    caution: str | None


@dataclass(slots=True)
class ModuleResult:
    snapshot: InputSnapshot
    aqi: AQIResult
    concurrence_score: float
    persistence_score: float
    fuzzy: FuzzyResult
    context_adjustments: list[str]
    alert: Alert

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["snapshot"]["generated_at"] = self.snapshot.generated_at.isoformat()
        for series in payload["snapshot"]["series"].values():
            for observation in series["observations"]:
                observation["datetime_from"] = observation["datetime_from"].isoformat()
                observation["datetime_to"] = observation["datetime_to"].isoformat()
        return payload
