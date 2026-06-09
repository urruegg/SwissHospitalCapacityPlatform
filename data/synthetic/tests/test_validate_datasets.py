#!/usr/bin/env python3
"""Unit tests for the Sprint 6 synthesized-data validation gate.

Run with: ``python3 -m unittest discover -s data/synthetic/tests``
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_datasets as vd  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SchemaValidationTests(unittest.TestCase):
    def test_type_mismatch_reported(self):
        errors = vd.validate_schema(5, {"type": "string"}, "$")
        self.assertTrue(any("expected type 'string'" in e for e in errors))

    def test_enum_violation_reported(self):
        errors = vd.validate_schema("xx", {"type": "string", "enum": ["a", "b"]}, "$")
        self.assertTrue(any("not in enum" in e for e in errors))

    def test_pattern_violation_reported(self):
        errors = vd.validate_schema("bad", {"type": "string", "pattern": r"^ONB-"}, "$")
        self.assertTrue(any("does not match pattern" in e for e in errors))

    def test_additional_property_rejected(self):
        schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["a"],
            "properties": {"a": {"type": "string"}},
        }
        errors = vd.validate_schema({"a": "x", "name": "Jane"}, schema, "$")
        self.assertTrue(any("additional property 'name'" in e for e in errors))

    def test_missing_required_reported(self):
        schema = {"type": "object", "required": ["a"], "properties": {}}
        errors = vd.validate_schema({}, schema, "$")
        self.assertTrue(any("missing required property 'a'" in e for e in errors))

    def test_min_items_reported(self):
        schema = {"type": "array", "minItems": 1, "items": {"type": "string"}}
        errors = vd.validate_schema([], schema, "$")
        self.assertTrue(any("minItems" in e for e in errors))

    def test_numeric_bounds_reported(self):
        schema = {"type": "integer", "minimum": 0, "maximum": 10}
        self.assertTrue(vd.validate_schema(-1, schema, "$"))
        self.assertTrue(vd.validate_schema(11, schema, "$"))
        self.assertFalse(vd.validate_schema(5, schema, "$"))

    def test_date_format_validation(self):
        schema = {"type": "string", "format": "date"}
        self.assertFalse(vd.validate_schema("2026-06-09", schema, "$"))
        self.assertTrue(vd.validate_schema("2026-13-40", schema, "$"))


class MinimizationTests(unittest.TestCase):
    def test_forbidden_identifier_detected(self):
        report = vd.GateReport()
        vd.check_minimization([{"onboardingId": "ONB-X-1", "birthDate": "1990-01-01"}],
                              "ds", report)
        self.assertTrue(any(not r.passed and r.control_id == "CH-C01"
                            for r in report.results))

    def test_clean_record_passes(self):
        report = vd.GateReport()
        vd.check_minimization([{"onboardingId": "ONB-X-1", "ageBand": "40-64"}],
                              "ds", report)
        self.assertTrue(all(r.passed for r in report.results))


class CapacityInvariantTests(unittest.TestCase):
    def test_overcommit_detected(self):
        report = vd.GateReport()
        vd.check_capacity_invariants([{"capacityRecordId": "CAP-1",
                                       "bedsTotal": 5, "bedsAvailable": 9}], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_valid_capacity_passes(self):
        report = vd.GateReport()
        vd.check_capacity_invariants([{"capacityRecordId": "CAP-1",
                                       "bedsTotal": 9, "bedsAvailable": 5}], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))


class EndToEndTests(unittest.TestCase):
    def test_committed_datasets_pass(self):
        evidence, report = vd.run(ROOT)
        self.assertEqual(evidence["passFailSummary"]["result"], "pass",
                         msg=[f"{r.control_id}:{r.message}" for r in report.failures])
        self.assertEqual(evidence["passFailSummary"]["criticalFailures"], 0)

    def test_traceability_covers_mvp_controls(self):
        evidence, _ = vd.run(ROOT)
        coverage = evidence["controlCoverage"]
        for fr in ("FR-ONB-001", "FR-ONB-002", "FR-ONB-003"):
            self.assertIn(fr, coverage["fr"])
        self.assertIn("CH-C01", coverage["ch"])
        self.assertIn("NFR-MAINT-005", coverage["nfr"])


if __name__ == "__main__":
    unittest.main()
