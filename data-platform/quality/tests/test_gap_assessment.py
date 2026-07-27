"""Sprint 31 DQA — gap assessment + newSourceNeeded seam unit tests.

Deterministic: each below-threshold dimension yields exactly one DC-DQ-GAP-v1
finding; the ``newSourceNeeded`` flag on a mapped domain is the frozen seam
Sprint 32 SGA consumes (design Sec 8). No randomness, never an LLM estimate.
"""
from __future__ import annotations

import copy
import unittest

from quality.gap_assessment import assess_gaps


IMPACT_MAP = {
    "staffing.skills": {
        "impactedKpi": ["skills-based-assignment", "forecast-accuracy"],
        "impactedAgents": ["sba-agent"],
        "recommendedSource": {"kind": "certification-register", "example": "NAREG / FMH"},
        "newSourceNeeded": True,
        "owner": "data-owner:staffing",
        "effort": "M",
    },
}
THRESHOLDS = {"completeness": 0.8, "timeliness": 0.8, "validity": 0.8}


class TestGapAssessment(unittest.TestCase):
    def test_below_threshold_dimension_yields_a_gap(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={"completeness": 0.4, "timeliness": 0.9, "validity": 0.95},
            thresholds=THRESHOLDS,
            impact_map=IMPACT_MAP,
        )
        self.assertEqual(len(gaps), 1)
        gap = gaps[0]
        self.assertEqual(gap["contractId"], "DC-DQ-GAP-v1")
        self.assertEqual(gap["dimension"], "completeness")
        self.assertEqual(gap["domain"], "staffing.skills")
        self.assertIs(gap["newSourceNeeded"], True)
        self.assertIn("sba-agent", gap["impactedAgents"])
        self.assertEqual(gap["owner"], "data-owner:staffing")
        self.assertEqual(gap["status"], "open")
        self.assertTrue(gap["gapId"].startswith("GAP-"))
        self.assertGreaterEqual(gap["impactScore"], 0.0)
        self.assertLessEqual(gap["impactScore"], 1.0)

    def test_impact_score_is_normalised_shortfall(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={"completeness": 0.4},
            thresholds={"completeness": 0.8},
            impact_map=IMPACT_MAP,
        )
        # (0.8 - 0.4) / 0.8 = 0.5
        self.assertAlmostEqual(gaps[0]["impactScore"], 0.5, places=4)

    def test_all_above_threshold_yields_no_gap(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={"completeness": 0.95, "timeliness": 0.9, "validity": 0.95},
            thresholds=THRESHOLDS,
            impact_map=IMPACT_MAP,
        )
        self.assertEqual(gaps, [])

    def test_multiple_below_threshold_dimensions_sorted_deterministically(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={"completeness": 0.4, "timeliness": 0.5, "validity": 0.95},
            thresholds=THRESHOLDS,
            impact_map=IMPACT_MAP,
        )
        # completeness + timeliness are below threshold; sorted by dimension name.
        self.assertEqual([g["dimension"] for g in gaps], ["completeness", "timeliness"])

    def test_unknown_domain_defaults_to_no_source_needed(self):
        gaps = assess_gaps(
            "unmapped.domain",
            metrics={"completeness": 0.1},
            thresholds={"completeness": 0.8},
            impact_map=IMPACT_MAP,
        )
        self.assertEqual(len(gaps), 1)
        self.assertIs(gaps[0]["newSourceNeeded"], False)
        self.assertEqual(gaps[0]["impactedAgents"], [])
        # Owner defaults to the domain's top-level segment.
        self.assertEqual(gaps[0]["owner"], "data-owner:unmapped")

    def test_missing_metric_is_treated_as_a_gap(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={},  # completeness absent -> treated as below threshold
            thresholds={"completeness": 0.8},
            impact_map=IMPACT_MAP,
        )
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["dimension"], "completeness")
        self.assertAlmostEqual(gaps[0]["impactScore"], 1.0, places=4)

    def test_gap_id_is_stable_and_deterministic(self):
        args = ("staffing.skills", {"completeness": 0.4}, {"completeness": 0.8})
        g1 = assess_gaps(*copy.deepcopy(args), impact_map=IMPACT_MAP)
        g2 = assess_gaps(*copy.deepcopy(args), impact_map=IMPACT_MAP)
        self.assertEqual(g1, g2)
        self.assertEqual(g1[0]["gapId"], g2[0]["gapId"])

    def test_no_impact_map_still_produces_gaps(self):
        gaps = assess_gaps(
            "staffing.skills",
            metrics={"completeness": 0.4},
            thresholds={"completeness": 0.8},
        )
        self.assertEqual(len(gaps), 1)
        self.assertIs(gaps[0]["newSourceNeeded"], False)


if __name__ == "__main__":
    unittest.main()
