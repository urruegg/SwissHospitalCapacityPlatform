#!/usr/bin/env python3
"""Unit tests for the Sprint 15 BVA synthetic FOCUS-shaped generator (T1).

Dependency-free (Python 3 standard library only), matching the repo convention
in ``data/synthetic/tests``. Run with::

    python3 -m unittest discover -s data-platform/scripts/tests
"""

import datetime as _dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bva_synth_focus as bsf  # noqa: E402


FIXED_END = _dt.date(2026, 6, 30)


class DeterminismTests(unittest.TestCase):
    def test_same_seed_identical_rows(self):
        a = bsf.generate_rows(seed=42, days=30, end_date=FIXED_END)
        b = bsf.generate_rows(seed=42, days=30, end_date=FIXED_END)
        self.assertEqual(a, b)

    def test_different_seed_differs(self):
        a = bsf.generate_rows(seed=42, days=30, end_date=FIXED_END)
        b = bsf.generate_rows(seed=7, days=30, end_date=FIXED_END)
        self.assertNotEqual(a, b)

    def test_serialized_output_byte_identical(self):
        rows = bsf.generate_rows(seed=42, days=10, end_date=FIXED_END)
        self.assertEqual(bsf._serialize_jsonl(rows), bsf._serialize_jsonl(rows))


class ShapeTests(unittest.TestCase):
    def setUp(self):
        self.schema = bsf.load_focus_schema()
        self.rows = bsf.generate_rows(seed=42, days=7, end_date=FIXED_END)

    def test_focus_shape_valid(self):
        errors = bsf.validate_focus_shape(self.rows, self.schema)
        self.assertEqual(errors, [], msg="; ".join(errors[:5]))

    def test_all_focus_columns_present(self):
        for row in self.rows:
            self.assertEqual(tuple(row.keys()), bsf.FOCUS_COLUMNS)

    def test_currency_fixed_chf(self):
        self.assertTrue(all(r["Currency"] == "CHF" for r in self.rows))

    def test_shape_detects_missing_column(self):
        broken = [dict(self.rows[0])]
        del broken[0]["EffectiveCost"]
        errors = bsf.validate_focus_shape(broken, self.schema)
        self.assertTrue(any("EffectiveCost" in e for e in errors))

    def test_partition_count_matches_days(self):
        partitions = bsf._rows_by_partition(bsf.generate_rows(seed=1, days=90, end_date=FIXED_END))
        self.assertEqual(len(partitions), 90)


class CalibrationTests(unittest.TestCase):
    def test_annualized_within_15pct(self):
        days = 90
        rows = bsf.generate_rows(seed=42, days=days, end_date=FIXED_END)
        annual = bsf.annualized_total(rows, days)
        lower = bsf.ROM_ANNUAL_AZURE_CHF * 0.85
        upper = bsf.ROM_ANNUAL_AZURE_CHF * 1.15
        self.assertGreaterEqual(annual, lower)
        self.assertLessEqual(annual, upper)

    def test_calibration_holds_across_seeds(self):
        days = 90
        for seed in (1, 7, 42, 99, 2026):
            rows = bsf.generate_rows(seed=seed, days=days, end_date=FIXED_END)
            annual = bsf.annualized_total(rows, days)
            self.assertGreaterEqual(annual, bsf.ROM_ANNUAL_AZURE_CHF * 0.85, msg=f"seed={seed}")
            self.assertLessEqual(annual, bsf.ROM_ANNUAL_AZURE_CHF * 1.15, msg=f"seed={seed}")


class CostDistributionTests(unittest.TestCase):
    def test_fabric_cosmos_container_apps_are_top3(self):
        rows = bsf.generate_rows(seed=42, days=90, end_date=FIXED_END)
        shares = bsf.service_cost_shares(rows)
        top3 = {name for name, _ in sorted(shares.items(), key=lambda kv: kv[1], reverse=True)[:3]}
        self.assertEqual(
            top3,
            {"Microsoft Fabric", "Azure Cosmos DB", "Azure Container Apps"},
        )

    def test_fabric_is_largest_share(self):
        rows = bsf.generate_rows(seed=42, days=90, end_date=FIXED_END)
        shares = bsf.service_cost_shares(rows)
        largest = max(shares.items(), key=lambda kv: kv[1])[0]
        self.assertEqual(largest, "Microsoft Fabric")

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(bsf._weight_sum(), 1.0, places=6)


class TagCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.rows = bsf.generate_rows(seed=42, days=14, end_date=FIXED_END)

    def test_no_null_tags(self):
        for row in self.rows:
            self.assertIn(row["x_env"], bsf.ENVIRONMENTS)
            self.assertIn(row["x_hospital"], bsf.HOSPITALS)
            self.assertIn(row["x_capability"], bsf.CAPABILITIES)

    def test_all_hospitals_present(self):
        self.assertEqual({r["x_hospital"] for r in self.rows}, set(bsf.HOSPITALS))

    def test_all_environments_present(self):
        self.assertEqual({r["x_env"] for r in self.rows}, set(bsf.ENVIRONMENTS))

    def test_all_capabilities_present(self):
        self.assertEqual({r["x_capability"] for r in self.rows}, set(bsf.CAPABILITIES))


class PartitioningTests(unittest.TestCase):
    def test_end_date_defaults_to_yesterday(self):
        rows = bsf.generate_rows(seed=42, days=3)
        yesterday = _dt.datetime.now(_dt.timezone.utc).date() - _dt.timedelta(days=1)
        latest = max(r["ChargePeriodStart"] for r in rows)
        self.assertEqual(latest, yesterday.isoformat())

    def test_invalid_days_rejected(self):
        with self.assertRaises(ValueError):
            bsf.generate_rows(seed=1, days=0)

    def test_write_partitioned_jsonl_roundtrip(self):
        rows = bsf.generate_rows(seed=42, days=5, end_date=FIXED_END)
        with tempfile.TemporaryDirectory() as tmp:
            written = bsf.write_partitioned(rows, tmp, fmt="jsonl")
            self.assertEqual(len(written), 5)
            for path in written:
                self.assertTrue(os.path.exists(path))
                self.assertTrue(path.endswith("part-00000.jsonl"))


class CliTests(unittest.TestCase):
    def test_dry_run_returns_zero(self):
        rc = bsf.main(["--seed", "42", "--days", "30", "--end-date", "2026-06-30"])
        self.assertEqual(rc, 0)

    def test_writes_90_partitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = bsf.main([
                "--seed", "42", "--days", "90", "--end-date", "2026-06-30",
                "--out-dir", tmp, "--format", "jsonl",
            ])
            self.assertEqual(rc, 0)
            billing_dirs = [d for d in os.listdir(tmp) if d.startswith("BillingPeriod=")]
            partition_count = sum(
                len(os.listdir(os.path.join(tmp, bd))) for bd in billing_dirs
            )
            self.assertEqual(partition_count, 90)


if __name__ == "__main__":
    unittest.main()
