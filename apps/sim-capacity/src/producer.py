from __future__ import annotations

import json

from contracts.demand_encounter import build_thin_demand_envelope


def emit_once() -> str:
    envelope = build_thin_demand_envelope()
    return json.dumps(envelope, separators=(",", ":"))


if __name__ == "__main__":
    print(emit_once())
