from __future__ import annotations

from datetime import UTC, datetime, timedelta

from aqrisk.alerting.service import build_alert
from aqrisk.application.scenarios import get_scenario
from aqrisk.aqi.epa import calculate_aqi
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
from aqrisk.processing.context import apply_context_adjustment
from aqrisk.processing.coverage import compute_global_coverage
from aqrisk.processing.normalization import normalize_snapshot
from aqrisk.processing.persistence import compute_persistence_score


class PipelineError(RuntimeError):
    pass


class AirQualityRiskPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine = MamdaniRiskEngine()

    def run(self) -> ModuleResult:
        snapshot = self._load_snapshot()
        snapshot = normalize_snapshot(snapshot)
        aqi_result = calculate_aqi(
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
        score, label, context_adjustments = apply_context_adjustment(
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
        if self.settings.mode == "mock":
            return self._mock_snapshot()
        if self.settings.mode == "openaq":
            return self._openaq_snapshot()
        raise PipelineError(f"Unsupported mode: {self.settings.mode}")

    def _mock_snapshot(self) -> InputSnapshot:
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        scenario = get_scenario(self.settings.scenario_id)
        mock_values = scenario.values
        units = {
            "pm25": "µg/m³",
            "pm10": "µg/m³",
            "co": "ppm",
            "no2": "ppm",
            "o3": "ppm",
            "so2": "ppm",
            "temperature": "°C",
            "humidity": "%",
        }
        series: dict[str, ParameterSeries] = {}
        for parameter, values in mock_values.items():
            observations = []
            for offset, value in enumerate(values, start=1):
                end = now - timedelta(hours=len(values) - offset)
                start = end - timedelta(hours=1)
                observations.append(
                    HourlyObservation(
                        sensor_id=offset,
                        parameter=parameter,
                        value=value,
                        unit=units[parameter],
                        datetime_from=start,
                        datetime_to=end,
                        coverage=100.0,
                    )
                )
            series[parameter] = ParameterSeries(
                parameter=parameter,
                unit=units[parameter],
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
        supported = {"pm25", "pm2.5", "pm10", "temperature", "humidity", "no2", "o3", "co", "so2"}
        selected = self._select_sensors(
            [sensor for sensor in sensors if sensor.parameter in supported]
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
        try:
            return client.get_hourly_series(sensor, self.settings.lookback_hours)
        except OpenAQClientError as exc:
            raise PipelineError(str(exc)) from exc

    def _select_sensors(self, sensors):
        selected: dict[str, object] = {}
        for sensor in sorted(sensors, key=lambda item: item.sensor_id):
            if sensor.parameter not in selected:
                selected[sensor.parameter] = sensor
        return list(selected.values())

    def _build_aqi_history(self, snapshot: InputSnapshot) -> list[int]:
        history: list[int] = []
        min_fraction = self.settings.min_coverage / 100.0
        max_offset = 3
        for offset in range(max_offset - 1, -1, -1):
            sliced_series: dict[str, ParameterSeries] = {}
            for parameter, series in snapshot.series.items():
                observations = series.observations[: len(series.observations) - offset] if offset else series.observations[:]
                if observations:
                    sliced_series[parameter] = ParameterSeries(
                        parameter=series.parameter,
                        unit=series.unit,
                        observations=observations,
                    )
            partial = calculate_aqi(sliced_series, min_fraction=min_fraction)
            if partial.global_aqi is not None:
                history.append(partial.global_aqi)
        return history
