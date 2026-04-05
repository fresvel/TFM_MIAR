from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    mode: str = "mock"
    openaq_api_key: str | None = None
    openaq_base_url: str = "https://api.openaq.org/v3"
    openaq_location_id: int | None = None
    lookback_hours: int = 24
    min_coverage: float = 80.0
    history_path: str = "data/evaluations.jsonl"
    scenario_id: str = "urban_escalation"

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv()
        location_id = os.getenv("OPENAQ_LOCATION_ID")
        return cls(
            openaq_api_key=os.getenv("OPENAQ_API_KEY"),
            openaq_base_url=os.getenv("OPENAQ_BASE_URL", "https://api.openaq.org/v3"),
            openaq_location_id=int(location_id) if location_id else None,
            lookback_hours=int(os.getenv("OPENAQ_LOOKBACK_HOURS", "24")),
            min_coverage=float(os.getenv("OPENAQ_MIN_COVERAGE", "80")),
            history_path=os.getenv("AQRISK_HISTORY_PATH", "data/evaluations.jsonl"),
        )
