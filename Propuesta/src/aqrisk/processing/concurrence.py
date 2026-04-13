from __future__ import annotations


def compute_concurrence_score(subindices: dict[str, int], global_aqi: int | None) -> float:
    if not subindices or global_aqi is None or global_aqi <= 0:
        return 15.0

    dominant = float(max(subindices.values()))
    threshold = max(25.0, dominant * 0.8)
    denominator = dominant - threshold
    remaining = sorted((float(value) for value in subindices.values()), reverse=True)

    # Exclude one dominant contributor so the score reflects additional pollutants.
    remaining.pop(0)

    if denominator <= 0 or not remaining:
        return 0.0

    effective_companions = 0.0
    for value in remaining:
        closeness = max(0.0, min(1.0, (value - threshold) / denominator))
        effective_companions += closeness

    # The fuzzy engine only distinguishes low/medium/high concurrence, so the
    # score saturates once the episode already behaves like a clearly
    # multi-contaminant case equivalent to three strong companions.
    score = min(100.0, (effective_companions / 3.0) * 100.0)
    return round(score, 2)
