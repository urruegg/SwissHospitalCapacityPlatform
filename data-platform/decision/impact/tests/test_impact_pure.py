"""Unit tests for the deterministic ``compute_expected_impact`` tool.

Dependency-light: the formula registry + resolver tests below use only the
standard library and injected fixtures (no PyYAML, no jsonschema, no Fabric).
A single optional test at the bottom resolves the real on-disk lever catalog
and is guarded by the repo's optional-import convention (see
``data-platform/scripts/csa/tests/test_scenarios.py``).
"""
from __future__ import annotations

import copy
import unittest

try:
    import yaml  # noqa: F401

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from impact.compute_expected_impact import (
    FORMULA_REGISTRY,
    compute_expected_impact,
    divert_low_acuity_beds,
    expedite_discharge_beds,
    unblock_barrier_beds,
)

MEDICINE_A_FORECAST_ROW = {
    "contractId": "DC-OCCUPANCY-FORECAST-v1",
    "forecastId": "OF-H-USZ-MEDICINE-A-20260724T00",
    "hospitalId": "H_USZ",
    "wardId": "hcp:Ward/Medicine A",
    "producedAt": "2026-07-24T00:00:00Z",
    "producedBy": "MRUN-FORESIGHT-SYNTH-V0-1",
    "modelVersion": "0.1.0",
    "horizonH": 72,
    "bucketStart": "2026-07-27T00:00:00Z",
    "bedCapacity": 100,
    "forecastOccupiedBeds": 116,
    "forecastOccupancyPct": 116.0,
    "lowerCi": 98.6,
    "upperCi": 133.4,
    "breach": True,
    "purposeTag": "capacity-planning",
    "dataResidencyRegion": "switzerlandnorth",
    "asOfTimestamp": "2026-07-24T00:00:00Z",
}

MEDICINE_A_DRIVER_ROWS = [
    {
        "contractId": "DC-FORECAST-DRIVER-v1",
        "forecastId": "OF-H-USZ-MEDICINE-A-20260724T00",
        "hospitalId": "H_USZ",
        "wardId": "hcp:Ward/Medicine A",
        "horizonH": 72,
        "factor": "forecast_admissions",
        "delta": 6.0,
        "note": "forecast admissions",
        "signalId": None,
        "purposeTag": "capacity-planning",
        "asOfTimestamp": "2026-07-24T00:00:00Z",
    },
    {
        "contractId": "DC-FORECAST-DRIVER-v1",
        "forecastId": "OF-H-USZ-MEDICINE-A-20260724T00",
        "hospitalId": "H_USZ",
        "wardId": "hcp:Ward/Medicine A",
        "horizonH": 72,
        "factor": "planned_discharges",
        "delta": -2.0,
        "note": "planned discharges",
        "signalId": None,
        "purposeTag": "capacity-planning",
        "asOfTimestamp": "2026-07-24T00:00:00Z",
    },
]


def _gold(forecast_rows=None, driver_rows=None):
    return {
        "forecast": forecast_rows if forecast_rows is not None else [MEDICINE_A_FORECAST_ROW],
        "drivers": driver_rows if driver_rows is not None else MEDICINE_A_DRIVER_ROWS,
    }


