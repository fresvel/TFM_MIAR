from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from aqrisk.domain.models import HourlyObservation, ParameterSeries, SensorDescriptor


OPENAQ_USER_AGENT = "aqrisk/0.1.0"
OPENAQ_TIMEOUT_SECONDS = 30
OPENAQ_LOOKBACK_PADDING_HOURS = 2
OPENAQ_MIN_HOURLY_LIMIT = 10


class OpenAQClientError(RuntimeError):
    """Represents failures produced while talking to the OpenAQ API."""


def _parse_datetime(value: str) -> datetime:
    """Parse an OpenAQ UTC datetime string into an aware datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


@dataclass(slots=True)
class OpenAQClient:
    """HTTP client for retrieving locations, sensors and hourly series from OpenAQ."""

    api_key: str
    base_url: str = "https://api.openaq.org/v3"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GET request against OpenAQ and decode its JSON response."""
        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            url=f"{self.base_url}{path}{query}",
            headers={
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "User-Agent": OPENAQ_USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=OPENAQ_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise OpenAQClientError(
                f"OpenAQ responded with HTTP {exc.code} for {path}: {detail or exc.reason}"
            ) from exc
        except URLError as exc:
            raise OpenAQClientError(f"OpenAQ request failed for {path}: {exc.reason}") from exc

    def get_location_name(self, location_id: int) -> str:
        """Return the display name for a single OpenAQ location."""
        payload = self._get(f"/locations/{location_id}")
        results = payload.get("results", [])
        if not results:
            raise ValueError(f"OpenAQ location {location_id} not found")
        return results[0].get("name") or f"location_{location_id}"

    def list_locations(
        self,
        *,
        iso: str | None = None,
        limit: int = 20,
        coordinates: str | None = None,
        radius: int | None = None,
    ) -> list[dict[str, Any]]:
        """List simplified locations for frontend selection."""
        params: dict[str, Any] = {"limit": limit, "page": 1}
        if iso:
            params["iso"] = iso
        if coordinates:
            params["coordinates"] = coordinates
        if radius is not None:
            params["radius"] = radius
        payload = self._get("/locations", params=params)
        return [
            {
                "id": int(item["id"]),
                "name": item.get("name") or f"location_{item['id']}",
                "city": item.get("city"),
                "country": (item.get("country") or {}).get("code"),
                "coordinates": item.get("coordinates"),
            }
            for item in payload.get("results", [])
        ]

    def get_sensors_by_location(self, location_id: int) -> list[SensorDescriptor]:
        """Return the sensors published by a location."""
        payload = self._get(f"/locations/{location_id}/sensors")
        sensors: list[SensorDescriptor] = []
        for item in payload.get("results", []):
            parameter = item["parameter"]["name"].lower()
            sensors.append(
                SensorDescriptor(
                    sensor_id=int(item["id"]),
                    parameter=parameter,
                    units=item["parameter"]["units"],
                )
            )
        return sensors

    def list_sensor_summaries(self, location_id: int) -> list[dict[str, Any]]:
        """Return sensor metadata as plain dictionaries for API responses."""
        sensors = self.get_sensors_by_location(location_id)
        return [
            {"sensor_id": sensor.sensor_id, "parameter": sensor.parameter, "units": sensor.units}
            for sensor in sensors
        ]

    def get_hourly_series(
        self,
        sensor: SensorDescriptor,
        lookback_hours: int,
    ) -> ParameterSeries:
        """Return one hourly time series for a sensor and lookback window."""
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        start = now - timedelta(hours=lookback_hours)
        payload = self._get(
            f"/sensors/{sensor.sensor_id}/hours",
            params={
                "datetime_from": start.isoformat(),
                "datetime_to": now.isoformat(),
                "limit": max(lookback_hours + OPENAQ_LOOKBACK_PADDING_HOURS, OPENAQ_MIN_HOURLY_LIMIT),
                "page": 1,
            },
        )
        observations: list[HourlyObservation] = []
        for item in payload.get("results", []):
            coverage = item.get("coverage") or {}
            period = item.get("period") or {}
            datetime_from = period.get("datetimeFrom") or coverage.get("datetimeFrom")
            datetime_to = period.get("datetimeTo") or coverage.get("datetimeTo")
            if not datetime_from or not datetime_to:
                continue
            observations.append(
                HourlyObservation(
                    sensor_id=sensor.sensor_id,
                    parameter=sensor.parameter,
                    value=float(item["value"]),
                    unit=item["parameter"]["units"],
                    datetime_from=_parse_datetime(datetime_from["utc"]),
                    datetime_to=_parse_datetime(datetime_to["utc"]),
                    coverage=float(coverage.get("percentCoverage"))
                    if coverage.get("percentCoverage") is not None
                    else None,
                )
            )
        observations.sort(key=lambda observation: observation.datetime_from)
        if len(observations) > lookback_hours:
            observations = observations[-lookback_hours:]
        return ParameterSeries(parameter=sensor.parameter, unit=sensor.units, observations=observations)
