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


if __name__ == "__main__":
    unittest.main()
