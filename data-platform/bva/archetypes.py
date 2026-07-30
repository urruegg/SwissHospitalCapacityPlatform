"""Synthetic BVA archetype constants for the deterministic what-if engine.

These CHF benchmarks are documented synthetic inputs for Sprint 33 WS-B. They
are intentionally transparent and deterministic so BVA arithmetic is never done
by an LLM. WS-A replaces these defaults with ``sm_bva`` Gold measures when the
semantic model wiring is available; until then, they are provisional planning
benchmarks aligned to the ROM band in docs/BVA.md.
"""
from __future__ import annotations

DISCOUNT_RATE = 0.05
OCCUPANCY_BASELINE = 0.85
ROM_BAND = 0.30

SCOPE_FACTOR = {
    "full": 1.0,
    "phased": 0.6,
    "pilot": 0.35,
}

ARCHETYPES = {
    "acute": {
        "base_onboarding_chf": 120_000.0,
        "onboarding_per_bed_chf": 280.0,
        "base_run_delta_chf": 90_000.0,
        "run_delta_per_bed_chf": 260.0,
        "benefit_per_bed_chf": 2_000.0,
    },
    "rehab": {
        "base_onboarding_chf": 72_000.0,
        "onboarding_per_bed_chf": 168.0,
        "base_run_delta_chf": 54_000.0,
        "run_delta_per_bed_chf": 156.0,
        "benefit_per_bed_chf": 1_200.0,
    },
    "spitex": {
        "base_onboarding_chf": 42_000.0,
        "onboarding_per_bed_chf": 98.0,
        "base_run_delta_chf": 31_500.0,
        "run_delta_per_bed_chf": 91.0,
        "benefit_per_bed_chf": 700.0,
    },
}
