from __future__ import annotations

import argparse
import json
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from aqrisk.application.pipeline import AirQualityRiskPipeline, PipelineError
from aqrisk.application.scenarios import list_scenarios
from aqrisk.config import Settings
from aqrisk.fuzzy.mamdani import membership_curve_set, MamdaniRiskEngine
from aqrisk.ingestion.openaq_client import OpenAQClient, OpenAQClientError
from aqrisk.storage.history import HistoryStore


def _metadata_payload(settings: Settings) -> dict[str, Any]:
    return {
        "modes": ["mock", "openaq"],
        "default_config": {
            "mode": settings.mode,
            "location_id": settings.openaq_location_id,
            "lookback_hours": settings.lookback_hours,
            "min_coverage": settings.min_coverage,
            "scenario_id": settings.scenario_id,
        },
        "model": {
            "normative_basis": "EPA/AQS AQI Breakpoints",
            "supported_parameters": ["pm25", "pm10", "co", "no2", "o3", "so2"],
            "context_parameters": ["temperature", "humidity"],
            "main_rule_count": 54,
            "context_rule_count": 9,
            "layers": [
                "consolidacion_normativa",
                "variables_auxiliares",
                "inferencia_difusa_principal",
                "ajuste_contextual",
                "alertamiento_salida",
            ],
            "membership_curves": {
                "aqi": membership_curve_set("aqi"),
                "persistence": membership_curve_set("persistence"),
                "concurrence": membership_curve_set("concurrence"),
                "risk": membership_curve_set("risk"),
            },
        },
    }


def _build_explainability(result: dict[str, Any]) -> dict[str, Any]:
    engine = MamdaniRiskEngine()
    trace = engine.trace(
        result["aqi"]["global_aqi"],
        result["persistence_score"],
        result["concurrence_score"],
    )
    return {
        "layer_outputs": {
            "consolidacion_normativa": {
                "global_aqi": result["aqi"]["global_aqi"],
                "category": result["aqi"]["category"],
                "dominant_parameter": result["aqi"]["dominant_parameter"],
                "subindices": result["aqi"]["subindices"],
            },
            "variables_auxiliares": {
                "concurrence_score": result["concurrence_score"],
                "persistence_score": result["persistence_score"],
                "coverage_global": result["snapshot"]["coverage_global"],
            },
            "inferencia_difusa_principal": trace,
            "ajuste_contextual": {
                "adjustments": result["context_adjustments"],
            },
            "alertamiento_salida": result["alert"],
        }
    }


def _settings_from_request(base: Settings, payload: dict[str, Any]) -> Settings:
    mode = payload.get("mode", base.mode)
    location_id = payload.get("location_id", base.openaq_location_id)
    lookback_hours = payload.get("lookback_hours", base.lookback_hours)
    min_coverage = payload.get("min_coverage", base.min_coverage)
    scenario_id = payload.get("scenario_id", base.scenario_id)
    return replace(
        base,
        mode=str(mode),
        openaq_location_id=int(location_id) if location_id is not None else None,
        lookback_hours=int(lookback_hours),
        min_coverage=float(min_coverage),
        scenario_id=str(scenario_id),
    )


def _json_response(
    handler: BaseHTTPRequestHandler,
    status: HTTPStatus,
    payload: dict[str, Any],
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def create_handler(base_settings: Settings):
    history_store = HistoryStore(base_settings.history_path)

    class AQRiskRequestHandler(BaseHTTPRequestHandler):
        server_version = "AQRiskHTTP/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            _json_response(self, HTTPStatus.NO_CONTENT, {})

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                _json_response(
                    self,
                    HTTPStatus.OK,
                    {"status": "ok", "service": "aqrisk-api"},
                )
                return
            if self.path == "/api/v1/metadata":
                _json_response(self, HTTPStatus.OK, _metadata_payload(base_settings))
                return
            if self.path == "/api/v1/scenarios":
                _json_response(self, HTTPStatus.OK, {"items": list_scenarios()})
                return
            if self.path.startswith("/api/v1/history"):
                _json_response(self, HTTPStatus.OK, {"items": history_store.list(limit=25)})
                return
            if self.path.startswith("/api/v1/locations/") and self.path.endswith("/sensors"):
                try:
                    location_id = int(self.path.split("/")[4])
                    client = OpenAQClient(
                        api_key=base_settings.openaq_api_key or "",
                        base_url=base_settings.openaq_base_url,
                    )
                    sensors = client.list_sensor_summaries(location_id)
                except (ValueError, OpenAQClientError) as exc:
                    _json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                    return
                _json_response(self, HTTPStatus.OK, {"items": sensors})
                return
            if self.path.startswith("/api/v1/locations"):
                try:
                    query = self.path.split("?", 1)[1] if "?" in self.path else ""
                    params = {}
                    for item in query.split("&"):
                        if not item or "=" not in item:
                            continue
                        key, value = item.split("=", 1)
                        params[key] = value
                    client = OpenAQClient(
                        api_key=base_settings.openaq_api_key or "",
                        base_url=base_settings.openaq_base_url,
                    )
                    items = client.list_locations(
                        iso=params.get("iso", "EC"),
                        limit=int(params.get("limit", "20")),
                        coordinates=params.get("coordinates", "-2.15968,-79.89807"),
                        radius=int(params.get("radius", "30000")),
                    )
                except (ValueError, OpenAQClientError) as exc:
                    _json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                    return
                _json_response(self, HTTPStatus.OK, {"items": items})
                return
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/v1/evaluate":
                _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length > 0 else b"{}"
                request_payload = json.loads(raw.decode("utf-8"))
                settings = _settings_from_request(base_settings, request_payload)
                result = AirQualityRiskPipeline(settings).run()
            except json.JSONDecodeError:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "JSON inválido"})
                return
            except (ValueError, TypeError) as exc:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            except PipelineError as exc:
                _json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
                return
            response_payload = result.to_dict()
            response_payload["explainability"] = _build_explainability(response_payload)
            history_store.append(request=request_payload, response=response_payload)
            _json_response(self, HTTPStatus.OK, response_payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    return AQRiskRequestHandler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AQRisk HTTP API")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8010)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    handler = create_handler(settings)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    try:
        print(f"AQRisk API listening on http://{args.host}:{args.port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
