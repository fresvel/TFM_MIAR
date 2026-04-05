from __future__ import annotations

from math import floor
from statistics import mean

from aqrisk.domain.models import AQIResult, ParameterSeries


CATEGORIES = [
    (0, 50, "good"),
    (51, 100, "moderate"),
    (101, 150, "unhealthy_sensitive_groups"),
    (151, 200, "unhealthy"),
    (201, 300, "very_unhealthy"),
    (301, 500, "hazardous"),
]

BREAKPOINTS: dict[str, list[tuple[float, float, int, int]]] = {
    "pm25_24h": [
        (0.0, 9.0, 0, 50),
        (9.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200),
        (125.5, 225.4, 201, 300),
        (225.5, 325.4, 301, 500),
    ],
    "pm10_24h": [
        (0.0, 54.0, 0, 50),
        (55.0, 154.0, 51, 100),
        (155.0, 254.0, 101, 150),
        (255.0, 354.0, 151, 200),
        (355.0, 424.0, 201, 300),
        (425.0, 604.0, 301, 500),
    ],
    "co_8h": [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
    "no2_1h": [
        (0.0, 53.0, 0, 50),
        (54.0, 100.0, 51, 100),
        (101.0, 360.0, 101, 150),
        (361.0, 649.0, 151, 200),
        (650.0, 1249.0, 201, 300),
        (1250.0, 2049.0, 301, 500),
    ],
    "o3_8h": [
        (0.000, 0.054, 0, 50),
        (0.055, 0.070, 51, 100),
        (0.071, 0.085, 101, 150),
        (0.086, 0.105, 151, 200),
        (0.106, 0.200, 201, 300),
    ],
    "o3_1h": [
        (0.125, 0.164, 101, 150),
        (0.165, 0.204, 151, 200),
        (0.205, 0.404, 201, 300),
        (0.405, 0.504, 301, 400),
        (0.505, 0.604, 401, 500),
    ],
    "so2_1h": [
        (0.0, 35.0, 0, 50),
        (36.0, 75.0, 51, 100),
        (76.0, 185.0, 101, 150),
        (186.0, 304.0, 151, 200),
    ],
    "so2_24h": [
        (305.0, 604.0, 201, 300),
        (605.0, 1004.0, 301, 500),
    ],
}


def _truncate(parameter_key: str, concentration: float) -> float:
    if parameter_key in {"pm25_24h", "co_8h"}:
        return floor(concentration * 10) / 10
    if parameter_key in {"o3_8h", "o3_1h"}:
        return floor(concentration * 1000) / 1000
    return float(floor(concentration))


def _calculate_subindex_for_key(parameter_key: str, concentration: float) -> int | None:
    if parameter_key not in BREAKPOINTS:
        return None
    value = _truncate(parameter_key, concentration)
    for c_low, c_high, i_low, i_high in BREAKPOINTS[parameter_key]:
        if c_low <= value <= c_high:
            return round(((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low)
    return None


def _required_observations(window: int, min_fraction: float) -> int:
    return max(1, int(window * min_fraction + 0.9999))


def _mean_last(values: list[float], window: int, min_fraction: float) -> float | None:
    if len(values) < _required_observations(window, min_fraction):
        return None
    return mean(values[-min(window, len(values)):])


def _latest_value(series: ParameterSeries) -> float | None:
    if not series.observations:
        return None
    return series.observations[-1].value


def _ppm_to_ppb(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 1000.0


def _representative_concentration(
    parameter: str,
    series: ParameterSeries,
    min_fraction: float,
) -> tuple[str, float] | None:
    values = [observation.value for observation in series.observations]
    if not values:
        return None

    if parameter == "pm25":
        concentration = _mean_last(values, 24, min_fraction)
        return ("pm25_24h", concentration) if concentration is not None else None

    if parameter == "pm10":
        concentration = _mean_last(values, 24, min_fraction)
        return ("pm10_24h", concentration) if concentration is not None else None

    if parameter == "co":
        concentration = _mean_last(values, 8, min_fraction)
        return ("co_8h", concentration) if concentration is not None else None

    if parameter == "no2":
        concentration = _ppm_to_ppb(_latest_value(series))
        return ("no2_1h", concentration) if concentration is not None else None

    if parameter == "o3":
        latest_1h = _latest_value(series)
        avg_8h = _mean_last(values, 8, min_fraction)
        candidates: list[tuple[str, float]] = []
        if avg_8h is not None:
            candidates.append(("o3_8h", avg_8h))
        if latest_1h is not None and latest_1h >= 0.125:
            candidates.append(("o3_1h", latest_1h))
        if not candidates:
            return None
        scored = [
            (key, value, _calculate_subindex_for_key(key, value) or -1)
            for key, value in candidates
        ]
        best = max(scored, key=lambda item: item[2])
        return (best[0], best[1]) if best[2] >= 0 else None

    if parameter == "so2":
        latest_1h = _ppm_to_ppb(_latest_value(series))
        avg_24h = _ppm_to_ppb(_mean_last(values, 24, min_fraction))
        candidates: list[tuple[str, float]] = []
        if latest_1h is not None:
            candidates.append(("so2_1h", latest_1h))
        if avg_24h is not None:
            candidates.append(("so2_24h", avg_24h))
        if not candidates:
            return None
        scored = [
            (key, value, _calculate_subindex_for_key(key, value) or -1)
            for key, value in candidates
        ]
        valid = [item for item in scored if item[2] >= 0]
        if not valid:
            return None
        best = max(valid, key=lambda item: item[2])
        return best[0], best[1]

    return None


def calculate_subindex(parameter: str, concentration: float) -> int | None:
    mapping = {
        "pm25": "pm25_24h",
        "pm10": "pm10_24h",
        "co": "co_8h",
        "no2": "no2_1h",
        "o3": "o3_8h",
        "so2": "so2_1h",
    }
    parameter_key = mapping.get(parameter.lower(), parameter.lower())
    return _calculate_subindex_for_key(parameter_key, concentration)


def classify_aqi(aqi_value: int | None) -> str:
    if aqi_value is None:
        return "sin_datos"
    for lower, upper, label in CATEGORIES:
        if lower <= aqi_value <= upper:
            return label
    return "fuera_de_rango"


def calculate_aqi(
    series_map: dict[str, ParameterSeries],
    min_fraction: float = 0.8,
) -> AQIResult:
    subindices: dict[str, int] = {}
    supported_parameters: list[str] = []
    unsupported_parameters: list[str] = []

    for parameter, series in series_map.items():
        representative = _representative_concentration(parameter, series, min_fraction)
        if representative is None:
            unsupported_parameters.append(parameter)
            continue
        breakpoint_key, concentration = representative
        subindex = _calculate_subindex_for_key(breakpoint_key, concentration)
        if subindex is None:
            unsupported_parameters.append(parameter)
            continue
        supported_parameters.append(parameter)
        subindices[parameter] = subindex

    if not subindices:
        return AQIResult(
            subindices={},
            global_aqi=None,
            dominant_parameter=None,
            category="sin_datos",
            supported_parameters=supported_parameters,
            unsupported_parameters=unsupported_parameters,
        )

    dominant_parameter = max(subindices, key=subindices.get)
    global_aqi = subindices[dominant_parameter]
    return AQIResult(
        subindices=subindices,
        global_aqi=global_aqi,
        dominant_parameter=dominant_parameter,
        category=classify_aqi(global_aqi),
        supported_parameters=supported_parameters,
        unsupported_parameters=unsupported_parameters,
    )
