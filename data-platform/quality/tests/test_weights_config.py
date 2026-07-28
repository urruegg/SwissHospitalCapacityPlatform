"""Sprint 31 DQA -- trust-score weights/thresholds config loader tests.

The loader is a PURE, stdlib-only reader of the git-tracked
``trustscore-weights.json`` source of truth (ADR-0053). No randomness, no
network, no clock -- same call always returns the same dict.
"""
from __future__ import annotations

import unittest

from quality.trust_score import DIMENSIONS, MODEL_VERSION, trust_score
from quality.weights_config import (
    config_model_version,
    load_profile,
    load_thresholds,
)


class TestLoadProfile(unittest.TestCase):
    def test_default_profile_covers_all_dimensions_and_is_positive(self):
        profile = load_profile("default")
        self.assertEqual(set(profile), set(DIMENSIONS))
        self.assertTrue(all(v > 0 for v in profile.values()))
        self.assertGreater(sum(profile.values()), 0.0)

    def test_default_profile_is_equal_weight(self):
        profile = load_profile("default")
        first = profile[DIMENSIONS[0]]
        for dim in DIMENSIONS:
            self.assertEqual(profile[dim], first)

    def test_none_and_unknown_class_fall_back_to_default(self):
        self.assertEqual(load_profile(None), load_profile("default"))
        self.assertEqual(load_profile("no-such-class"), load_profile("default"))

    def test_crisis_upweights_timeliness_completeness_provenance(self):
        profile = load_profile("crisis")
        self.assertEqual(set(profile), set(DIMENSIONS))
        for up in ("timeliness", "completeness", "provenance"):
            self.assertGreater(profile[up], profile["validity"])

    def test_planning_upweights_completeness_consistency_ontology(self):
        profile = load_profile("planning")
        for up in ("completeness", "consistency", "ontology_mapping"):
            self.assertGreater(profile[up], profile["validity"])

    def test_config_model_version_matches_module(self):
        self.assertEqual(config_model_version(), MODEL_VERSION)


class TestLoadThresholds(unittest.TestCase):
    def test_default_thresholds_shape_and_values(self):
        thr = load_thresholds("default")
        self.assertEqual(thr["overall"], 0.80)
        self.assertEqual(thr["gating"]["completeness"], 0.80)
        self.assertEqual(thr["gating"]["provenance"], 0.80)
        self.assertEqual(thr["gating"]["ontology_mapping"], 0.80)

    def test_crisis_thresholds_are_stricter_on_timeliness(self):
        thr = load_thresholds("crisis")
        self.assertEqual(thr["overall"], 0.85)
        self.assertEqual(thr["gating"]["timeliness"], 0.90)

    def test_planning_thresholds(self):
        thr = load_thresholds("planning")
        self.assertEqual(thr["overall"], 0.80)
        self.assertEqual(thr["gating"]["consistency"], 0.80)

    def test_none_and_unknown_class_fall_back_to_default(self):
        self.assertEqual(load_thresholds(None), load_thresholds("default"))
        self.assertEqual(load_thresholds("no-such-class"), load_thresholds("default"))

    def test_gating_dimensions_are_known_dimensions(self):
        for cls in ("default", "crisis", "planning"):
            for dim in load_thresholds(cls)["gating"]:
                self.assertIn(dim, DIMENSIONS)

    def test_thresholds_are_unit_interval(self):
        for cls in ("default", "crisis", "planning"):
            thr = load_thresholds(cls)
            self.assertTrue(0.0 <= thr["overall"] <= 1.0)
            self.assertTrue(all(0.0 <= v <= 1.0 for v in thr["gating"].values()))


class TestProfileDrivesTrustScore(unittest.TestCase):
    def test_default_profile_equals_module_default_score(self):
        dims = {d: 0.5 for d in DIMENSIONS}
        dims["completeness"] = 1.0
        with_config = trust_score("d", dims, weights=load_profile("default"))
        module_default = trust_score("d", dims)  # equal weights internally
        self.assertAlmostEqual(with_config["score"], module_default["score"], places=6)

    def test_crisis_profile_rewards_timeliness(self):
        # A domain strong on timeliness but weak elsewhere scores higher under
        # crisis weighting than under the equal-weight default.
        dims = {d: 0.2 for d in DIMENSIONS}
        dims["timeliness"] = 1.0
        crisis = trust_score("d", dims, weights=load_profile("crisis"))
        default = trust_score("d", dims, weights=load_profile("default"))
        self.assertGreater(crisis["score"], default["score"])

    def test_loaded_profile_is_accepted_by_trust_score_contract(self):
        out = trust_score("d", {x: 1.0 for x in DIMENSIONS}, weights=load_profile("planning"))
        self.assertEqual(out["contractId"], "DC-DQ-TRUSTSCORE-v1")
        self.assertEqual(out["score"], 1.0)


if __name__ == "__main__":
    unittest.main()
