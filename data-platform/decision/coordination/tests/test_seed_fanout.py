"""Unit tests for the Sprint 26 WS-B fan-out coordination seed.

Verifies that each of the four fanned-out roles (BMCA / ORSA / SBA / CSA) drives
a deterministic open -> propose -> HITL approve -> live-sync thread through the
same pure ``plan_runtime`` used by the OOA -> DCA Slice 1 seed, reusing the
role-agnostic ``plans`` / ``proposed_actions`` store surface. Dependency-light:
injected catalog + gold literals, no PyYAML / Cosmos / Fabric I/O.
"""
from __future__ import annotations

import unittest

from coordination.seed_fanout import FANOUT_THREADS, build_all_threads, build_role_thread


class TestFanoutSeedDeterminism(unittest.TestCase):
    def test_build_all_threads_is_deterministic(self):
        self.assertEqual(build_all_threads(), build_all_threads())

    def test_covers_all_four_fanout_roles(self):
        self.assertEqual(
            {t["role"] for t in FANOUT_THREADS},
            {"bmca", "orsa", "sba", "csa"},
        )


class TestFanoutSeedRecompute(unittest.TestCase):
    def test_each_role_recomputes_below_baseline(self):
        results = build_all_threads()
        self.assertEqual(set(results), {"bmca", "orsa", "sba", "csa"})
        for role, plan in results.items():
            with self.subTest(role=role):
                # Every thread breaches at open and drops below its baseline
                # after the single HITL-approved lever is applied.
                self.assertGreater(plan["baseline_pct"], 100, msg=role)
                self.assertLess(plan["current_pct"], plan["baseline_pct"], msg=role)
                self.assertEqual(len(plan["forecast_deltas"]), 1, msg=role)
                applied = plan["forecast_deltas"][0]
                self.assertGreater(applied["delta"], 0, msg=role)
                self.assertEqual(applied["resulting_pct"], plan["current_pct"], msg=role)

    def test_expected_headline_percentages(self):
        results = build_all_threads()
        self.assertEqual(results["bmca"]["baseline_pct"], 105)
        self.assertEqual(results["bmca"]["current_pct"], 97)
        self.assertEqual(results["orsa"]["baseline_pct"], 105)
        self.assertEqual(results["orsa"]["current_pct"], 95)
        self.assertEqual(results["sba"]["baseline_pct"], 104)
        self.assertEqual(results["sba"]["current_pct"], 98)
        self.assertEqual(results["csa"]["baseline_pct"], 120)
        self.assertEqual(results["csa"]["current_pct"], 80)

    def test_self_owned_levers_record_no_handoff(self):
        results = build_all_threads()
        for role, plan in results.items():
            with self.subTest(role=role):
                self.assertEqual(plan["handoffs"], [], msg=role)

    def test_build_role_thread_rejects_unknown_role(self):
        with self.assertRaises(KeyError):
            build_role_thread("no-such-role")


if __name__ == "__main__":
    unittest.main()
