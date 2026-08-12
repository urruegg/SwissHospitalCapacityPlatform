"""Deterministic synthetic Microsoft Web IQ result payload (no network).

Mirrors the shape a real Web IQ web/news grounding call would return, reduced to
the typed fields the parser consumes. Used in CI + demo (defaultMode: simulated);
the live binding is GA/credential-gated (see live_adapter.py).
"""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "query": "emerging hospital-relevant public-health events Switzerland",
        "results": [
            {
                "title": f"Regional respiratory-illness uptick reported (sim {seed:04d})",
                "uri": "https://example.invalid/webiq/news/respiratory-uptick",
                "publishedAt": "2026-08-12T06:00:00Z",
                "hazard": "outbreak",
                "cantons": ["ZH"],
                "confidence": 0.72,
                "snippet": "Local outlets report a rise in respiratory presentations "
                           "ahead of official surveillance.",
            }
        ],
    }
