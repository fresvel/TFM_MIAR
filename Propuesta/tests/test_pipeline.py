from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aqrisk.application.pipeline import AirQualityRiskPipeline, PipelineError
from aqrisk.config import Settings
from aqrisk.fuzzy.mamdani import RULE_MATRIX


class PipelineSmokeTest(unittest.TestCase):
    def test_mock_pipeline_returns_traceable_payload(self) -> None:
        settings = Settings(mode="mock")
        result = AirQualityRiskPipeline(settings).run()

        self.assertIsNotNone(result.aqi.global_aqi)
        self.assertIn(
            result.fuzzy.label,
            {
                "good",
                "moderate",
                "unhealthy_sensitive_groups",
                "unhealthy",
                "very_unhealthy",
                "hazardous",
            },
        )
        self.assertTrue(result.alert.message)
        self.assertGreaterEqual(result.snapshot.coverage_global, 0)
        self.assertIn("pm25", result.snapshot.series)
        self.assertIn("co", result.snapshot.series)
        self.assertIn("no2", result.snapshot.series)
        self.assertIn("o3", result.snapshot.series)
        self.assertTrue({"pm25", "pm10", "co", "no2", "o3", "so2"}.issubset(set(result.aqi.supported_parameters)))
        self.assertEqual(sum(len(persistence_map) for concurrence_map in RULE_MATRIX.values() for persistence_map in concurrence_map.values()), 54)

    def test_openaq_mode_requires_api_key(self) -> None:
        settings = Settings(mode="openaq", openaq_location_id=2178, openaq_api_key=None)
        with self.assertRaises(PipelineError):
            AirQualityRiskPipeline(settings).run()

    def test_mock_pipeline_supports_named_scenarios(self) -> None:
        settings = Settings(mode="mock", scenario_id="moderate_multicontaminant")
        result = AirQualityRiskPipeline(settings).run()

        self.assertEqual(result.snapshot.source, "mock")
        self.assertEqual(result.snapshot.location_name, "Moderate Multi-Contaminant")
        self.assertIsNotNone(result.aqi.global_aqi)


if __name__ == "__main__":
    unittest.main()
