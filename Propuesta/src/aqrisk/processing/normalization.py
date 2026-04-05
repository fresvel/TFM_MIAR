from __future__ import annotations

from aqrisk.domain.models import InputSnapshot, ParameterSeries


PARAMETER_ALIASES = {
    "pm25": "pm25",
    "pm2.5": "pm25",
    "pm10": "pm10",
    "temperature": "temperature",
    "humidity": "humidity",
    "relativehumidity": "humidity",
    "no2": "no2",
    "o3": "o3",
    "co": "co",
    "so2": "so2",
}


def normalize_parameter_name(name: str) -> str:
    key = name.replace("_", "").replace("-", "").replace(" ", "").lower()
    return PARAMETER_ALIASES.get(key, name.lower())


def normalize_snapshot(snapshot: InputSnapshot) -> InputSnapshot:
    normalized_series: dict[str, ParameterSeries] = {}
    for _, series in snapshot.series.items():
        parameter = normalize_parameter_name(series.parameter)
        normalized_series[parameter] = ParameterSeries(
            parameter=parameter,
            unit=series.unit,
            observations=series.observations,
        )
    snapshot.series = normalized_series
    return snapshot
