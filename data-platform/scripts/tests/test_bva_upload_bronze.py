#!/usr/bin/env python3
"""Unit tests for the BVA Bronze upload planner (T2).

Dependency-free (Python 3 standard library only). Exercises the pure
:func:`plan_uploads` partition-walking logic against a real generated slice, so
the FOCUS partition path is preserved into ``Bronze/consumption/``. The live
OneLake REST layer (:func:`upload_file`) is not exercised here — it needs Azure
credentials and only runs inside the ``bva-sim-refresh`` workflow.

Run with::

    python3 -m unittest discover -s data-platform/scripts/tests
"""

import datetime as _dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bva_synth_focus as bsf  # noqa: E402
import bva_upload_bronze as bub  # noqa: E402

FIXED_END = _dt.date(2026, 6, 30)


class PlanUploadsTests(unittest.TestCase):
    def _make_slice(self, tmp: str, days: int = 3) -> list[str]:
        rows = bsf.generate_rows(seed=42, days=days, end_date=FIXED_END)
        return bsf.write_partitioned(rows, tmp, fmt="jsonl")

    def test_one_pair_per_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = self._make_slice(tmp, days=5)
            pairs = bub.plan_uploads(tmp)
            self.assertEqual(len(pairs), len(written))
            self.assertEqual(len(pairs), 5)

    def test_partition_path_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_slice(tmp, days=3)
            pairs = bub.plan_uploads(tmp)
            for _, rel in pairs:
                self.assertTrue(rel.startswith("BillingPeriod="), rel)
                self.assertIn("/ChargePeriodStart=", rel)
                self.assertTrue(rel.endswith("/part-00000.jsonl"), rel)

    def test_remote_paths_use_forward_slashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_slice(tmp, days=2)
            pairs = bub.plan_uploads(tmp)
            for _, rel in pairs:
                self.assertNotIn("\\", rel)

    def test_deterministic_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_slice(tmp, days=4)
            a = [rel for _, rel in bub.plan_uploads(tmp)]
            b = [rel for _, rel in bub.plan_uploads(tmp)]
            self.assertEqual(a, b)
            self.assertEqual(a, sorted(a))

    def test_local_paths_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_slice(tmp, days=2)
            for local, _ in bub.plan_uploads(tmp):
                self.assertTrue(os.path.isfile(local))

    def test_missing_dir_raises(self):
        with self.assertRaises(NotADirectoryError):
            bub.plan_uploads("/nonexistent/path/for/bva")

    def test_empty_dir_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                bub.plan_uploads(tmp)

    def test_dry_run_main_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_slice(tmp, days=2)
            rc = bub.main(["--src", tmp, "--dry-run"])
            self.assertEqual(rc, 0)


class RemoteUrlTests(unittest.TestCase):
    """The remote URL must be environment-parametrized so the same partition
    tree can be uploaded to SIT or PROD by passing the target coordinates."""

    def test_defaults_to_sit_constants(self):
        url = bub._remote_url(
            bub.WORKSPACE_ID, bub.LAKEHOUSE_ID,
            "Bronze/consumption", "BillingPeriod=2026-06/ChargePeriodStart=2026-06-30/part-00000.parquet",
        )
        self.assertIn(bub.WORKSPACE_ID, url)
        self.assertIn(bub.LAKEHOUSE_ID, url)
        self.assertTrue(url.startswith(bub.ONELAKE_HOST))
        self.assertIn("/Files/Bronze/consumption/", url)
        self.assertTrue(url.endswith("/part-00000.parquet"))

    def test_targets_given_prod_coordinates(self):
        prod_ws = "1c8408f4-6eb7-401f-aee9-77fe4c8a515e"
        prod_lh = "57bd6e02-5248-439c-9f31-16bf9ee83cb4"
        url = bub._remote_url(
            prod_ws, prod_lh, "Bronze/consumption",
            "BillingPeriod=2026-06/ChargePeriodStart=2026-06-30/part-00000.parquet",
        )
        self.assertIn(prod_ws, url)
        self.assertIn(prod_lh, url)
        self.assertNotIn(bub.WORKSPACE_ID, url)

    def test_forward_slashes_preserved(self):
        url = bub._remote_url("ws", "lh", "Bronze/consumption", "a=1/b=2/part-00000.parquet")
        self.assertNotIn("\\", url)
        self.assertIn("a=1/b=2/", url)


if __name__ == "__main__":
    unittest.main()
