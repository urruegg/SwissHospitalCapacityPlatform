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
    activate_surge_beds,
    compute_expected_impact,
    defer_elective_slots,
    divert_low_acuity_beds,
    expedite_discharge_beds,
    flex_staff_beds,
    rebalance_census_beds,
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
            {
                "expedite_discharge_beds",
                "divert_low_acuity_beds",
                "unblock_barrier_beds",
                "rebalance_census_beds",
                "defer_elective_slots",
                "flex_staff_beds",
                "activate_surge_beds",
            },
        )

    def test_expedite_discharge_beds_within_gap(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 6)
        self.assertIn("delta=min(n, occupied_beds)=6", result["assumptions"])

    def test_divert_low_acuity_beds_within_gap(self):
        gold = _gold()
        params = {"n": 3, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = divert_low_acuity_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 3)

    def test_expedite_discharge_beds_exceeds_over_capacity_gap_but_not_clipped(self):
        # Requested n (20) exceeds the over-capacity gap (116 - 100 = 16), but the
        # grounding rule no longer clips at the gap: it only clips at physically
        # occupied beds (116), so delta == n here.
        gold = _gold()
        params = {"n": 20, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertEqual(result["delta"], 20)

    def test_unblock_barrier_beds_within_gap(self):
        gold = _gold()
        params = {"barrier_type": "transport", "n": 4, "ward": "hcp:Ward/Medicine A"}
        result = unblock_barrier_beds(params, gold)
        self.assertEqual(result["metric"], "beds")
        self.assertEqual(result["delta"], 4)

    def test_unblock_barrier_beds_capped_by_physically_occupied_beds(self):
        # n (50) is still below the physically-occupied cap (116), so delta == n.
        gold = _gold()
        params = {"barrier_type": "transport", "n": 50, "ward": "hcp:Ward/Medicine A"}
        result = unblock_barrier_beds(params, gold)
        self.assertEqual(result["delta"], 50)

    def test_unblock_barrier_beds_capped_when_n_exceeds_occupied_beds(self):
        # n (200) exceeds the physically-occupied beds (116): the physical cap
        # still binds, so delta == occupied beds, not n.
        gold = _gold()
        params = {"barrier_type": "transport", "n": 200, "ward": "hcp:Ward/Medicine A"}
        result = unblock_barrier_beds(params, gold)
        self.assertEqual(result["delta"], 116)

    def test_expedite_discharge_beds_headline_case_below_100_percent(self):
        # Regression guard for the Sprint-26 golden-thread headline: a ward at
        # ~102% occupancy (bedCapacity=75, forecastOccupiedBeds=76) can now
        # recover the full requested n=6 beds (previously clipped to the
        # over-capacity gap of 1), enabling occupancy to drop below 100%.
        row = dict(MEDICINE_A_FORECAST_ROW)
        row["bedCapacity"] = 75
        row["forecastOccupiedBeds"] = 76
        gold = _gold(forecast_rows=[row], driver_rows=[])
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertEqual(result["delta"], 6)

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

    def test_forecast_row_missing_forecast_occupied_beds_raises(self):
        bad_row = dict(MEDICINE_A_FORECAST_ROW)
        del bad_row["forecastOccupiedBeds"]
        gold = _gold(forecast_rows=[bad_row])
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        with self.assertRaises(ValueError):
            expedite_discharge_beds(params, gold)

    def test_driver_context_assumption_format_is_pinned(self):
        gold = _gold()
        params = {"n": 6, "before": "08:00", "ward": "hcp:Ward/Medicine A"}
        result = expedite_discharge_beds(params, gold)
        self.assertIn("driver:forecast_admissions=+6", result["assumptions"])
        self.assertIn("driver:planned_discharges=-2", result["assumptions"])

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


class TestFanoutFormulas(unittest.TestCase):
    """Sprint 26 WS-B fan-out: role-specific metric labels over the same
    bed-relief grounding (delta = min(n, occupied_beds)). Each formula is pure
    and deterministic, and carries a role-meaningful ``metric`` + mechanism
    assumption while keeping ``delta`` a bed-relief magnitude so the
    coordination recompute stays intact."""

    def test_rebalance_census_beds(self):
        gold = _gold()
        params = {"n": 5, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = rebalance_census_beds(params, gold)
        self.assertEqual(result["metric"], "rebalanced_beds")
        self.assertEqual(result["delta"], 5)
        self.assertIn("mechanism=rebalance_census", result["assumptions"])
        self.assertIn("to_ward=hcp:Ward/Medicine B", result["assumptions"])

    def test_defer_elective_slots(self):
        gold = _gold()
        params = {"n": 4, "before": "07:00", "ward": "hcp:Ward/Medicine A"}
        result = defer_elective_slots(params, gold)
        self.assertEqual(result["metric"], "elective_slots")
        self.assertEqual(result["delta"], 4)
        self.assertIn("mechanism=defer_elective", result["assumptions"])
        self.assertIn("before=07:00", result["assumptions"])

    def test_flex_staff_beds(self):
        gold = _gold()
        params = {"n": 3, "shift": "night", "ward": "hcp:Ward/Medicine A"}
        result = flex_staff_beds(params, gold)
        self.assertEqual(result["metric"], "staffed_beds")
        self.assertEqual(result["delta"], 3)
        self.assertIn("mechanism=flex_staff", result["assumptions"])
        self.assertIn("shift=night", result["assumptions"])

    def test_activate_surge_beds(self):
        gold = _gold()
        params = {"n": 8, "scope": "cantonal", "ward": "hcp:Ward/Medicine A"}
        result = activate_surge_beds(params, gold)
        self.assertEqual(result["metric"], "surge_beds")
        self.assertEqual(result["delta"], 8)
        self.assertIn("mechanism=activate_surge", result["assumptions"])
        self.assertIn("scope=cantonal", result["assumptions"])

    def test_fanout_formulas_bound_by_occupied_beds(self):
        gold = _gold()
        params = {"n": 500, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = rebalance_census_beds(params, gold)
        # occupied beds in the fixture forecast row is 116.
        self.assertEqual(result["delta"], 116)

    def test_fanout_missing_required_param_raises(self):
        gold = _gold()
        # defer_elective_slots requires `before`.
        with self.assertRaises(ValueError):
            defer_elective_slots({"n": 4, "ward": "hcp:Ward/Medicine A"}, gold)

    def test_fanout_missing_n_raises(self):
        gold = _gold()
        with self.assertRaises(ValueError):
            flex_staff_beds({"shift": "day", "ward": "hcp:Ward/Medicine A"}, gold)

    def test_fanout_determinism(self):
        gold = _gold()
        params = {"n": 8, "scope": "cantonal", "ward": "hcp:Ward/Medicine A"}
        r1 = activate_surge_beds(copy.deepcopy(params), copy.deepcopy(gold))
        r2 = activate_surge_beds(copy.deepcopy(params), copy.deepcopy(gold))
        self.assertEqual(r1, r2)


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
        {
            "lever_id": "BMCA-REBALANCE-CENSUS",
            "impact_formula_ref": "rebalance_census_beds",
            "owner_role": "bmca",
        },
        {
            "lever_id": "ORSA-DEFER-ELECTIVE",
            "impact_formula_ref": "defer_elective_slots",
            "owner_role": "orsa",
        },
        {
            "lever_id": "SBA-FLEX-STAFF-BEDS",
            "impact_formula_ref": "flex_staff_beds",
            "owner_role": "sba",
        },
        {
            "lever_id": "CSA-ACTIVATE-SURGE",
            "impact_formula_ref": "activate_surge_beds",
            "owner_role": "csa",
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

    def test_resolver_rebalance_census(self):
        gold = _gold()
        params = {"n": 5, "to_ward": "hcp:Ward/Medicine B", "ward": "hcp:Ward/Medicine A"}
        result = compute_expected_impact(
            "BMCA-REBALANCE-CENSUS", params, gold, catalog=self.INJECTED_CATALOG
        )
        self.assertEqual(result["owner_role"], "bmca")
        self.assertEqual(result["metric"], "rebalanced_beds")
        self.assertEqual(result["delta"], 5)

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

    def test_real_catalog_resolves_fanout_levers(self):
        gold = _gold()
        cases = [
            ("BMCA-REBALANCE-CENSUS", {"n": 5, "to_ward": "hcp:Ward/Medicine B"}, "bmca", "rebalanced_beds"),
            ("ORSA-DEFER-ELECTIVE", {"n": 4, "before": "07:00"}, "orsa", "elective_slots"),
            ("SBA-FLEX-STAFF-BEDS", {"n": 3, "shift": "night"}, "sba", "staffed_beds"),
            ("CSA-ACTIVATE-SURGE", {"n": 8, "scope": "cantonal"}, "csa", "surge_beds"),
        ]
        for lever_id, params, owner, metric in cases:
            with self.subTest(lever_id=lever_id):
                params = dict(params, ward="hcp:Ward/Medicine A")
                result = compute_expected_impact(lever_id, params, gold)
                self.assertEqual(result["owner_role"], owner)
                self.assertEqual(result["metric"], metric)
                self.assertEqual(result["delta"], params["n"])


if __name__ == "__main__":
    unittest.main()
