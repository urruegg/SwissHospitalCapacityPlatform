#!/usr/bin/env python3
"""Tests for the Sprint 7 planning datasets generator."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generate_planning_datasets as gen  # noqa: E402
import validate_datasets as vd            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneratorOrganizationTests(unittest.TestCase):
    def test_default_two_organizations(self):
        cfg = gen.GeneratorConfig(seed=42)
        bundle = gen.build_bundle(cfg)
        self.assertEqual(len(bundle["organizations"]), 2)
        org_ids = [o["organizationId"] for o in bundle["organizations"]]
        self.assertIn("ORG-HIRSLANDEN", org_ids)
        self.assertIn("ORG-ZOLLIKERBERG", org_ids)


class GeneratorLocationTests(unittest.TestCase):
    def test_default_no_beds(self):
        cfg = gen.GeneratorConfig(seed=42)
        bundle = gen.build_bundle(cfg)
        beds = [l for l in bundle["locations"] if l["physicalType"] == "bd"]
        self.assertEqual(beds, [])

    def test_with_beds_emits_beds(self):
        cfg = gen.GeneratorConfig(seed=42, with_beds=True,
                                  sites_per_org=1, stations_per_site=2,
                                  beds_per_station=3)
        bundle = gen.build_bundle(cfg)
        beds = [l for l in bundle["locations"] if l["physicalType"] == "bd"]
        self.assertEqual(len(beds), 12)
        for b in beds:
            self.assertIn(b["operationalStatus"], list("UOHIKC"))

    def test_hierarchy_passes_validator(self):
        cfg = gen.GeneratorConfig(seed=42, with_beds=True)
        bundle = gen.build_bundle(cfg)
        report = vd.GateReport()
        vd.check_location_hierarchy(bundle["locations"], "ds", report)
        self.assertTrue(all(r.passed for r in report.results),
                        msg=[r.message for r in report.results if not r.passed])

    def test_deterministic_with_seed(self):
        a = gen.build_bundle(gen.GeneratorConfig(seed=42, with_beds=True))
        b = gen.build_bundle(gen.GeneratorConfig(seed=42, with_beds=True))
        self.assertEqual(a["locations"], b["locations"])


class GeneratorEncounterTests(unittest.TestCase):
    def test_default_encounter_count(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=50)
        bundle = gen.build_bundle(cfg)
        self.assertEqual(len(bundle["encounters"]), 50)

    def test_encounter_passes_lifecycle_check(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=20)
        bundle = gen.build_bundle(cfg)
        report = vd.GateReport()
        vd.check_encounter_lifecycle(bundle["encounters"], "ds", report)
        self.assertTrue(all(r.severity == "low" or r.passed
                            for r in report.results),
                        msg=[r.message for r in report.results if not r.passed])

    def test_acuity_distribution_weighted(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=1000)
        bundle = gen.build_bundle(cfg)
        counts = {"routine": 0, "urgent": 0, "asap": 0, "stat": 0}
        for e in bundle["encounters"]:
            counts[e["acuityBand"]] += 1
        self.assertGreater(counts["routine"], counts["urgent"])
        self.assertGreater(counts["urgent"], counts["asap"])
        self.assertGreater(counts["asap"], counts["stat"])

    def test_phi_denylist_clean(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=20)
        bundle = gen.build_bundle(cfg)
        report = vd.GateReport()
        vd.check_planning_phi_denylist(bundle["encounters"], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))


class RecommendationGeneratorTests(unittest.TestCase):
    def test_one_recommendation_per_encounter(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=30)
        bundle = gen.build_bundle(cfg)
        bundle["recommendations"] = gen.build_recommendations(cfg, bundle)
        self.assertEqual(len(bundle["recommendations"]), 30)

    def test_recommendations_pass_invariants(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=30)
        bundle = gen.build_bundle(cfg)
        bundle["recommendations"] = gen.build_recommendations(cfg, bundle)
        report = vd.GateReport()
        vd.check_recommendation_invariants(bundle["recommendations"], "ds", report)
        self.assertTrue(all(r.passed for r in report.results),
                        msg=[r.message for r in report.results if not r.passed])

    def test_recommendations_pass_cross_contract(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=20, with_beds=True,
                                  sites_per_org=1, stations_per_site=2,
                                  beds_per_station=3)
        bundle = gen.build_bundle(cfg)
        bundle["recommendations"] = gen.build_recommendations(cfg, bundle)
        report = vd.GateReport()
        vd.check_planning_cross_contract(bundle, report)
        self.assertTrue(all(r.passed for r in report.results),
                        msg=[r.message for r in report.results if not r.passed])

    def test_bed_recommended_when_with_beds(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=10, with_beds=True,
                                  sites_per_org=1, stations_per_site=2,
                                  beds_per_station=3)
        bundle = gen.build_bundle(cfg)
        bundle["recommendations"] = gen.build_recommendations(cfg, bundle)
        for rec in bundle["recommendations"]:
            for c in rec["candidates"]:
                self.assertIsNotNone(c["recommendedBedLocationId"])


class ManifestTests(unittest.TestCase):
    def test_manifest_lists_all_datasets(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=5)
        manifest = gen.build_manifest(cfg, gen.build_bundle(cfg))
        self.assertIn("seed", manifest)
        self.assertIn("counts", manifest)
        self.assertEqual(set(manifest["counts"].keys()),
                         {"organizations", "locations", "encounters",
                          "recommendations"})


if __name__ == "__main__":
    unittest.main()
