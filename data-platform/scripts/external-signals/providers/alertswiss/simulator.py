"""Deterministic synthetic raw payload for the alertswiss channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "alerts": [
            {
                "identifier": f"alertswiss-sim-{seed:04d}",
                "hazard": "flood",
                "severity": "Severe",
                "certainty": "Likely",
                "urgency": "Expected",
                "cantons": ["BE"],
                "onset": "2026-07-23T00:00:00Z",
                "effective": "2026-07-23T00:00:00Z",
                "expires": "2026-07-24T00:00:00Z",
                "status": "Actual",
                "uri": "https://example.invalid/alertswiss/sim",
            }
        ]
    }
