from __future__ import annotations

import argparse
import json

from contracts.demand_encounter import build_thin_demand_envelope


def emit_kickstart_once(profile_name: str = "baseline") -> str:
    envelope = build_thin_demand_envelope()
    envelope["simulationProfile"] = profile_name
    return json.dumps(envelope, separators=(",", ":"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit one simulator kickstart event envelope.")
    parser.add_argument("--profile", default="baseline", help="Simulation profile name")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    print(emit_kickstart_once(profile_name=args.profile))
