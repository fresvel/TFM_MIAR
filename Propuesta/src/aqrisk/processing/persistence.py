from __future__ import annotations

from statistics import mean

from aqrisk.domain.models import ParameterSeries


def compute_persistence_score(aqi_history: list[int]) -> float:
    if not aqi_history:
        return 0.0
    window_mean = mean(aqi_history)
    exceedances = sum(1 for value in aqi_history if value >= 100)
    persistence = min(100.0, (window_mean / 3.0) + (exceedances * 15.0))
    return round(persistence, 2)


def series_latest_value(series: ParameterSeries) -> float | None:
    if not series.observations:
        return None
    return series.observations[-1].value
