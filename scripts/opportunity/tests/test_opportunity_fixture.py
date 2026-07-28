"""Tests for the Backstage opportunity-pipeline app fixture."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.opportunity.build_opportunity_fixture import (
    DEFAULT_OUT,
    STAGE_WEIGHTS,
    build_dataset,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestOpportunityFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = build_dataset(REPO_ROOT)

    def test_pipeline_metrics_match_synthetic_dataset(self) -> None:
        pipeline = self.dataset["pipeline"]

        self.assertEqual(pipeline["total"], 7)
        self.assertEqual(pipeline["open"], 4)
        self.assertEqual(
            pipeline["statusCounts"],
            {
                "new": 1,
                "evaluating": 1,
                "qualified": 1,
                "onboarding": 1,
                "won": 1,
                "disqualified": 1,
                "lost": 1,
            },
        )
        self.assertEqual(pipeline["weightedRoiPct"], 35.93)
        self.assertEqual(pipeline["stageWeights"], STAGE_WEIGHTS)

    def test_opportunity_list_is_app_shaped_and_sorted(self) -> None:
        opportunities = self.dataset["opportunities"]

        self.assertEqual([row["id"] for row in opportunities], sorted(row["id"] for row in opportunities))
        self.assertEqual(
            set(opportunities[0]),
            {"id", "hospitalName", "archetype", "status", "language", "roiPct", "poVerdict", "latestEvent"},
        )
        self.assertIn(
            {
                "at": "2026-07-29T09:00:00Z",
                "event": "commercial approval recorded",
                "by": "account-team",
            },
            [row["latestEvent"] for row in opportunities],
        )

    def test_committed_fixture_matches_regen(self) -> None:
        committed = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))

        self.assertEqual(
            committed,
            self.dataset,
            "opportunity-demo.json is stale — run `python -m scripts.opportunity.build_opportunity_fixture`",
        )

    def test_byte_stable(self) -> None:
        second = build_dataset(REPO_ROOT)

        self.assertEqual(json.dumps(self.dataset, sort_keys=True), json.dumps(second, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
