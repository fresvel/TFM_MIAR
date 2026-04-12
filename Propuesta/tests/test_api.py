from __future__ import annotations

import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading
import unittest
from urllib import error, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aqrisk.api.server import create_handler
from aqrisk.config import Settings


class ApiServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        history_path = str(Path(self.tempdir.name) / "history.jsonl")
        settings = Settings(mode="mock", history_path=history_path)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(settings))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()
        self.tempdir.cleanup()

    def _request(self, path: str, *, method: str = "GET", payload: dict | None = None, raw_body: bytes | None = None):
        if raw_body is not None:
            body = raw_body
        elif payload is not None:
            body = json.dumps(payload).encode("utf-8")
        else:
            body = None
        headers = {}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=5) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            return exc.code, json.loads(raw) if raw else {}

    def test_health_endpoint_returns_ok(self) -> None:
        status, payload = self._request("/health")

        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "aqrisk-api")

    def test_metadata_exposes_model_contract(self) -> None:
        status, payload = self._request("/api/v1/metadata")

        self.assertEqual(status, 200)
        self.assertEqual(payload["modes"], ["mock", "openaq"])
        self.assertEqual(payload["model"]["main_rule_count"], 54)
        self.assertEqual(payload["model"]["context_rule_count"], 9)
        self.assertIn("consolidacion_normativa", payload["model"]["layers"])

    def test_evaluate_mock_run_is_persisted_in_history(self) -> None:
        status, payload = self._request(
            "/api/v1/evaluate",
            method="POST",
            payload={"mode": "mock", "scenario_id": "moderate_multicontaminant"},
        )

        self.assertEqual(status, 200)
        self.assertEqual(payload["snapshot"]["source"], "mock")
        self.assertIn("explainability", payload)
        self.assertIn("alert", payload)

        history_status, history_payload = self._request("/api/v1/history")
        self.assertEqual(history_status, 200)
        self.assertEqual(len(history_payload["items"]), 1)
        self.assertEqual(history_payload["items"][0]["summary"]["source"], "mock")

    def test_diffuse_overlap_returns_multiple_triggered_rules_in_explainability(self) -> None:
        status, payload = self._request(
            "/api/v1/evaluate",
            method="POST",
            payload={"mode": "mock", "scenario_id": "diffuse_overlap"},
        )

        self.assertEqual(status, 200)
        rules = payload["explainability"]["layer_outputs"]["inferencia_difusa_principal"]["rules"]
        self.assertGreaterEqual(len(rules), 4)
        self.assertTrue(all(rule["strength"] > 0 for rule in rules))

    def test_invalid_json_returns_bad_request(self) -> None:
        status, payload = self._request(
            "/api/v1/evaluate",
            method="POST",
            raw_body=b"{invalid json",
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "JSON inválido")

    def test_invalid_payload_type_returns_bad_request(self) -> None:
        status, payload = self._request(
            "/api/v1/evaluate",
            method="POST",
            payload={"mode": "openaq", "location_id": "abc"},
        )

        self.assertEqual(status, 400)
        self.assertIn("invalid literal for int()", payload["error"])

    def test_unknown_route_returns_not_found(self) -> None:
        status, payload = self._request("/api/v1/does-not-exist")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "Ruta no encontrada")


if __name__ == "__main__":
    unittest.main()
