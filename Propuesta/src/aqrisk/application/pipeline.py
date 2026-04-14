from __future__ import annotations

from datetime import UTC, datetime, timedelta

from aqrisk.alerting.service import build_alert
from aqrisk.application.scenarios import get_scenario
from aqrisk.aqi.epa import AQICalculator
from aqrisk.config import Settings
from aqrisk.domain.models import (
    FuzzyResult,
    HourlyObservation,
    InputSnapshot,
    ModuleResult,
    ParameterSeries,
)
from aqrisk.fuzzy.mamdani import MamdaniRiskEngine
from aqrisk.ingestion.openaq_client import OpenAQClient, OpenAQClientError
from aqrisk.processing.concurrence import compute_concurrence_score
from aqrisk.processing.context import ContextualRiskAdjuster
from aqrisk.processing.coverage import compute_global_coverage
from aqrisk.processing.normalization import normalize_snapshot
from aqrisk.processing.persistence import compute_persistence_score


class PipelineError(RuntimeError):
    """Represents recoverable errors during pipeline execution."""


class AirQualityRiskPipeline:
    """Executes the end-to-end air-quality risk evaluation pipeline."""

    MOCK_UNITS = {
        "pm25": "µg/m³",
        "pm10": "µg/m³",
        "co": "ppm",
        "no2": "ppm",
        "o3": "ppm",
        "so2": "ppm",
        "temperature": "°C",
        "humidity": "%",
    }
    SUPPORTED_OPENAQ_PARAMETERS = {"pm25", "pm2.5", "pm10", "temperature", "humidity", "no2", "o3", "co", "so2"}
    HISTORY_WINDOW_COUNT = 3

    def __init__(
        self,
        settings: Settings,
        *,
        aqi_calculator: AQICalculator | None = None,
        contextual_adjuster: ContextualRiskAdjuster | None = None,
        engine: MamdaniRiskEngine | None = None,
    ) -> None:
        """Initialize the pipeline and its collaborators."""
        self.settings = settings
        self.aqi_calculator = aqi_calculator or AQICalculator()
        self.contextual_adjuster = contextual_adjuster or ContextualRiskAdjuster()
        self.engine = engine or MamdaniRiskEngine()

    def run(self) -> ModuleResult:
        """Run the full evaluation pipeline and return a structured result."""
        snapshot = self._load_snapshot()
        snapshot = normalize_snapshot(snapshot)
        aqi_result = self.aqi_calculator.calculate(
            snapshot.series,
            min_fraction=self.settings.min_coverage / 100.0,
        )
        history = self._build_aqi_history(snapshot)
        persistence_score = compute_persistence_score(history)
        concurrence_score = compute_concurrence_score(
            aqi_result.subindices,
            aqi_result.global_aqi,
        )
        score, label, triggered = self.engine.evaluate(
            aqi_result.global_aqi,
            persistence_score,
            concurrence_score,
        )
        score, label, context_adjustments = self.contextual_adjuster.apply(
            label,
            score,
            snapshot,
            aqi_result,
        )
        fuzzy_result = FuzzyResult(score=score, label=label, triggered_rules=triggered)
        alert = build_alert(
            aqi_result,
            fuzzy_result,
            snapshot.coverage_global,
            self.settings.min_coverage,
        )
        return ModuleResult(
            snapshot=snapshot,
            aqi=aqi_result,
            concurrence_score=concurrence_score,
            persistence_score=persistence_score,
            fuzzy=fuzzy_result,
            context_adjustments=context_adjustments,
            alert=alert,
        )

    def _load_snapshot(self) -> InputSnapshot:
        """Dispatch snapshot construction based on the execution mode."""
        if self.settings.mode == "mock":
            return self._mock_snapshot()
        if self.settings.mode == "openaq":
            return self._openaq_snapshot()
        raise PipelineError(f"Unsupported mode: {self.settings.mode}")

    def _mock_snapshot(self) -> InputSnapshot:
        """Build a synthetic snapshot from the selected mock scenario."""
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        scenario = get_scenario(self.settings.scenario_id)
        series: dict[str, ParameterSeries] = {}

        for parameter, values in scenario.values.items():
            observations = []
            for offset, value in enumerate(values, start=1):
                end = now - timedelta(hours=len(values) - offset)
                start = end - timedelta(hours=1)
                observations.append(
                    HourlyObservation(
                        sensor_id=offset,
                        parameter=parameter,
                        value=value,
                        unit=self.MOCK_UNITS[parameter],
                        datetime_from=start,
                        datetime_to=end,
                        coverage=100.0,
                    )
                )
            series[parameter] = ParameterSeries(
                parameter=parameter,
                unit=self.MOCK_UNITS[parameter],
                observations=observations,
            )

        return InputSnapshot(
            source="mock",
            location_id=None,
            location_name=scenario.name,
            generated_at=now,
            series=series,
            coverage_global=compute_global_coverage(series),
        )

    def _openaq_snapshot(self) -> InputSnapshot:
        """Build a real snapshot from the OpenAQ API."""
        if not self.settings.openaq_api_key:
            raise PipelineError("OPENAQ_API_KEY is required for mode=openaq")
        if not self.settings.openaq_location_id:
            raise PipelineError("OPENAQ_LOCATION_ID or --location-id is required for mode=openaq")

        client = OpenAQClient(
            api_key=self.settings.openaq_api_key,
            base_url=self.settings.openaq_base_url,
        )
        location_id = self.settings.openaq_location_id
        try:
            location_name = client.get_location_name(location_id)
            sensors = client.get_sensors_by_location(location_id)
        except OpenAQClientError as exc:
            raise PipelineError(str(exc)) from exc

        selected = self._select_sensors(
            [sensor for sensor in sensors if sensor.parameter in self.SUPPORTED_OPENAQ_PARAMETERS]
        )
        series = {
            sensor.parameter: self._safe_fetch_hourly_series(client, sensor)
            for sensor in selected
        }
        if not series:
            raise PipelineError(f"No supported sensors found for OpenAQ location {location_id}")
        return InputSnapshot(
            source="openaq",
            location_id=location_id,
            location_name=location_name,
            generated_at=datetime.now(UTC),
            series=series,
            coverage_global=compute_global_coverage(series),
        )

    def _safe_fetch_hourly_series(
        self,
        client: OpenAQClient,
        sensor,
    ) -> ParameterSeries:
        """Fetch one hourly series and surface transport errors as pipeline failures."""
        try:
            return client.get_hourly_series(sensor, self.settings.lookback_hours)
        except OpenAQClientError as exc:
            raise PipelineError(str(exc)) from exc

    def _select_sensors(self, sensors):
        """Select a single sensor per parameter, preferring the lowest sensor id."""
        selected: dict[str, object] = {}
        for sensor in sorted(sensors, key=lambda item: item.sensor_id):
            if sensor.parameter not in selected:
                selected[sensor.parameter] = sensor
        return list(selected.values())

    def _build_aqi_history(self, snapshot: InputSnapshot) -> list[int]:
        """Build a short AQI history from progressively larger trailing windows."""
        history: list[int] = []
        min_fraction = self.settings.min_coverage / 100.0
        for offset in range(self.HISTORY_WINDOW_COUNT - 1, -1, -1):
            sliced_series: dict[str, ParameterSeries] = {}
            for parameter, series in snapshot.series.items():
                observations = series.observations[: len(series.observations) - offset] if offset else series.observations[:]
                if observations:
                    sliced_series[parameter] = ParameterSeries(
                        parameter=series.parameter,
                        unit=series.unit,
                        observations=observations,
                    )
            partial = self.aqi_calculator.calculate(sliced_series, min_fraction=min_fraction)
            if partial.global_aqi is not None:
                history.append(partial.global_aqi)
        return history
