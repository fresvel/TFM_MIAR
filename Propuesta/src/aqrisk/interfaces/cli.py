from __future__ import annotations

import argparse
import json
import sys

from aqrisk.application.pipeline import AirQualityRiskPipeline, PipelineError
from aqrisk.config import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AQRisk prototype")
    parser.add_argument("--mode", choices=["mock", "openaq"], default=None)
    parser.add_argument("--location-id", type=int, default=None)
    parser.add_argument("--lookback-hours", type=int, default=None)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings.from_env()
    if args.mode:
        settings.mode = args.mode
    if args.location_id:
        settings.openaq_location_id = args.location_id
    if args.lookback_hours:
        settings.lookback_hours = args.lookback_hours
    try:
        result = AirQualityRiskPipeline(settings).run()
    except PipelineError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    payload = result.to_dict()
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