class TestFormulaRegistry(unittest.TestCase):
    """Formula-level tests: pure, deterministic, grounded in the gold forecast."""

    def test_registry_has_all_three_formulas(self):
        self.assertEqual(
            set(FORMULA_REGISTRY.keys()),
            {"expedite_discharge_beds", "divert_low_acuity_beds", "unblock_barrier_beds"},
        )

    def test_expedite_discharge_beds_within_gap(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 6)
        self.assertTrue(any("16" in a for a in result["assumptions"]))
        self.assertTrue(any("6" in a for a in result["assumptions"]))

    def test_divert_low_acuity_beds_within_gap(self):
        gold = _gold()
        params = {"n": 3, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = divert_low_acuity_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 3)

    def test_expedite_discharge_beds_capped_by_gap(self):
        gold = _gold()
        params = {"n": 20, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertEqual(result["delta"], 16)

    def test_unblock_barrier_beds_within_gap(self):
        gold = _gold()
        params = {"barrier_type": "transport", "n": 4, "ward": "hcp:Ward/Medicine A"}
        result = unblock_barrier_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 4)

    def test_unblock_barrier_beds_capped_by_gap(self):
        gold = _gold()
        params = {"barrier_type": "transport", "n": 50, "ward": "hcp:Ward/Medicine A"}
        result = unblock_barrier_beds(params, gold)
        self.assertEqual(result["delta"], 16)

    def test_determinism_expedite(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        r1 = expedite_discharge_beds(copy.deepcopy(params), copy.deepcopy(gold))
        r2 = expedite_discharge_beds(copy.deepcopy(params), copy.deepcopy(gold))
        self.assertEqual(r1, r2)

    def test_determinism_divert(self):
        gold = _gold()
        params = {"n": 3, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        r1 = divert_low_acuity_beds(copy.deepcopy(params), copy.deepcopy(gold))
        r2 = divert_low_acuity_beds(copy.deepcopy(params), copy.deepcopy(gold))
        self.assertEqual(r1, r2)

    def test_determinism_unblock(self):
        gold = _gold()
        params = {"barrier_type": "transport", "n": 4, "ward": "hcp:Ward/Medicine A"}
        r1 = unblock_barrier_beds(copy.deepcopy(params), copy.deepcopy(gold))
        r2 = unblock_barrier_beds(copy.deepcopy(params), copy.deepcopy(gold))
        self.assertEqual(r1, r2)

    def test_assumptions_mention_ward_and_horizon(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        joined = " ".join(result["assumptions"])
        self.assertIn("hcp:Ward/Medicine A", joined)
        self.assertIn("72", joined)

    def test_zero_matching_forecast_rows_raises(self):
        gold = _gold(forecast_rows=[])
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_multiple_matching_forecast_rows_raises(self):
        gold = _gold(forecast_rows=[MEDICINE_A_FORECAST_ROW, dict(MEDICINE_A_FORECAST_ROW)])
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_missing_ward_raises(self):
        gold = _gold(forecast_rows=[MEDICINE_A_FORECAST_ROW])
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/No Such Ward"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_missing_n_raises(self):
        gold = _gold()
        params = {"before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_zero_n_raises(self):
        gold = _gold()
        params = {"n": 0, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_negative_n_raises(self):
        gold = _gold()
        params = {"n": -2, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)


class TestResolver(unittest.TestCase):
    """Resolver tests using an injected catalog (dependency-light)."""

    INJECTED_CATALOG = [
        {
            "lever_id": "OOA-EXPEDITE-DISCHARGE",
            "impact_formula_ref": "expedite_discharge_beds",
            "owner_role": "dca",
        },
        {
            "lever_id": "OOA-DIVERT-LOW-ACUITY",
            "impact_formula_ref": "divert_low_acuity_beds",
            "owner_role": "bmca",
        },
        {
            "lever_id": "DCA-UNBLOCK-BARRIER",
            "impact_formula_ref": "unblock_barrier_beds",
            "owner_role": "dca",
        },
    ]

    def test_resolver_expedite_discharge(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = compute_expected_impact(
            "OOA-EXPEDITE-DISCHARGE", params, gold, catalog=self.INJECTED_CATALOG
        )
        self.assertEqual(result["owner_role"], "dca")
        self.assertEqual(result["lever_id"], "OOA-EXPEDITE-DISCHARGE")
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 6)
        self.assertIn("assumptions", result)

    def test_resolver_divert_low_acuity(self):
        gold = _gold()
        params = {"n": 3, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = compute_expected_impact(
            "OOA-DIVERT-LOW-ACUITY", params, gold, catalog=self.INJECTED_CATALOG
        )
        self.assertEqual(result["owner_role"], "bmca")
        self.assertEqual(result["delta"], 3)

    def test_resolver_unknown_lever_id_raises(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            compute_expected_impact("NO-SUCH-LEVER", params, gold, catalog=self.INJECTED_CATALOG)

    def test_resolver_unknown_formula_ref_raises(self):
        gold = _gold()
        catalog = [
            {"lever_id": "X-LEVER", "impact_formula_ref": "not_a_real_formula", "owner_role": "dca"}
        ]
        params = {"n": 6, "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            compute_expected_impact("X-LEVER", params, gold, catalog=catalog)

    def test_resolver_determinism(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        r1 = compute_expected_impact(
            "OOA-EXPEDITE-DISCHARGE", copy.deepcopy(params), copy.deepcopy(gold),
            catalog=copy.deepcopy(self.INJECTED_CATALOG),
        )
        r2 = compute_expected_impact(
            "OOA-EXPEDITE-DISCHARGE", copy.deepcopy(params), copy.deepcopy(gold),
            catalog=copy.deepcopy(self.INJECTED_CATALOG),
        )
        self.assertEqual(r1, r2)


@unittest.skipUnless(_HAS_YAML, "PyYAML not installed")
class TestResolverRealCatalog(unittest.TestCase):
    """Optional: resolve OOA-EXPEDITE-DISCHARGE from the real on-disk catalog."""

    def test_real_catalog_resolves_expedite_discharge(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = compute_expected_impact("OOA-EXPEDITE-DISCHARGE", params, gold)
        self.assertEqual(result["owner_role"], "dca")
        self.assertEqual(result["delta"], 6)

    def test_real_catalog_resolves_unblock_barrier(self):
        gold = _gold()
        params = {"barrier_type": "transport", "n": 4, "ward": "hcp:Ward/Medicine A"}
        result = compute_expected_impact("DCA-UNBLOCK-BARRIER", params, gold)
        self.assertEqual(result["owner_role"], "dca")
        self.assertEqual(result["delta"], 4)


if __name__ == "__main__":
    unittest.main()
