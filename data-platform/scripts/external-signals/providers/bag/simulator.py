"""Deterministic synthetic raw payload for the bag channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "reports": [
            {
                "reportId": f"bag-sim-{seed:04d}",
                "indicator": "rsv",
                "incidencePer100k": 90.0,
                "thresholdPer100k": 30.0,
                "cantons": ["ZH"],
                "publishedAt": "2026-07-23T00:00:00Z",
                "weekStart": "2026-07-20",
                "uri": "https://example.invalid/bag/sim",
            }
        ]
    }
