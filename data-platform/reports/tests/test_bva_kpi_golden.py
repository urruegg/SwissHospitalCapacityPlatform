#!/usr/bin/env python3
"""Golden-value tests for the BVA KPI catalogue (Sprint 15 · T5).

The sandbox cannot evaluate DAX, so these tests validate the **semantics** of
every BVA KPI measure through the pure reference implementation in
``data-platform/notebooks/bva/bva_kpi.py`` (which the DAX in
``bva_measures.tmdl`` mirrors one-for-one — see
``docs/adr/0025-bva-kpi-catalog.md``).

They drive the KPIs off a deterministic synthetic slice from ``bva_synth_focus``
→ ``bva_transforms`` Gold facts and assert:

* every headline KPI from design spec §6 is present and finite,
* the cost calibration stays within the ROM band, and
* the internal identities the DAX relies on hold (ROI, cost-to-value, etc.).

Dependency-free (Python 3 standard library only). Run with::

    python3 -m unittest discover -s data-platform/reports/tests
"""

import datetime as _dt
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NB_DIR = os.path.join(REPO, "data-platform", "notebooks", "bva")
SCRIPTS_DIR = os.path.join(REPO, "data-platform", "scripts")
sys.path.insert(0, NB_DIR)
sys.path.insert(0, SCRIPTS_DIR)

import bva_kpi as K  # noqa: E402
import bva_synth_focus as bsf  # noqa: E402
import bva_transforms as T  # noqa: E402

FIXED_END = _dt.date(2026, 6, 30)


def _kpis(seed: int = 42, days: int = 90):
    focus = bsf.generate_rows(seed=seed, days=days, end_date=FIXED_END)
    silver = T.to_silver(focus, ingest_utc="2026-06-30T02:00:00Z", source_seed=seed)
    consumption = T.fact_azure_consumption(silver)
    budget = T.fact_budget(silver)
    value = T.fact_value_realization(silver)
    return K.compute_kpis(consumption, budget, value), (consumption, budget, value)


class KpiCatalogueTests(unittest.TestCase):
    def setUp(self):
        self.kpis, _ = _kpis()

    def test_all_headline_kpis_present_and_finite(self):
        for persona, names in K.HEADLINE_KPIS.items():
            for name in names:
                self.assertIn(name, self.kpis, f"{persona} headline {name} missing")
                self.assertTrue(math.isfinite(self.kpis[name]),
                                f"{persona} headline {name} not finite")

    def test_catalogue_has_at_least_twenty_measures(self):
        self.assertGreaterEqual(len(self.kpis), 20)

    def test_no_kpi_is_nan_or_inf(self):
        for name, value in self.kpis.items():
            self.assertTrue(math.isfinite(value), f"{name} is not finite")


class KpiIdentityTests(unittest.TestCase):
    def setUp(self):
        self.kpis, _ = _kpis()

    def test_cost_optimization_is_list_minus_effective(self):
        self.assertAlmostEqual(
            self.kpis["Cost Optimization Realized"],
            self.kpis["List Cost"] - self.kpis["Effective Cost"],
            places=2,
        )

    def test_net_value_3yr_is_triple_net_annual(self):
        self.assertAlmostEqual(
            self.kpis["Net Value Realized (3yr)"],
            self.kpis["Net Annual Benefit"] * 3.0,
            places=2,
        )

    def test_roi_matches_net_over_tco(self):
        self.assertAlmostEqual(
            self.kpis["ROI %"],
            self.kpis["Net Annual Benefit"] / self.kpis["Actual TCO (Annualized)"],
            places=6,
        )

    def test_annualized_tco_uses_months_in_scope(self):
        expected = self.kpis["Effective Cost"] / self.kpis["Months In Scope"] * 12.0
        self.assertAlmostEqual(self.kpis["Actual TCO (Annualized)"], expected, places=2)

    def test_benefit_realization_pct_positive(self):
        self.assertGreater(self.kpis["Benefit Realization %"], 0.0)

    def test_cost_to_value_below_one(self):
        # Synthetic benefit multipliers (3.5–7x) keep the platform value-positive.
        self.assertLess(self.kpis["Cost-to-Value Ratio"], 1.0)


class KpiCalibrationTests(unittest.TestCase):
    def test_annualized_tco_within_rom_band(self):
        # ROM baseline CHF 760k/yr ±15% (design spec / docs/BVA.md).
        low, high = 760_000 * 0.85, 760_000 * 1.15
        for seed in (1, 7, 42, 101, 999):
            kpis, _ = _kpis(seed=seed)
            self.assertTrue(
                low <= kpis["Actual TCO (Annualized)"] <= high,
                f"seed {seed}: TCO {kpis['Actual TCO (Annualized)']:.0f} out of band",
            )

    def test_deterministic_for_fixed_seed(self):
        a, _ = _kpis(seed=42)
        b, _ = _kpis(seed=42)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
