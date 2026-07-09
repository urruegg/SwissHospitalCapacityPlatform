#!/usr/bin/env python3
"""Unit tests for the gated BVA medallion pipeline deploy helper (T3).

Exercises the pure plan + approval-gate logic. The live Fabric publish path is
not exercised (needs OIDC + Fabric).

Run with::

    python3 -m unittest discover -s data-platform/scripts/bva/tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import deploy_pipeline as dp  # noqa: E402


class BuildPlanTests(unittest.TestCase):
    def test_plan_is_medallion_ordered(self):
        plan = dp.build_plan()
        self.assertEqual([s["notebook"] for s in plan], list(dp.NOTEBOOK_ORDER))

    def test_first_step_has_no_dependency(self):
        plan = dp.build_plan()
        self.assertIsNone(plan[0]["depends_on"])

    def test_each_later_step_depends_on_previous(self):
        plan = dp.build_plan()
        for prev, cur in zip(plan, plan[1:]):
            self.assertEqual(cur["depends_on"], prev["notebook"])

    def test_bronze_before_silver_before_gold(self):
        order = [s["notebook"] for s in dp.build_plan()]
        self.assertLess(order.index("ingest_bronze_consumption"), order.index("build_silver_bva"))
        self.assertLess(order.index("build_silver_bva"), order.index("build_gold_bva_dims"))
        self.assertLess(order.index("build_gold_bva_dims"), order.index("build_gold_bva_facts"))


class ApprovalGateTests(unittest.TestCase):
    def test_human_handle_valid(self):
        self.assertTrue(dp.approval_is_valid("urruegg"))

    def test_empty_invalid(self):
        self.assertFalse(dp.approval_is_valid(None))
        self.assertFalse(dp.approval_is_valid(""))

    def test_bot_invalid(self):
        self.assertFalse(dp.approval_is_valid("github-actions[bot]"))
        self.assertFalse(dp.approval_is_valid("Copilot"))

    def test_dry_run_main_exits_zero(self):
        self.assertEqual(dp.main(["--dry-run"]), 0)

    def test_no_approver_is_dry_run(self):
        self.assertEqual(dp.main([]), 0)


if __name__ == "__main__":
    unittest.main()
