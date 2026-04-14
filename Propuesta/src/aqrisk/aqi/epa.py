from __future__ import annotations

from math import floor
from statistics import mean

from aqrisk.aqi.constants import (
    AQI_BREAKPOINTS,
    AQI_CATEGORIES,
    AQI_PARAMETER_MAPPING,
    CO_8H,
    CO_WINDOW,
    NO2_1H,
    O3_1H,
    O3_1H_APPLICABILITY_MIN,
    O3_8H,
    PM10_24H,
    PM24H_WINDOW,
    PM25_24H,
    PPM_TO_PPB_FACTOR,
    REQUIRED_OBSERVATION_MINIMUM,
    ROUNDING_PRECISIONS,
    SO2_1H,
    SO2_24H,
)
from aqrisk.domain.models import AQIResult, ParameterSeries


DEFAULT_MIN_FRACTION = 0.8
AQI_NO_DATA_LABEL = "sin_datos"
AQI_OUT_OF_RANGE_LABEL = "fuera_de_rango"


class AQICalculator:
    """Calculates AQI values using EPA/AQS breakpoints and window rules."""

    def truncate(self, parameter_key: str, concentration: float) -> float:
        """Truncate a concentration using the precision required by the pollutant.

        Args:
            parameter_key: Internal breakpoint key, for example `pm25_24h`.
            concentration: Concentration to be truncated.

        Returns:
            The truncated concentration value.
        """
        precision = ROUNDING_PRECISIONS.get(parameter_key)
        if precision is None:
            return float(floor(concentration))
        return floor(concentration * precision) / precision

    def calculate_subindex_for_key(self, parameter_key: str, concentration: float) -> int | None:
        """Interpolate an AQI subindex for an internal breakpoint key."""
        breakpoints = AQI_BREAKPOINTS.get(parameter_key)
        if breakpoints is None:
            return None

        value = self.truncate(parameter_key, concentration)
        for breakpoint in breakpoints:
            if breakpoint.concentration_low <= value <= breakpoint.concentration_high:
                slope = (breakpoint.index_high - breakpoint.index_low) / (
                    breakpoint.concentration_high - breakpoint.concentration_low
                )
                return round(slope * (value - breakpoint.concentration_low) + breakpoint.index_low)
        return None

    def required_observations(self, window: int, min_fraction: float) -> int:
        """Return the minimum observations required to accept a partial window."""
        return max(REQUIRED_OBSERVATION_MINIMUM, int(window * min_fraction + 0.9999))

    def mean_last(self, values: list[float], window: int, min_fraction: float) -> float | None:
        """Return the mean of the trailing window when coverage is sufficient."""
        if len(values) < self.required_observations(window, min_fraction):
            return None
        return mean(values[-min(window, len(values)):])

    @staticmethod
    def latest_value(series: ParameterSeries) -> float | None:
        """Return the last observed value in a normalized parameter series."""
        if not series.observations:
            return None
        return series.observations[-1].value

    @staticmethod
    def ppm_to_ppb(value: float | None) -> float | None:
        """Convert parts per million into parts per billion."""
        if value is None:
            return None
        return value * PPM_TO_PPB_FACTOR

    def representative_concentration(
        self,
        parameter: str,
        series: ParameterSeries,
        min_fraction: float,
    ) -> tuple[str, float] | None:
        """Resolve the representative concentration for a pollutant series."""
        values = [observation.value for observation in series.observations]
        if not values:
            return None

        if parameter == "pm25":
            concentration = self.mean_last(values, PM24H_WINDOW, min_fraction)
            return (PM25_24H, concentration) if concentration is not None else None

        if parameter == "pm10":
            concentration = self.mean_last(values, PM24H_WINDOW, min_fraction)
            return (PM10_24H, concentration) if concentration is not None else None

        if parameter == "co":
            concentration = self.mean_last(values, CO_WINDOW, min_fraction)
            return (CO_8H, concentration) if concentration is not None else None

        if parameter == "no2":
            concentration = self.ppm_to_ppb(self.latest_value(series))
            return (NO2_1H, concentration) if concentration is not None else None

        if parameter == "o3":
            return self._represent_ozone(series, values, min_fraction)

        if parameter == "so2":
            return self._represent_sulfur_dioxide(series, values, min_fraction)

        return None

    def _represent_ozone(
        self,
        series: ParameterSeries,
        values: list[float],
        min_fraction: float,
    ) -> tuple[str, float] | None:
        """Resolve the best ozone concentration window based on AQI score."""
        latest_1h = self.latest_value(series)
        avg_8h = self.mean_last(values, CO_WINDOW, min_fraction)
        candidates: list[tuple[str, float]] = []
        if avg_8h is not None:
            candidates.append((O3_8H, avg_8h))
        if latest_1h is not None and latest_1h >= O3_1H_APPLICABILITY_MIN:
            candidates.append((O3_1H, latest_1h))
        if not candidates:
            return None

        scored = [
            (key, value, self.calculate_subindex_for_key(key, value) or -1)
            for key, value in candidates
        ]
        best = max(scored, key=lambda item: item[2])
        return (best[0], best[1]) if best[2] >= 0 else None

    def _represent_sulfur_dioxide(
        self,
        series: ParameterSeries,
        values: list[float],
        min_fraction: float,
    ) -> tuple[str, float] | None:
        """Resolve the best sulfur dioxide concentration window based on AQI score."""
        latest_1h = self.ppm_to_ppb(self.latest_value(series))
        avg_24h = self.ppm_to_ppb(self.mean_last(values, PM24H_WINDOW, min_fraction))
        candidates: list[tuple[str, float]] = []
        if latest_1h is not None:
            candidates.append((SO2_1H, latest_1h))
        if avg_24h is not None:
            candidates.append((SO2_24H, avg_24h))
        if not candidates:
            return None

        scored = [
            (key, value, self.calculate_subindex_for_key(key, value) or -1)
            for key, value in candidates
        ]
        valid = [item for item in scored if item[2] >= 0]
        if not valid:
            return None
        best = max(valid, key=lambda item: item[2])
        return best[0], best[1]

    def calculate_subindex(self, parameter: str, concentration: float) -> int | None:
        """Calculate a pollutant AQI subindex from its public parameter name."""
        parameter_key = AQI_PARAMETER_MAPPING.get(parameter.lower(), parameter.lower())
        return self.calculate_subindex_for_key(parameter_key, concentration)

    def classify(self, aqi_value: int | None) -> str:
        """Map an AQI value to the public categorical label."""
        if aqi_value is None:
            return AQI_NO_DATA_LABEL
        for category in AQI_CATEGORIES:
            if category.lower <= aqi_value <= category.upper:
                return category.label
        return AQI_OUT_OF_RANGE_LABEL

    def calculate(
        self,
        series_map: dict[str, ParameterSeries],
        min_fraction: float = DEFAULT_MIN_FRACTION,
    ) -> AQIResult:
        """Calculate subindices, dominant parameter and AQI category."""
        subindices: dict[str, int] = {}
        supported_parameters: list[str] = []
        unsupported_parameters: list[str] = []

        for parameter, series in series_map.items():
            representative = self.representative_concentration(parameter, series, min_fraction)
            if representative is None:
                unsupported_parameters.append(parameter)
                continue
            breakpoint_key, concentration = representative
            subindex = self.calculate_subindex_for_key(breakpoint_key, concentration)
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
                category=AQI_NO_DATA_LABEL,
                supported_parameters=supported_parameters,
                unsupported_parameters=unsupported_parameters,
            )

        dominant_parameter = max(subindices, key=subindices.get)
        global_aqi = subindices[dominant_parameter]
        return AQIResult(
            subindices=subindices,
            global_aqi=global_aqi,
            dominant_parameter=dominant_parameter,
            category=self.classify(global_aqi),
            supported_parameters=supported_parameters,
            unsupported_parameters=unsupported_parameters,
        )
