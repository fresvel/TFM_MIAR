from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AQICategoryRange:
    """Represents an AQI category interval and its public label."""

    lower: int
    upper: int
    label: str


@dataclass(frozen=True, slots=True)
class AQIBreakpoint:
    """Represents a concentration breakpoint interval for AQI interpolation."""

    concentration_low: float
    concentration_high: float
    index_low: int
    index_high: int


AQI_CATEGORIES: tuple[AQICategoryRange, ...] = (
    AQICategoryRange(0, 50, "good"),
    AQICategoryRange(51, 100, "moderate"),
    AQICategoryRange(101, 150, "unhealthy_sensitive_groups"),
    AQICategoryRange(151, 200, "unhealthy"),
    AQICategoryRange(201, 300, "very_unhealthy"),
    AQICategoryRange(301, 500, "hazardous"),
)

PM25_24H = "pm25_24h"
PM10_24H = "pm10_24h"
CO_8H = "co_8h"
NO2_1H = "no2_1h"
O3_8H = "o3_8h"
O3_1H = "o3_1h"
SO2_1H = "so2_1h"
SO2_24H = "so2_24h"

AQI_BREAKPOINTS: dict[str, tuple[AQIBreakpoint, ...]] = {
    PM25_24H: (
        AQIBreakpoint(0.0, 9.0, 0, 50),
        AQIBreakpoint(9.1, 35.4, 51, 100),
        AQIBreakpoint(35.5, 55.4, 101, 150),
        AQIBreakpoint(55.5, 125.4, 151, 200),
        AQIBreakpoint(125.5, 225.4, 201, 300),
        AQIBreakpoint(225.5, 325.4, 301, 500),
    ),
    PM10_24H: (
        AQIBreakpoint(0.0, 54.0, 0, 50),
        AQIBreakpoint(55.0, 154.0, 51, 100),
        AQIBreakpoint(155.0, 254.0, 101, 150),
        AQIBreakpoint(255.0, 354.0, 151, 200),
        AQIBreakpoint(355.0, 424.0, 201, 300),
        AQIBreakpoint(425.0, 604.0, 301, 500),
    ),
    CO_8H: (
        AQIBreakpoint(0.0, 4.4, 0, 50),
        AQIBreakpoint(4.5, 9.4, 51, 100),
        AQIBreakpoint(9.5, 12.4, 101, 150),
        AQIBreakpoint(12.5, 15.4, 151, 200),
        AQIBreakpoint(15.5, 30.4, 201, 300),
        AQIBreakpoint(30.5, 50.4, 301, 500),
    ),
    NO2_1H: (
        AQIBreakpoint(0.0, 53.0, 0, 50),
        AQIBreakpoint(54.0, 100.0, 51, 100),
        AQIBreakpoint(101.0, 360.0, 101, 150),
        AQIBreakpoint(361.0, 649.0, 151, 200),
        AQIBreakpoint(650.0, 1249.0, 201, 300),
        AQIBreakpoint(1250.0, 2049.0, 301, 500),
    ),
    O3_8H: (
        AQIBreakpoint(0.000, 0.054, 0, 50),
        AQIBreakpoint(0.055, 0.070, 51, 100),
        AQIBreakpoint(0.071, 0.085, 101, 150),
        AQIBreakpoint(0.086, 0.105, 151, 200),
        AQIBreakpoint(0.106, 0.200, 201, 300),
    ),
    O3_1H: (
        AQIBreakpoint(0.125, 0.164, 101, 150),
        AQIBreakpoint(0.165, 0.204, 151, 200),
        AQIBreakpoint(0.205, 0.404, 201, 300),
        AQIBreakpoint(0.405, 0.504, 301, 400),
        AQIBreakpoint(0.505, 0.604, 401, 500),
    ),
    SO2_1H: (
        AQIBreakpoint(0.0, 35.0, 0, 50),
        AQIBreakpoint(36.0, 75.0, 51, 100),
        AQIBreakpoint(76.0, 185.0, 101, 150),
        AQIBreakpoint(186.0, 304.0, 151, 200),
    ),
    SO2_24H: (
        AQIBreakpoint(305.0, 604.0, 201, 300),
        AQIBreakpoint(605.0, 1004.0, 301, 500),
    ),
}

AQI_PARAMETER_MAPPING = {
    "pm25": PM25_24H,
    "pm10": PM10_24H,
    "co": CO_8H,
    "no2": NO2_1H,
    "o3": O3_8H,
    "so2": SO2_1H,
}

ROUNDING_PRECISIONS: dict[str, int] = {
    PM25_24H: 10,
    CO_8H: 10,
    O3_8H: 1000,
    O3_1H: 1000,
}

REQUIRED_OBSERVATION_MINIMUM = 1
PPM_TO_PPB_FACTOR = 1000.0
PM24H_WINDOW = 24
CO_WINDOW = 8
O3_1H_APPLICABILITY_MIN = 0.125
