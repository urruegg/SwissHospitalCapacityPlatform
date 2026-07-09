#!/usr/bin/env python3
"""Unit tests for the BVA medallion pure transforms (T3).

Dependency-free (Python 3 standard library only). Drives the transforms off a
small deterministic slice from ``bva_synth_focus`` so the Bronze → Silver → Gold
contract is exercised end-to-end without PySpark.

Run with::

    python3 -m unittest discover -s data-platform/notebooks/bva/tests
"""

import datetime as _dt
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.abspath(os.path.join(MODULE_DIR, "..", "..", "scripts"))
sys.path.insert(0, MODULE_DIR)
sys.path.insert(0, SCRIPTS_DIR)

import bva_transforms as T  # noqa: E402
import bva_synth_focus as bsf  # noqa: E402

FIXED_END = _dt.date(2026, 6, 30)


def _slice(days: int = 40):
    return bsf.generate_rows(seed=42, days=days, end_date=FIXED_END)


class SilverTests(unittest.TestCase):
    def setUp(self):
        self.focus = _slice()
        self.silver = T.to_silver(self.focus, ingest_utc="2026-06-30T02:00:00Z", source_seed=42)

    def test_silver_row_per_focus_row(self):
        self.assertEqual(len(self.silver), len(self.focus))

    def test_provenance_columns_present(self):
        for row in self.silver:
            self.assertEqual(row["_ingest_utc"], "2026-06-30T02:00:00Z")
            self.assertEqual(row["_source_seed"], 42)

    def test_keys_derived(self):
        row = self.silver[0]
        for key in ("date_key", "month_key", "service_key", "meter_key",
                    "resource_key", "env_key", "hospital_key", "capability_key"):
            self.assertIn(key, row)
            self.assertTrue(row[key])

    def test_sorted_stable(self):
        again = T.to_silver(self.focus, ingest_utc="2026-06-30T02:00:00Z", source_seed=42)
        self.assertEqual(
            json.dumps(self.silver, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )


class DimTests(unittest.TestCase):
    def setUp(self):
        self.focus = _slice()

    def test_dim_service_covers_all_services(self):
        dim = T.dim_service(self.focus)
        self.assertEqual(len(dim), len(bsf.SERVICES))
        self.assertEqual([d["service_key"] for d in dim], sorted(d["service_key"] for d in dim))

    def test_dim_environment(self):
        dim = T.dim_environment(self.focus)
        self.assertEqual({d["env_key"] for d in dim}, set(bsf.ENVIRONMENTS))

    def test_dim_hospital(self):
        dim = T.dim_hospital(self.focus)
        self.assertEqual({d["hospital_key"] for d in dim}, set(bsf.HOSPITALS))

    def test_dim_capability(self):
        dim = T.dim_capability(self.focus)
        self.assertTrue({d["capability_key"] for d in dim}.issubset(set(bsf.CAPABILITIES)))

    def test_dim_date_one_per_day(self):
        dim = T.dim_date(self.focus)
        self.assertEqual(len(dim), 40)
        self.assertEqual(dim[-1]["date_key"], FIXED_END.isoformat())

    def test_dim_exec_role_has_five_plus_board(self):
        dim = T.dim_exec_role()
        keys = {d["exec_role_key"] for d in dim}
        self.assertTrue({"CEO", "CFO", "CIO", "COO", "CTO", "BOARD"}.issubset(keys))


class FactTests(unittest.TestCase):
    def setUp(self):
        self.focus = _slice()
        self.silver = T.to_silver(self.focus, ingest_utc="2026-06-30T02:00:00Z", source_seed=42)

    def test_consumption_conserves_total_cost(self):
        fact = T.fact_azure_consumption(self.silver)
        focus_total = round(sum(float(r["EffectiveCost"]) for r in self.focus), 2)
        fact_total = round(sum(r["effective_cost"] for r in fact), 2)
        self.assertAlmostEqual(focus_total, fact_total, places=0)

    def test_budget_variance_sums_to_zero_per_env_capability(self):
        fact = T.fact_budget(self.silver)
        # Since plan == mean monthly actual, monthly variances cancel per (env, cap).
        by_ec = {}
        for row in fact:
            by_ec.setdefault((row["env_key"], row["capability_key"]), 0.0)
            by_ec[(row["env_key"], row["capability_key"])] += row["variance_cost"]
        for total in by_ec.values():
            self.assertAlmostEqual(total, 0.0, places=0)

    def test_value_realization_adoption_default_zero(self):
        fact = T.fact_value_realization(self.silver)
        self.assertTrue(all(r["adoption_count"] == 0 for r in fact))
        self.assertTrue(all(r["benefit_realized"] > 0 for r in fact))

    def test_value_realization_adoption_join(self):
        fact0 = T.fact_value_realization(self.silver)
        gk = (fact0[0]["capability_key"], fact0[0]["month_key"], fact0[0]["hospital_key"])
        fact1 = T.fact_value_realization(self.silver, adoption_index={gk: 17})
        joined = {(r["capability_key"], r["month_key"], r["hospital_key"]): r for r in fact1}
        self.assertEqual(joined[gk]["adoption_count"], 17)

    def test_facts_byte_stable(self):
        a = json.dumps(T.fact_azure_consumption(self.silver), sort_keys=True)
        b = json.dumps(T.fact_azure_consumption(self.silver), sort_keys=True)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
