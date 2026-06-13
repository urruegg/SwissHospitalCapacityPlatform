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

    def test_nullable_type_accepts_null(self):
        schema = {"type": ["string", "null"]}
        self.assertFalse(vd.validate_schema(None, schema, "$"))
        self.assertFalse(vd.validate_schema("ok", schema, "$"))

    def test_nullable_type_rejects_other_types(self):
        schema = {"type": ["string", "null"]}
        errors = vd.validate_schema(5, schema, "$")
        self.assertTrue(any("expected type" in e for e in errors))

    def test_date_time_format_validation(self):
        schema = {"type": "string", "format": "date-time"}
        self.assertFalse(vd.validate_schema("2026-06-12T14:32:00Z", schema, "$"))
        self.assertFalse(vd.validate_schema("2026-06-12T14:32:00.123Z", schema, "$"))
        # Non-UTC offsets and missing 'T'/'Z' must be rejected.
        self.assertTrue(vd.validate_schema("2026-06-12 14:32:00Z", schema, "$"))
        self.assertTrue(vd.validate_schema("2026-06-12T14:32:00+02:00", schema, "$"))
        self.assertTrue(vd.validate_schema("not-a-timestamp", schema, "$"))


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


class PurposeTagPolicyTests(unittest.TestCase):
    def test_undeclared_purpose_tag_detected(self):
        report = vd.GateReport()
        data = {"purposeTags": ["capacity-planning"]}
        vd.check_purpose_tags(data, [{"onboardingId": "ONB-1", "purposeTag": "marketing"}],
                              "ds", report)
        self.assertTrue(any(not r.passed and r.control_id == "NFR-COMP-011"
                            for r in report.results))

    def test_missing_minimization_marker_detected(self):
        report = vd.GateReport()
        data = {"purposeTags": ["capacity-planning"]}
        vd.check_purpose_tags(
            data,
            [{"onboardingId": "ONB-1", "purposeTag": "capacity-planning",
              "minimizationReviewed": False}],
            "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_compliant_records_pass(self):
        report = vd.GateReport()
        data = {"purposeTags": ["capacity-planning", "bed-management"]}
        vd.check_purpose_tags(
            data,
            [{"onboardingId": "ONB-1", "purposeTag": "bed-management",
              "minimizationReviewed": True}],
            "ds", report)
        self.assertTrue(all(r.passed for r in report.results))


class SpecialtyMetadataTests(unittest.TestCase):
    def test_taxonomy_version_mismatch_detected(self):
        report = vd.GateReport()
        data = {"specialtyTaxonomyVersion": "9.9.9"}
        vd.check_specialty_metadata(data, [], "ds", "1.0.0", report)
        self.assertTrue(any(not r.passed and r.control_id == "NFR-DQ-005"
                            for r in report.results))

    def test_specialty_not_in_tags_detected(self):
        report = vd.GateReport()
        data = {"specialtyTaxonomyVersion": "1.0.0"}
        vd.check_specialty_metadata(
            data,
            [{"capacityRecordId": "CAP-1", "specialty": "cardiology",
              "specialtyTags": ["surgery"]}],
            "ds", "1.0.0", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_duplicate_tags_detected(self):
        report = vd.GateReport()
        data = {"specialtyTaxonomyVersion": "1.0.0"}
        vd.check_specialty_metadata(
            data,
            [{"capacityRecordId": "CAP-1", "specialty": "cardiology",
              "specialtyTags": ["cardiology", "cardiology"]}],
            "ds", "1.0.0", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_valid_specialty_metadata_passes(self):
        report = vd.GateReport()
        data = {"specialtyTaxonomyVersion": "1.0.0"}
        vd.check_specialty_metadata(
            data,
            [{"capacityRecordId": "CAP-1", "specialty": "cardiology",
              "specialtyTags": ["cardiology", "acute-coronary"]}],
            "ds", "1.0.0", report)
        self.assertTrue(all(r.passed for r in report.results))


class TenantBoundaryTests(unittest.TestCase):
    def test_dataset_provider_mismatch_detected(self):
        report = vd.GateReport()
        data = {"providerId": "hirslanden"}
        entry = {"providerScope": "zollikerberg"}
        vd.check_tenant_boundary(data, entry, [], "ds", report)
        self.assertTrue(any(not r.passed and r.control_id == "NFR-SEC-005"
                            for r in report.results))

    def test_cross_tenant_record_detected(self):
        report = vd.GateReport()
        data = {"providerId": "hirslanden"}
        entry = {"providerScope": "hirslanden"}
        vd.check_tenant_boundary(
            data, entry,
            [{"capacityRecordId": "CAP-1", "providerId": "zollikerberg"}],
            "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_provider_scoped_dataset_passes(self):
        report = vd.GateReport()
        data = {"providerId": "hirslanden"}
        entry = {"providerScope": "hirslanden"}
        vd.check_tenant_boundary(
            data, entry, [{"capacityRecordId": "CAP-1"}], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))

    def test_shared_lane_rejects_dataset_provider_id(self):
        report = vd.GateReport()
        data = {"providerId": "usz"}
        entry = {"providerScope": "none"}
        vd.check_tenant_boundary(data, entry, [], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_shared_lane_with_record_providers_passes(self):
        report = vd.GateReport()
        data = {}
        entry = {"providerScope": "none"}
        vd.check_tenant_boundary(
            data, entry, [{"capacityRecordId": "CAP-1", "providerId": "usz"}],
            "ds", report)
        self.assertTrue(all(r.passed for r in report.results))


class DegradedModeTests(unittest.TestCase):
    def _ok_block(self):
        return {
            "fallbackReadModel": "last-known-good-capacity-snapshot",
            "maxDataStalenessMinutes": 15,
            "manualOverrideSupported": True,
            "recoveryRunbook": "docs/runbooks/x.md",
        }

    def test_shared_lane_skipped(self):
        report = vd.GateReport()
        vd.check_degraded_mode({}, {"providerScope": "none"}, "ds", report)
        self.assertEqual(report.results, [])

    def test_missing_block_detected(self):
        report = vd.GateReport()
        vd.check_degraded_mode({}, {"providerScope": "hirslanden"}, "ds", report)
        self.assertTrue(any(not r.passed and r.control_id == "NFR-REL-005"
                            for r in report.results))

    def test_staleness_ceiling_enforced(self):
        report = vd.GateReport()
        block = self._ok_block()
        block["maxDataStalenessMinutes"] = 120
        vd.check_degraded_mode({"degradedMode": block},
                               {"providerScope": "hirslanden"}, "ds", report)
        self.assertTrue(any(not r.passed and "60-minute ceiling" in r.message
                            for r in report.results))

    def test_manual_override_required(self):
        report = vd.GateReport()
        block = self._ok_block()
        block["manualOverrideSupported"] = False
        vd.check_degraded_mode({"degradedMode": block},
                               {"providerScope": "zollikerberg"}, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_valid_degraded_mode_passes(self):
        report = vd.GateReport()
        vd.check_degraded_mode({"degradedMode": self._ok_block()},
                               {"providerScope": "hirslanden"}, "ds", report)
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

    def test_traceability_covers_phase2_controls(self):
        evidence, _ = vd.run(ROOT)
        coverage = evidence["controlCoverage"]
        self.assertIn("NFR-SEC-005", coverage["nfr"])
        self.assertIn("CH-C02", coverage["ch"])
        for rv in ("RV-06-03", "RV-06-04", "RV-06-07"):
            self.assertIn(rv, coverage["rv"])


    def test_traceability_covers_phase3_controls(self):
        evidence, _ = vd.run(ROOT)
        coverage = evidence["controlCoverage"]
        self.assertIn("NFR-REL-005", coverage["nfr"])
        self.assertIn("CH-C03", coverage["ch"])
        for rv in ("RV-06-05", "RV-06-08", "RV-06-09"):
            self.assertIn(rv, coverage["rv"])


if __name__ == "__main__":
    unittest.main()
