#!/usr/bin/env python3
"""Structural tests for the BVA boardroom report + RLS (Sprint 15 · T6).

DAX/RLS cannot be evaluated in the sandbox, so these tests assert the PBIR
structure instead:

* every card visual binds a measure that actually exists in ``bva_measures.tmdl``,
* the report has the six expected pages (Board summary + 5 C-suite),
* the two BVA RLS roles exist and are referenced by the model, and
* the report connects to the semantic model that hosts the ``bva_`` tables.

Dependency-free (Python 3 standard library only). Run with::

    python3 -m unittest discover -s data-platform/reports/tests
"""

import glob
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.abspath(os.path.join(HERE, ".."))
MODEL = os.path.join(REPORTS, "capacity-dashboard.SemanticModel", "definition")
REPORT = os.path.join(REPORTS, "bva-boardroom.Report")
MEASURES_TMDL = os.path.join(MODEL, "tables", "bva_measures.tmdl")

EXPECTED_PAGES = {"board", "ceo", "cfo", "cio", "coo", "cto"}
BVA_ROLES = {"BvaExecFull", "BvaBoardReadOnly"}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _measure_names():
    return set(re.findall(r"measure '([^']+)'", _read(MEASURES_TMDL)))


def _card_measures():
    used = []
    for vf in glob.glob(os.path.join(REPORT, "definition", "pages", "*", "visuals", "*", "visual.json")):
        v = _load(vf)
        vis = v.get("visual", {})
        if vis.get("visualType") != "card":
            continue
        for proj in vis["query"]["queryState"]["Values"]["projections"]:
            field = proj.get("field", {})
            if "Measure" in field:
                used.append((vf, field["Measure"]["Property"]))
    return used


class ReportStructureTests(unittest.TestCase):
    def test_all_json_parses(self):
        files = glob.glob(os.path.join(REPORT, "**", "*.json"), recursive=True)
        files += [os.path.join(REPORT, "definition.pbir"), os.path.join(REPORT, ".platform")]
        for f in files:
            _load(f)

    def test_six_expected_pages(self):
        pages = {
            _load(p)["name"]
            for p in glob.glob(os.path.join(REPORT, "definition", "pages", "*", "page.json"))
        }
        self.assertEqual(pages, EXPECTED_PAGES)

    def test_pages_json_order_matches_pages(self):
        meta = _load(os.path.join(REPORT, "definition", "pages", "pages.json"))
        self.assertEqual(set(meta["pageOrder"]), EXPECTED_PAGES)
        self.assertIn(meta["activePageName"], EXPECTED_PAGES)

    def test_report_connects_to_capacity_model(self):
        pbir = _load(os.path.join(REPORT, "definition.pbir"))
        conn = pbir["datasetReference"]["byConnection"]["connectionString"]
        self.assertIn("semanticmodelid=", conn)


class MeasureBindingTests(unittest.TestCase):
    def test_every_card_measure_exists_in_model(self):
        names = _measure_names()
        self.assertGreaterEqual(len(names), 20)
        for vf, measure in _card_measures():
            self.assertIn(measure, names, f"{vf} binds unknown measure {measure!r}")

    def test_report_has_card_visuals(self):
        self.assertGreater(len(_card_measures()), 0)


class RlsRoleTests(unittest.TestCase):
    def test_bva_roles_exist_on_disk(self):
        for role in BVA_ROLES:
            self.assertTrue(
                os.path.exists(os.path.join(MODEL, "roles", f"{role}.tmdl")),
                f"missing role file {role}.tmdl",
            )

    def test_bva_roles_referenced_by_model(self):
        model = _read(os.path.join(MODEL, "model.tmdl"))
        for role in BVA_ROLES:
            self.assertIn(f"ref role {role}", model)

    def test_board_readonly_restricts_hospital_to_aggregated(self):
        text = _read(os.path.join(MODEL, "roles", "BvaBoardReadOnly.tmdl"))
        self.assertIn("bva_dim_hospital", text)
        self.assertIn('"Aggregated"', text)


if __name__ == "__main__":
    unittest.main()
