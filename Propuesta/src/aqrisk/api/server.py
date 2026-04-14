from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from aqrisk.api.constants import (
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_LOCATION_COORDINATES,
    DEFAULT_LOCATION_ISO,
    DEFAULT_LOCATION_LIMIT,
    DEFAULT_LOCATION_RADIUS,
    EVALUATE_ROUTE,
    HEALTH_ROUTE,
    HISTORY_ROUTE,
    JSON_ERROR_INVALID,
    JSON_ERROR_ROUTE_NOT_FOUND,
    LOCATIONS_ROUTE,
    METADATA_ROUTE,
    SCENARIOS_ROUTE,
    SENSORS_ROUTE_SUFFIX,
)
from aqrisk.api.services import (
    EvaluationService,
    ExplainabilityBuilder,
    JsonResponseWriter,
    MetadataBuilder,
    SettingsMapper,
)
from aqrisk.application.pipeline import PipelineError
from aqrisk.application.scenarios import list_scenarios
from aqrisk.config import Settings
from aqrisk.ingestion.openaq_client import OpenAQClient, OpenAQClientError
from aqrisk.storage.history import HistoryStore


def create_handler(base_settings: Settings):
    """Create the HTTP handler bound to the provided base settings."""
    history_store = HistoryStore(base_settings.history_path)
    metadata_builder = MetadataBuilder()
    explainability_builder = ExplainabilityBuilder()
    evaluation_service = EvaluationService()

    class AQRiskRequestHandler(BaseHTTPRequestHandler):
        """Serve the public HTTP endpoints for the AQRisk prototype."""

        server_version = "AQRiskHTTP/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            """Respond to CORS preflight requests."""
            JsonResponseWriter.write(self, HTTPStatus.NO_CONTENT, {})

        def do_GET(self) -> None:  # noqa: N802
            """Serve read-only API resources."""
            if self.path == HEALTH_ROUTE:
                JsonResponseWriter.write(
                    self,
                    HTTPStatus.OK,
                    {"status": "ok", "service": "aqrisk-api"},
                )
                return

            if self.path == METADATA_ROUTE:
                JsonResponseWriter.write(self, HTTPStatus.OK, metadata_builder.build(base_settings))
                return

            if self.path == SCENARIOS_ROUTE:
                JsonResponseWriter.write(self, HTTPStatus.OK, {"items": list_scenarios()})
                return

            if self.path.startswith(HISTORY_ROUTE):
                JsonResponseWriter.write(
                    self,
                    HTTPStatus.OK,
                    {"items": history_store.list(limit=DEFAULT_HISTORY_LIMIT)},
                )
                return

            if self.path.startswith(f"{LOCATIONS_ROUTE}/") and self.path.endswith(SENSORS_ROUTE_SUFFIX):
                self._handle_location_sensors()
                return

            if self.path.startswith(LOCATIONS_ROUTE):
                self._handle_locations()
                return

            JsonResponseWriter.write(self, HTTPStatus.NOT_FOUND, {"error": JSON_ERROR_ROUTE_NOT_FOUND})

        def do_POST(self) -> None:  # noqa: N802
            """Serve mutating API resources."""
            if self.path != EVALUATE_ROUTE:
                JsonResponseWriter.write(self, HTTPStatus.NOT_FOUND, {"error": JSON_ERROR_ROUTE_NOT_FOUND})
                return

            try:
                request_payload = self._read_json_payload()
                settings = SettingsMapper.from_request(base_settings, request_payload)
                payload = evaluation_service.evaluate(settings)
            except json.JSONDecodeError:
                JsonResponseWriter.write(self, HTTPStatus.BAD_REQUEST, {"error": JSON_ERROR_INVALID})
                return
            except (ValueError, TypeError) as exc:
                JsonResponseWriter.write(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            except PipelineError as exc:
                JsonResponseWriter.write(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            payload["explainability"] = explainability_builder.build(payload)
            history_store.append(request=request_payload, response=payload)
            JsonResponseWriter.write(self, HTTPStatus.OK, payload)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            """Silence the default request logging in tests and local runs."""
            return

        def _read_json_payload(self) -> dict[str, Any]:
            """Read and decode the JSON request body."""
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

        def _handle_location_sensors(self) -> None:
            """Return the sensors associated with a single OpenAQ location."""
            try:
                location_id = int(self.path.split("/")[4])
                client = OpenAQClient(
                    api_key=base_settings.openaq_api_key or "",
                    base_url=base_settings.openaq_base_url,
                )
                sensors = client.list_sensor_summaries(location_id)
            except (ValueError, OpenAQClientError) as exc:
                JsonResponseWriter.write(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            JsonResponseWriter.write(self, HTTPStatus.OK, {"items": sensors})

        def _handle_locations(self) -> None:
            """Return simplified OpenAQ locations for frontend discovery."""
            try:
                params = self._parse_query_string()
                client = OpenAQClient(
                    api_key=base_settings.openaq_api_key or "",
                    base_url=base_settings.openaq_base_url,
                )
                items = client.list_locations(
                    iso=params.get("iso", DEFAULT_LOCATION_ISO),
                    limit=int(params.get("limit", str(DEFAULT_LOCATION_LIMIT))),
                    coordinates=params.get("coordinates", DEFAULT_LOCATION_COORDINATES),
                    radius=int(params.get("radius", str(DEFAULT_LOCATION_RADIUS))),
                )
            except (ValueError, OpenAQClientError) as exc:
                JsonResponseWriter.write(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            JsonResponseWriter.write(self, HTTPStatus.OK, {"items": items})

        def _parse_query_string(self) -> dict[str, str]:
            """Parse the query string using the current request path."""
            query = self.path.split("?", 1)[1] if "?" in self.path else ""
            params: dict[str, str] = {}
            for item in query.split("&"):
                if not item or "=" not in item:
                    continue
                key, value = item.split("=", 1)
                params[key] = value
            return params

    return AQRiskRequestHandler


def run_server(settings: Settings, host: str, port: int) -> None:
    """Start the threaded HTTP server using the provided configuration."""
    server = ThreadingHTTPServer((host, port), create_handler(settings))
    print(f"AQRisk API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the HTTP API entrypoint."""
    parser = argparse.ArgumentParser(description="Run AQRisk HTTP API")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8010)
    return parser


def main() -> int:
    """Execute the HTTP API entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings.from_env()
    run_server(settings, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
