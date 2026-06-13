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


if __name__ == "__main__":
    unittest.main()
