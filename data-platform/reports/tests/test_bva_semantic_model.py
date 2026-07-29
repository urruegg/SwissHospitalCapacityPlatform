#!/usr/bin/env python3
"""Structural tests for the sm_bva.SemanticModel (Sprint 33 WS-A · Step 3).

DAX cannot be evaluated in the sandbox, so these tests assert the TMDL structure
of the separate BVA cost-basis Direct Lake model (the ``sm_bva`` grounding
surface over the 5 ``gold.bva_*`` cost-basis tables, per
``docs/data-platform/bva-cost-gold-schema.md`` and ``bva-cost-gated-load-plan.md``
Step 3):

* all five cost-basis Gold facts/dims are present as Direct Lake tables,
* all six ``sm_bva`` measure-catalog measures exist,
* the ``BvaReadOnly`` role exists (read-only, no row filter — synthetic non-PHI),
  and is referenced by the model, and
* the model is isolated from the capacity-dashboard / consumption contracts.

Dependency-free (Python 3 standard library only). Run with::

    python3 -m unittest discover -s data-platform/reports/tests
"""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.abspath(os.path.join(HERE, ".."))
MODEL = os.path.join(REPORTS, "sm_bva.SemanticModel", "definition")
TABLES = os.path.join(MODEL, "tables")

EXPECTED_TABLES = {
    "bva_bom_dim",
    "bva_cost_fact",
    "bva_effort_fact",
    "bva_hospital_profile_dim",
    "bva_baseline_kpi",
}

EXPECTED_MEASURES = {
    "Total Cost CHF",
    "One-Time CHF",
    "Annual Run CHF",
    "Cost per Hospital CHF",
    "Cost per Bed CHF",
    "Cost per Forecast Run CHF",
}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class BvaSemanticModel(unittest.TestCase):
    def test_platform_publishes_as_sm_bva(self):
        platform = _read(os.path.join(REPORTS, "sm_bva.SemanticModel", ".platform"))
        self.assertIn('"type": "SemanticModel"', platform)
        self.assertIn('"displayName": "sm_bva"', platform)

    def test_model_references_all_tables_and_role(self):
        model = _read(os.path.join(MODEL, "model.tmdl"))
        for table in EXPECTED_TABLES:
            self.assertIn(f"ref table {table}", model)
        self.assertIn("ref role BvaReadOnly", model)

    def test_tables_exist_and_are_direct_lake_gold(self):
        for table in EXPECTED_TABLES:
            path = os.path.join(TABLES, f"{table}.tmdl")
            self.assertTrue(os.path.exists(path), f"missing {table}.tmdl")
            body = _read(path)
            self.assertIn("mode: directLake", body)
            self.assertIn("schemaName: gold", body)
            self.assertIn(f"[gold].[{table}]", body)

    def test_all_six_measures_present(self):
        kpi = _read(os.path.join(TABLES, "bva_baseline_kpi.tmdl"))
        found = set(re.findall(r"measure '([^']+)'", kpi))
        self.assertEqual(EXPECTED_MEASURES, found)

    def test_baseline_measures_select_from_baseline_kpi(self):
        kpi = _read(os.path.join(TABLES, "bva_baseline_kpi.tmdl"))
        # The three direct-select ROM measures must filter bva_baseline_kpi by metric_id.
        for metric in ("totalCostChf", "oneTimeChf", "annualRunChf", "costPerHospitalChf"):
            self.assertIn(metric, kpi, f"measure metric_id '{metric}' not selected")

    def test_readonly_role_has_no_row_filter(self):
        role = _read(os.path.join(MODEL, "roles", "BvaReadOnly.tmdl"))
        self.assertIn("modelPermission: read", role)
        # Synthetic non-PHI cost-basis (ADR-0016): no tablePermission row filters.
        self.assertNotIn("tablePermission", role)

    def test_direct_lake_expression_is_sit_pinned(self):
        # Repo is SIT-pinned; parameter.yml rewrites the OneLake path for PROD.
        expr = _read(os.path.join(MODEL, "expressions.tmdl"))
        self.assertIn("f3af9733-9503-4e92-98f9-a901d96f1c87", expr)  # SIT workspace
        self.assertIn("30594c20-46ba-40ea-91fa-4701b105e0b9", expr)  # SIT lakehouse

    def test_isolated_from_other_products(self):
        # Additive product: must not reference capacity or consumption contracts.
        model = _read(os.path.join(MODEL, "model.tmdl"))
        self.assertNotIn("fact_capacity_baseline", model)
        self.assertNotIn("bva_fact_azure_consumption", model)
        self.assertNotIn("bva_dim_", model)


if __name__ == "__main__":
    unittest.main()
