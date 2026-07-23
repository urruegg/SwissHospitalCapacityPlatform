"""Deterministic synthetic raw payload for the swissgrid channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "events": [
            {
                "eventId": f"swissgrid-sim-{seed:04d}",
                "severity": "Severe",
                "cantons": ["ZH"],
                "time": "2026-07-23T00:00:00Z",
                "expires": "2026-07-24T00:00:00Z",
                "uri": "https://example.invalid/swissgrid/sim",
            }
        ]
    }
