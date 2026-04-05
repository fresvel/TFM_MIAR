from __future__ import annotations

from statistics import mean

from aqrisk.domain.models import ParameterSeries


def compute_global_coverage(series_map: dict[str, ParameterSeries]) -> float:
    coverages: list[float] = []
    for series in series_map.values():
        for observation in series.observations:
            if observation.coverage is not None:
                coverages.append(observation.coverage)
    if not coverages:
        return 0.0
    return round(mean(coverages), 2)
