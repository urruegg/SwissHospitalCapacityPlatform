"""Deterministic unit tests for the BVA simulation engine."""
from __future__ import annotations

import math

import pytest

from bva.models import BvaBaseline, HospitalDelta, InsufficientInputError
from bva.simulate import simulate


def _expected_acute_full_320() -> dict[str, float]:
    beds = 320
    onboarding = (120_000.0 + 280.0 * beds) * 1.0
    annual_run = 90_000.0 + 260.0 * beds
    annual_benefit = 2_000.0 * beds * (0.85 / 0.85)
    net_annual = annual_benefit - annual_run
    tco3y = onboarding + 3.0 * annual_run
    net3y = 3.0 * annual_benefit - tco3y
    roi = (net3y / tco3y) * 100.0
    payback = (onboarding / net_annual) * 12.0
    npv = sum(net_annual / math.pow(1.05, year) for year in range(1, 4)) - onboarding
    return {
        "onboarding": round(onboarding, 2),
        "annual_run": round(annual_run, 2),
        "annual_benefit": round(annual_benefit, 2),
        "tco3y": round(tco3y, 2),
        "roi": round(roi, 1),
        "payback": round(payback, 1),
        "npv": round(npv, 2),
    }


def _delta(
    archetype: str = "acute",
    beds: int = 320,
    occupancy_target: float = 0.85,
    onboarding_scope: str = "full",
) -> HospitalDelta:
    return HospitalDelta(
        hospital_name="Kantonsspital Curavias",
        archetype=archetype,
        beds=beds,
        occupancy_target=occupancy_target,
        onboarding_scope=onboarding_scope,
    )


def test_canonical_acute_what_if_matches_independent_formula_values() -> None:
    result = simulate(BvaBaseline.rom_default(), _delta())
    expected = _expected_acute_full_320()

    assert result["scenarioId"] == "sim-kantonsspital-curavias-acute"
    assert result["currency"] == "CHF"
    assert result["asOf"] == "2026-07-28T00:00:00Z"
    assert result["baseline"] == {
        "totalCostChf": 2_550_000.0,
        "oneTimeChf": 1_300_000.0,
        "annualRunChf": 1_250_000.0,
        "hospitals": 3,
    }
    assert result["projection"]["hospitalName"] == "Kantonsspital Curavias"
    assert result["projection"]["archetype"] == "acute"
    assert result["projection"]["onboardingOneTimeChf"] == expected["onboarding"]
    assert result["projection"]["annualRunDeltaChf"] == expected["annual_run"]
    assert result["projection"]["annualBenefitChf"] == expected["annual_benefit"]
    assert result["metrics"]["tco3yChf"] == expected["tco3y"]
    assert result["metrics"]["roiPct"] == expected["roi"]
    assert result["metrics"]["paybackMonths"] == expected["payback"]
    assert result["metrics"]["npvChf"] == expected["npv"]
    assert result["chunks"][0]["citation"]["sourceRef"] == (
        "docs/BVA.md ROM baseline; archetype:acute; input:beds=320,occupancy=0.85,scope=full"
    )


def test_sensitivity_low_base_high_and_base_matches_metric_roi() -> None:
    result = simulate(BvaBaseline.rom_default(), _delta())

    sensitivity = result["sensitivity"]
    assert sensitivity["low"] < sensitivity["base"] < sensitivity["high"]
    assert sensitivity["base"] == result["metrics"]["roiPct"]


def test_pilot_scope_reduces_onboarding_against_full_scope() -> None:
    baseline = BvaBaseline.rom_default()

    full = simulate(baseline, _delta(onboarding_scope="full"))
    pilot = simulate(baseline, _delta(onboarding_scope="pilot"))

    assert pilot["projection"]["onboardingOneTimeChf"] < full["projection"]["onboardingOneTimeChf"]


@pytest.mark.parametrize(
    "bad_delta, expected_message",
    [
        (_delta(beds=0), "beds"),
        (_delta(beds=-10), "beds"),
        (_delta(archetype=""), "archetype"),
        (_delta(archetype="clinic"), "archetype"),
        (_delta(occupancy_target=0.0), "occupancy_target"),
        (_delta(onboarding_scope="unknown"), "onboarding_scope"),
    ],
)
def test_insufficient_input_error_names_bad_slot(
    bad_delta: HospitalDelta, expected_message: str
) -> None:
    with pytest.raises(InsufficientInputError, match=expected_message):
        simulate(BvaBaseline.rom_default(), bad_delta)


def test_archetype_scaling_orders_onboarding_for_identical_inputs() -> None:
    baseline = BvaBaseline.rom_default()
    acute = simulate(baseline, _delta(archetype="acute"))
    rehab = simulate(baseline, _delta(archetype="rehab"))
    spitex = simulate(baseline, _delta(archetype="spitex"))

    assert (
        acute["projection"]["onboardingOneTimeChf"]
        > rehab["projection"]["onboardingOneTimeChf"]
        > spitex["projection"]["onboardingOneTimeChf"]
    )
