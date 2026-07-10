#!/usr/bin/env python3
"""Structural tests for the evidence.SemanticModel (Sprint 14.1 · T4).

DAX cannot be evaluated in the sandbox, so these tests assert the TMDL structure
of the separate readiness model authored per ADR-0026 (Option B):

* both readiness Gold facts are present as Direct Lake tables,
* all five plan-Task-4 measures exist,
* the ``EvidenceReadOnly`` role exists and is referenced by the model, and
* the model does not touch the ``capacity-dashboard`` contract (isolation).

Dependency-free (Python 3 standard library only). Run with::

    python3 -m unittest discover -s data-platform/reports/tests
"""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.abspath(os.path.join(HERE, ".."))
MODEL = os.path.join(REPORTS, "evidence.SemanticModel", "definition")
TABLES = os.path.join(MODEL, "tables")

EXPECTED_MEASURES = {
    "BOM count",
    "Readiness % (T-SHOW)",
    "Readiness % (T-PROD)",
    "GA-Parity Gap",
    "Blocked requirements count",
}
EXPECTED_TABLES = {"fact_readiness_snapshot", "fact_readiness_summary"}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class EvidenceSemanticModel(unittest.TestCase):
    def test_model_references_both_facts_and_role(self):
        model = _read(os.path.join(MODEL, "model.tmdl"))
        for table in EXPECTED_TABLES:
            self.assertIn(f"ref table {table}", model)
        self.assertIn("ref role EvidenceReadOnly", model)

    def test_tables_exist_and_are_direct_lake_gold(self):
        for table in EXPECTED_TABLES:
            path = os.path.join(TABLES, f"{table}.tmdl")
            self.assertTrue(os.path.exists(path), f"missing {table}.tmdl")
            body = _read(path)
            self.assertIn("mode: directLake", body)
            self.assertIn("schemaName: gold", body)
            self.assertIn(f"[gold].[{table}]", body)

    def test_all_five_measures_present(self):
        snapshot = _read(os.path.join(TABLES, "fact_readiness_snapshot.tmdl"))
        found = set(re.findall(r"measure '([^']+)'", snapshot))
        self.assertEqual(EXPECTED_MEASURES, found)

    def test_readonly_role_has_no_row_filter(self):
        role = _read(os.path.join(MODEL, "roles", "EvidenceReadOnly.tmdl"))
        self.assertIn("modelPermission: read", role)
        # Synthetic non-PHI evidence (ADR-0016): no tablePermission row filters.
        self.assertNotIn("tablePermission", role)

    def test_isolated_from_capacity_dashboard(self):
        # ADR-0026 Option B: the evidence model must not reference capacity tables.
        model = _read(os.path.join(MODEL, "model.tmdl"))
        self.assertNotIn("fact_capacity_baseline", model)
        self.assertNotIn("bva_", model)


if __name__ == "__main__":
    unittest.main()
