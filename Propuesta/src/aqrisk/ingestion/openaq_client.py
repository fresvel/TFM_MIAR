from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from aqrisk.domain.models import HourlyObservation, ParameterSeries, SensorDescriptor


class OpenAQClientError(RuntimeError):
    pass


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


@dataclass(slots=True)
class OpenAQClient:
    api_key: str
    base_url: str = "https://api.openaq.org/v3"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            url=f"{self.base_url}{path}{query}",
            headers={
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "User-Agent": "aqrisk/0.1.0",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise OpenAQClientError(
                f"OpenAQ responded with HTTP {exc.code} for {path}: {detail or exc.reason}"
            ) from exc
        except URLError as exc:
            raise OpenAQClientError(f"OpenAQ request failed for {path}: {exc.reason}") from exc

    def get_location_name(self, location_id: int) -> str:
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
        params: dict[str, Any] = {"limit": limit, "page": 1}
        if iso:
            params["iso"] = iso
        if coordinates:
            params["coordinates"] = coordinates
        if radius is not None:
            params["radius"] = radius
        payload = self._get("/locations", params=params)
        results: list[dict[str, Any]] = []
        for item in payload.get("results", []):
            results.append(
                {
                    "id": int(item["id"]),
                    "name": item.get("name") or f"location_{item['id']}",
                    "city": item.get("city"),
                    "country": (item.get("country") or {}).get("code"),
                    "coordinates": item.get("coordinates"),
                }
            )
        return results

    def get_sensors_by_location(self, location_id: int) -> list[SensorDescriptor]:
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
        sensors = self.get_sensors_by_location(location_id)
        return [
            {
                "sensor_id": sensor.sensor_id,
                "parameter": sensor.parameter,
                "units": sensor.units,
            }
            for sensor in sensors
        ]

    def get_hourly_series(
        self,
        sensor: SensorDescriptor,
        lookback_hours: int,
    ) -> ParameterSeries:
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        start = now - timedelta(hours=lookback_hours)
        payload = self._get(
            f"/sensors/{sensor.sensor_id}/hours",
            params={
                "datetime_from": start.isoformat(),
                "datetime_to": now.isoformat(),
                "limit": max(lookback_hours + 2, 10),
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
        observations.sort(key=lambda obs: obs.datetime_from)
        if len(observations) > lookback_hours:
            observations = observations[-lookback_hours:]
        return ParameterSeries(parameter=sensor.parameter, unit=sensor.units, observations=observations)
