from __future__ import annotations

import json
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any

from aqrisk.api.constants import (
    API_MODES,
    MODEL_CONTEXT_PARAMETERS,
    MODEL_LAYERS,
    MODEL_SUPPORTED_PARAMETERS,
)
from aqrisk.application.pipeline import AirQualityRiskPipeline
from aqrisk.config import Settings
from aqrisk.fuzzy.mamdani import MamdaniRiskEngine, MembershipCurveFactory
from aqrisk.processing.context import ContextualRiskAdjuster


class JsonResponseWriter:
    """Writes JSON responses to the HTTP handler with the expected headers."""

    @classmethod
    def write(
        cls,
        handler: BaseHTTPRequestHandler,
        status: HTTPStatus,
        payload: dict[str, Any],
    ) -> None:
        """Send a JSON response with CORS headers."""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        handler.send_response(status.value)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(body)))
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type")
        handler.end_headers()
        handler.wfile.write(body)


class SettingsMapper:
    """Maps request payloads into runtime settings."""

    @staticmethod
    def from_request(base: Settings, payload: dict[str, Any]) -> Settings:
        """Build settings from the incoming JSON payload."""
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


class MetadataBuilder:
    """Builds the public model metadata consumed by the frontend."""

    def __init__(self, curve_factory: MembershipCurveFactory | None = None) -> None:
        """Initialize reusable collaborators for metadata serialization."""
        self._curve_factory = curve_factory or MembershipCurveFactory()

    def build(self, settings: Settings) -> dict[str, Any]:
        """Return the metadata payload for the current backend settings."""
        return {
            "modes": list(API_MODES),
            "default_config": {
                "mode": settings.mode,
                "location_id": settings.openaq_location_id,
                "lookback_hours": settings.lookback_hours,
                "min_coverage": settings.min_coverage,
                "scenario_id": settings.scenario_id,
            },
            "model": {
                "normative_basis": "EPA/AQS AQI Breakpoints",
                "supported_parameters": list(MODEL_SUPPORTED_PARAMETERS),
                "context_parameters": list(MODEL_CONTEXT_PARAMETERS),
                "main_rule_count": MamdaniRiskEngine().rule_count,
                "context_rule_count": ContextualRiskAdjuster().rule_count,
                "layers": list(MODEL_LAYERS),
                "membership_curves": {
                    "aqi": self._curve_factory.curve_set("aqi"),
                    "persistence": self._curve_factory.curve_set("persistence"),
                    "concurrence": self._curve_factory.curve_set("concurrence"),
                    "risk": self._curve_factory.curve_set("risk"),
                },
            },
        }


class ExplainabilityBuilder:
    """Builds explainability payloads from serialized module results."""

    def __init__(
        self,
        *,
        engine: MamdaniRiskEngine | None = None,
        adjuster: ContextualRiskAdjuster | None = None,
    ) -> None:
        """Initialize the explainability collaborators."""
        self._engine = engine or MamdaniRiskEngine()
        self._adjuster = adjuster or ContextualRiskAdjuster()

    def build(self, result: dict[str, Any]) -> dict[str, Any]:
        """Return the explainability payload expected by the frontend."""
        trace = self._engine.trace(
            result["aqi"]["global_aqi"],
            result["persistence_score"],
            result["concurrence_score"],
        )
        context_trace = self._adjuster.build_context_trace(result, trace)
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
                "ajuste_contextual": context_trace,
                "alertamiento_salida": result["alert"],
            }
        }


class EvaluationService:
    """Coordinates pipeline execution for the HTTP layer."""

    def evaluate(self, settings: Settings) -> dict[str, Any]:
        """Execute the pipeline and return a serialized result."""
        return AirQualityRiskPipeline(settings).run().to_dict()
