from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


class HistoryStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, *, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "recorded_at": datetime.now(UTC).isoformat(),
            "request": request,
            "summary": {
                "source": response["snapshot"]["source"],
                "location_id": response["snapshot"]["location_id"],
                "location_name": response["snapshot"]["location_name"],
                "coverage_global": response["snapshot"]["coverage_global"],
                "aqi_global": response["aqi"]["global_aqi"],
                "category": response["aqi"]["category"],
                "dominant_parameter": response["aqi"]["dominant_parameter"],
                "fuzzy_label": response["fuzzy"]["label"],
                "fuzzy_score": response["fuzzy"]["score"],
                "context_adjustments": response["context_adjustments"],
                "triggered_rules": response["fuzzy"]["triggered_rules"],
            },
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def list(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        items = [json.loads(line) for line in lines if line.strip()]
        return list(reversed(items[-limit:]))
