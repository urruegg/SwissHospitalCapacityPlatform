"""Deterministic bva.simulate calculation engine.

The engine is pure stdlib and clock-free by default. It returns the frozen
``BvaSimulationResult`` v1 shape without performing schema validation; the B2
contract tests own that boundary.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from .archetypes import (
    ARCHETYPES,
    DISCOUNT_RATE,
    OCCUPANCY_BASELINE,
    ROM_BAND,
    SCOPE_FACTOR,
)
from .models import BvaBaseline, HospitalDelta, InsufficientInputError

_DEFAULT_AS_OF = "2026-07-28T00:00:00Z"
_SUPPORTED_LANGUAGES = {"de", "en"}


def _safe_div(numerator: float, denominator: float) -> float:
    """DAX ``DIVIDE`` semantics: return 0.0 when the denominator is zero."""
    if not denominator:
        return 0.0
    return numerator / denominator


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_pct(value: float) -> float:
    return round(float(value), 1)


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "hospital"


def _validate(baseline: BvaBaseline, delta: HospitalDelta, language: str) -> None:
    if not delta.hospital_name or not delta.hospital_name.strip():
        raise InsufficientInputError("hospital_name must be provided")
    if not isinstance(delta.beds, int) or isinstance(delta.beds, bool) or delta.beds <= 0:
        raise InsufficientInputError("beds must be a positive integer")
    if delta.archetype not in ARCHETYPES:
        raise InsufficientInputError(
            f"archetype must be one of {sorted(ARCHETYPES)}, got {delta.archetype!r}"
        )
    if (
        not isinstance(delta.occupancy_target, (int, float))
        or isinstance(delta.occupancy_target, bool)
        or not 0.0 < float(delta.occupancy_target) <= 1.5
    ):
        raise InsufficientInputError("occupancy_target must be in (0, 1.5]")
    if delta.onboarding_scope not in SCOPE_FACTOR:
        raise InsufficientInputError(
            f"onboarding_scope must be one of {sorted(SCOPE_FACTOR)}, got {delta.onboarding_scope!r}"
        )
    if language not in _SUPPORTED_LANGUAGES:
        raise InsufficientInputError(f"language must be one of {sorted(_SUPPORTED_LANGUAGES)}")
    if baseline.hospitals < 1:
        raise InsufficientInputError("baseline.hospitals must be at least 1")


def _roi_pct(annual_benefit_chf: float, tco3y_chf: float) -> float:
    net3y_chf = 3.0 * annual_benefit_chf - tco3y_chf
    return _safe_div(net3y_chf, tco3y_chf) * 100.0


def _chunk(
    text: str,
    source_ref: str,
    as_of: str,
    language: str,
) -> dict[str, Any]:
    return {
        "classId": "C",
        "text": text,
        "citation": {
            "sourceRef": source_ref,
            "anchor": "bva.simulate",
        },
        "asOf": as_of,
        "liveness": "snapshot",
        "status": "requires-validation",
        "confidence": 0.72,
        "language": language,
    }


def simulate(
    baseline: BvaBaseline,
    delta: HospitalDelta,
    *,
    language: str = "en",
    as_of: str = _DEFAULT_AS_OF,
) -> dict[str, Any]:
    """Return a deterministic BVA simulation result for one hospital delta."""
    _validate(baseline, delta, language)

    archetype = ARCHETYPES[delta.archetype]
    scope_factor = SCOPE_FACTOR[delta.onboarding_scope]
    beds = float(delta.beds)

    onboarding_one_time_chf = (
        archetype["base_onboarding_chf"] + archetype["onboarding_per_bed_chf"] * beds
    ) * scope_factor
    annual_run_delta_chf = archetype["base_run_delta_chf"] + archetype["run_delta_per_bed_chf"] * beds
    occupancy_factor = float(delta.occupancy_target) / OCCUPANCY_BASELINE
    annual_benefit_chf = archetype["benefit_per_bed_chf"] * beds * occupancy_factor
    net_annual_chf = annual_benefit_chf - annual_run_delta_chf
    tco3y_chf = onboarding_one_time_chf + 3.0 * annual_run_delta_chf
    net3y_chf = 3.0 * annual_benefit_chf - tco3y_chf
    roi_pct = _safe_div(net3y_chf, tco3y_chf) * 100.0
    payback_months = 0.0
    if net_annual_chf > 0.0:
        payback_months = _safe_div(onboarding_one_time_chf, net_annual_chf) * 12.0
    npv_chf = (
        sum(net_annual_chf / (1.0 + DISCOUNT_RATE) ** year for year in range(1, 4))
        - onboarding_one_time_chf
    )

    sensitivity = {
        "low": _round_pct(_roi_pct(annual_benefit_chf * (1.0 - ROM_BAND), tco3y_chf)),
        "base": _round_pct(roi_pct),
        "high": _round_pct(_roi_pct(annual_benefit_chf * (1.0 + ROM_BAND), tco3y_chf)),
    }
    metrics = {
        "roiPct": _round_pct(roi_pct),
        "paybackMonths": round(payback_months, 1),
        "tco3yChf": _round_money(tco3y_chf),
        "npvChf": _round_money(npv_chf),
    }
    projection = {
        "hospitalName": delta.hospital_name,
        "archetype": delta.archetype,
        "onboardingOneTimeChf": _round_money(onboarding_one_time_chf),
        "annualRunDeltaChf": _round_money(annual_run_delta_chf),
        "annualBenefitChf": _round_money(annual_benefit_chf),
    }
    baseline_result = {
        "totalCostChf": _round_money(baseline.total_cost_chf),
        "oneTimeChf": _round_money(baseline.one_time_chf),
        "annualRunChf": _round_money(baseline.annual_run_chf),
        "hospitals": int(baseline.hospitals),
    }
    source_ref = (
        "docs/BVA.md ROM baseline; "
        f"archetype:{delta.archetype}; input:beds={delta.beds},scope={delta.onboarding_scope}"
    )
    text = (
        f"{delta.hospital_name} {delta.archetype} what-if: "
        f"3-year TCO CHF {metrics['tco3yChf']:.2f}, "
        f"ROI {metrics['roiPct']:.1f}%, "
        f"payback {metrics['paybackMonths']:.1f} months."
    )

    return {
        "scenarioId": f"sim-{_slug(delta.hospital_name)}-{delta.archetype}",
        "currency": "CHF",
        "asOf": as_of,
        "baseline": baseline_result,
        "projection": projection,
        "metrics": metrics,
        "sensitivity": sensitivity,
        "chunks": [_chunk(text, source_ref, as_of, language)],
    }
