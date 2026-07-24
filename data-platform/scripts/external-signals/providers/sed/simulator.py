"""Deterministic synthetic raw payload for the sed channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "events": [
            {
                "eventId": f"sed-sim-{seed:04d}",
                "magnitude": 5.4,
                "cantons": ["VS"],
                "time": "2026-07-23T00:00:00Z",
                "expires": "2026-07-24T00:00:00Z",
                "uri": "https://example.invalid/sed/sim",
            }
        ]
    }
