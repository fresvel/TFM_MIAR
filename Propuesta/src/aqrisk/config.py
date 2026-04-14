from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


DEFAULT_ENV_FILENAME = ".env"
DEFAULT_MODE = "mock"
DEFAULT_OPENAQ_BASE_URL = "https://api.openaq.org/v3"
DEFAULT_LOOKBACK_HOURS = 24
DEFAULT_MIN_COVERAGE = 80.0
DEFAULT_HISTORY_PATH = "data/evaluations.jsonl"
DEFAULT_SCENARIO_ID = "urban_escalation"


class EnvironmentLoader:
    """Loads environment variables from a local dotenv file when present."""

    def __init__(self, env_filename: str = DEFAULT_ENV_FILENAME) -> None:
        """Initialize the loader with the dotenv filename to inspect.

        Args:
            env_filename: Name of the dotenv file to read from the current working
                directory.
        """
        self.env_path = Path(env_filename)

    def load(self) -> None:
        """Populate missing process environment variables from the dotenv file."""
        if not self.env_path.exists():
            return

        for line in self.env_path.read_text(encoding="utf-8").splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#") or "=" not in candidate:
                continue
            key, value = candidate.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    """Holds the runtime configuration used by CLI, API and pipeline."""

    mode: str = DEFAULT_MODE
    openaq_api_key: str | None = None
    openaq_base_url: str = DEFAULT_OPENAQ_BASE_URL
    openaq_location_id: int | None = None
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS
    min_coverage: float = DEFAULT_MIN_COVERAGE
    history_path: str = DEFAULT_HISTORY_PATH
    scenario_id: str = DEFAULT_SCENARIO_ID

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from OS environment variables and a local `.env` file."""
        EnvironmentLoader().load()
        location_id = os.getenv("OPENAQ_LOCATION_ID")
        return cls(
            openaq_api_key=os.getenv("OPENAQ_API_KEY"),
            openaq_base_url=os.getenv("OPENAQ_BASE_URL", DEFAULT_OPENAQ_BASE_URL),
            openaq_location_id=int(location_id) if location_id else None,
            lookback_hours=int(os.getenv("OPENAQ_LOOKBACK_HOURS", str(DEFAULT_LOOKBACK_HOURS))),
            min_coverage=float(os.getenv("OPENAQ_MIN_COVERAGE", str(DEFAULT_MIN_COVERAGE))),
            history_path=os.getenv("AQRISK_HISTORY_PATH", DEFAULT_HISTORY_PATH),
            scenario_id=os.getenv("AQRISK_SCENARIO_ID", DEFAULT_SCENARIO_ID),
        )
