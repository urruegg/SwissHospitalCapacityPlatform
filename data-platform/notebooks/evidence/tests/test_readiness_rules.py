"""Golden regression + branch tests for the readiness scoring rules (design spec §6)."""

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_DIR = HERE.parent
FIXTURE = HERE / "fixtures" / "readiness_golden"

sys.path.insert(0, str(MODULE_DIR))
from readiness_rules import aggregate_readiness, score_readiness  # noqa: E402


def _load(name: str):
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


class TestReadinessRules(unittest.TestCase):
    def setUp(self):
        self.inp = _load("input.json")
        self.rows = score_readiness(self.inp["bom_items"], self.inp["availability"])

    def test_golden_readiness_regression(self):
        self.assertEqual(self.rows, _load("expected_readiness.json"))

    def test_golden_aggregate_regression(self):
        self.assertEqual(aggregate_readiness(self.rows), _load("expected_aggregate.json"))

    def test_byte_stable(self):
        a = json.dumps(score_readiness(self.inp["bom_items"], self.inp["availability"]), sort_keys=True)
        b = json.dumps(score_readiness(self.inp["bom_items"], self.inp["availability"]), sort_keys=True)
        self.assertEqual(a, b)

    def test_tshow_preview_is_showcase_only(self):
        by_key = {(r["bomId"], r["track"]): r for r in self.rows}
        iq = by_key[("bom-iq-ontology", "T-SHOW")]
        self.assertEqual(iq["status"], "Ready")
        self.assertTrue(iq["showcaseOnly"])
        self.assertEqual(iq["region"], "West Europe")

    def test_tprod_blocks_non_ga(self):
        by_key = {(r["bomId"], r["track"]): r for r in self.rows}
        iq = by_key[("bom-iq-ontology", "T-PROD")]
        self.assertEqual(iq["status"], "Blocked")
        self.assertIn("not GA", iq["blockingReason"])

    def test_dependency_preview_propagates_showcase_only(self):
        by_key = {(r["bomId"], r["track"]): r for r in self.rows}
        agent = by_key[("bom-data-agent", "T-SHOW")]
        self.assertEqual(agent["status"], "Ready")
        self.assertTrue(agent["showcaseOnly"])

    def test_unavailable_resource_blocked_tshow(self):
        by_key = {(r["bomId"], r["track"]): r for r in self.rows}
        orphan = by_key[("bom-orphan", "T-SHOW")]
        self.assertEqual(orphan["status"], "Blocked")
        self.assertIn("not available", orphan["blockingReason"])


if __name__ == "__main__":
    unittest.main()
