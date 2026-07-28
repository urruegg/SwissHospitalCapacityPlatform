"""Sprint 31 DQA — deterministic trust-score unit tests (design Sec 6).

The trust score is a PURE function of its dimension inputs: same inputs always
produce the same score. No randomness, never an LLM estimate. Mirrors the
determinism guarantees of data-platform/decision/impact/compute_expected_impact.py.
"""
from __future__ import annotations

import copy
import unittest

from quality.trust_score import DIMENSIONS, MODEL_VERSION, trust_score


def _full(v: float) -> dict:
    return {d: v for d in DIMENSIONS}


class TestTrustScore(unittest.TestCase):
    def test_perfect_score_is_one(self):
        out = trust_score("staffing.skills", _full(1.0))
        self.assertEqual(out["score"], 1.0)
        self.assertEqual(out["contractId"], "DC-DQ-TRUSTSCORE-v1")
        self.assertEqual(out["modelVersion"], MODEL_VERSION)
        self.assertEqual(set(out["dimensions"]), set(DIMENSIONS))
        self.assertEqual(out["domain"], "staffing.skills")

    def test_equal_weights_average(self):
        dims = _full(0.5)
        dims["completeness"] = 1.0
        out = trust_score("staffing.skills", dims)
        # 7*0.5 + 1.0 = 4.5 over 8 dims = 0.5625
        self.assertAlmostEqual(out["score"], 0.5625, places=4)

    def test_custom_weights_are_honoured(self):
        dims = _full(0.0)
        dims["completeness"] = 1.0
        # Put all weight on completeness -> score is completeness value.
        weights = {d: (1.0 if d == "completeness" else 0.0) for d in DIMENSIONS}
        out = trust_score("d", dims, weights=weights)
        self.assertAlmostEqual(out["score"], 1.0, places=4)

    def test_decision_class_is_echoed(self):
        out = trust_score("d", _full(1.0), decision_class="crisis")
        self.assertEqual(out["decisionClass"], "crisis")

    def test_determinism(self):
        dims = _full(0.4)
        r1 = trust_score("d", copy.deepcopy(dims))
        r2 = trust_score("d", copy.deepcopy(dims))
        self.assertEqual(r1, r2)

    def test_missing_dimension_raises(self):
        dims = _full(1.0)
        del dims["provenance"]
        with self.assertRaises(ValueError):
            trust_score("d", dims)

    def test_out_of_range_raises(self):
        dims = _full(1.0)
        dims["validity"] = 1.5
        with self.assertRaises(ValueError):
            trust_score("d", dims)

    def test_bool_dimension_rejected(self):
        dims = _full(1.0)
        dims["validity"] = True
        with self.assertRaises(ValueError):
            trust_score("d", dims)

    def test_zero_total_weight_raises(self):
        weights = {d: 0.0 for d in DIMENSIONS}
        with self.assertRaises(ValueError):
            trust_score("d", _full(1.0), weights=weights)

    def test_partial_weights_raise(self):
        weights = {"completeness": 1.0}
        with self.assertRaises(ValueError):
            trust_score("d", _full(1.0), weights=weights)


if __name__ == "__main__":
    unittest.main()
