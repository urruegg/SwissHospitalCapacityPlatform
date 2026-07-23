"""Deterministic synthetic raw payload for the meteoswiss channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "warnings": [
            {
                "warningId": f"meteoswiss-sim-{seed:04d}",
                "hazard": "heat",
                "dangerLevel": 4,
                "cantons": ["ZH"],
                "onset": "2026-07-23T00:00:00Z",
                "effective": "2026-07-23T00:00:00Z",
                "expires": "2026-07-24T00:00:00Z",
                "uri": "https://example.invalid/meteoswiss/sim",
            }
        ]
    }
