"""Sprint 16 T5 — golden fixtures for the CSA tier classifier (Lage doctrine)."""
from __future__ import annotations

import unittest

from _util import load_script


class TestTierClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_script("csa-tier-classifier.py")

    def classify(self, state):
        return self.mod.classify_tier(state)

    def test_normallage_is_tier1(self) -> None:
        state = {"resources": {"beds": {"utilization": 0.72, "shortfall": 0}}, "flags": {}}
        self.assertEqual(self.classify(state)["tier"], 1)

    def test_threshold_breach_is_tier2(self) -> None:
        state = {"resources": {"beds": {"utilization": 0.94, "shortfall": 0}}, "flags": {}}
        result = self.classify(state)
        self.assertEqual(result["tier"], 2)
        self.assertTrue(any("beds" in r for r in result["reasons"]))

    def test_boundary_exactly_at_threshold_is_tier2(self) -> None:
        state = {"resources": {"icu-beds": {"utilization": 0.90, "shortfall": 0}}, "flags": {}}
        self.assertEqual(self.classify(state)["tier"], 2)

    def test_capacity_exceeded_after_levers_is_tier3(self) -> None:
        state = {
            "resources": {"beds": {"utilization": 0.94, "shortfall": 12}},
            "flags": {"capacityExceededAfterLevers": True},
        }
        result = self.classify(state)
        self.assertEqual(result["tier"], 3)
        self.assertTrue(any("after internal levers" in r for r in result["reasons"]))

    def test_multi_canton_is_tier3(self) -> None:
        state = {"resources": {"beds": {"utilization": 0.5}}, "flags": {"multiCanton": True}}
        self.assertEqual(self.classify(state)["tier"], 3)

    def test_special_capability_overwhelmed_is_tier3(self) -> None:
        state = {"resources": {"ventilators": {"utilization": 1.1, "shortfall": 3}}, "flags": {}}
        result = self.classify(state)
        self.assertEqual(result["tier"], 3)
        self.assertTrue(any("special capability" in r for r in result["reasons"]))

    def test_burn_beds_shortfall_is_tier3(self) -> None:
        state = {"resources": {"burn-beds": {"utilization": 1.0, "shortfall": 4}}, "flags": {}}
        self.assertEqual(self.classify(state)["tier"], 3)

    def test_result_stamps_rules_version(self) -> None:
        state = {"resources": {}, "flags": {}}
        self.assertEqual(self.classify(state)["rulesVersion"], self.mod.RULES_VERSION)


if __name__ == "__main__":
    unittest.main()
