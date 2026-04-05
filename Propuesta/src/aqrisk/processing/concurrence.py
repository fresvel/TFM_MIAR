from __future__ import annotations


def compute_concurrence_score(subindices: dict[str, int], global_aqi: int | None) -> float:
    if not subindices or global_aqi is None or global_aqi <= 0:
        return 15.0

    threshold = max(25, int(global_aqi * 0.8))
    near_dominant = [value for value in subindices.values() if value >= threshold]
    count = len(near_dominant)

    if count <= 1:
        return 20.0
    if count == 2:
        return 55.0
    return 85.0
