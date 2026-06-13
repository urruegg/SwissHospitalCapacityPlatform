#!/usr/bin/env python3
"""Sprint 7 planning data-product contract tests."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_datasets as vd  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel: str) -> dict:
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
        return json.load(fh)


class SupplyOrganizationSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        full = _load("schema/dc-supply-organization-v1.schema.json")
        self.item_schema = full["properties"]["records"]["items"]

    def test_minimal_valid_record_passes(self):
        record = {
            "contractId": "DC-SUPPLY-ORGANIZATION-v1",
            "organizationId": "ORG-HIRSLANDEN",
            "name": "Klinik Hirslanden",
            "organizationType": "prov",
            "active": True,
            "country": "CH",
            "canton": "CH-ZH",
            "dataResidencyRegion": "switzerlandnorth",
        }
        self.assertFalse(vd.validate_schema(record, self.item_schema, "$"))

    def test_non_swiss_country_rejected(self):
        record = {
            "contractId": "DC-SUPPLY-ORGANIZATION-v1",
            "organizationId": "ORG-X",
            "name": "Test",
            "organizationType": "prov",
            "active": True,
            "country": "DE",
            "canton": "CH-ZH",
            "dataResidencyRegion": "switzerlandnorth",
        }
        errors = vd.validate_schema(record, self.item_schema, "$")
        self.assertTrue(any("country" in e for e in errors))

    def test_additional_property_rejected(self):
        record = {
            "contractId": "DC-SUPPLY-ORGANIZATION-v1",
            "organizationId": "ORG-X",
            "name": "Test",
            "organizationType": "prov",
            "active": True,
            "country": "CH",
            "canton": "CH-ZH",
            "dataResidencyRegion": "switzerlandnorth",
            "patientName": "John Doe",
        }
        errors = vd.validate_schema(record, self.item_schema, "$")
        self.assertTrue(any("patientName" in e for e in errors))


class SupplyLocationSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        full = _load("schema/dc-supply-location-v1.schema.json")
        self.item_schema = full["properties"]["records"]["items"]

    def _site(self):
        return {
            "contractId": "DC-SUPPLY-LOCATION-v1",
            "locationId": "LOC-HIRSL-SITE-01",
            "organizationId": "ORG-HIRSLANDEN",
            "physicalType": "si",
            "partOfId": None,
            "name": "Hirslanden Zurich Campus",
            "status": "active",
            "asOfTimestamp": "2026-06-12T08:00:00Z",
        }

    def _ward(self):
        return {
            "contractId": "DC-SUPPLY-LOCATION-v1",
            "locationId": "LOC-HIRSL-WARD-01",
            "organizationId": "ORG-HIRSLANDEN",
            "physicalType": "wa",
            "partOfId": "LOC-HIRSL-SITE-01",
            "name": "Cardiology Ward",
            "status": "active",
            "bedsTotal": 24,
            "bedsAvailable": 6,
            "specialtyServiceIds": ["HCS-CARD-01"],
            "healthcareServices": [{
                "healthcareServiceId": "HCS-CARD-01",
                "specialty": "cardiology",
                "specialtyTaxonomyVersion": "1.0.0",
                "category": "inpatient"
            }],
            "asOfTimestamp": "2026-06-12T08:00:00Z",
        }

    def _bed(self):
        return {
            "contractId": "DC-SUPPLY-LOCATION-v1",
            "locationId": "LOC-HIRSL-BED-001",
            "organizationId": "ORG-HIRSLANDEN",
            "physicalType": "bd",
            "partOfId": "LOC-HIRSL-WARD-01",
            "name": "Bed 1A",
            "status": "active",
            "operationalStatus": "U",
            "characteristic": ["single-room", "cardiac-monitoring"],
            "asOfTimestamp": "2026-06-12T08:00:00Z",
        }

    def test_site_record_valid(self):
        self.assertFalse(vd.validate_schema(self._site(), self.item_schema, "$"))

    def test_ward_record_valid(self):
        self.assertFalse(vd.validate_schema(self._ward(), self.item_schema, "$"))

    def test_bed_record_valid(self):
        self.assertFalse(vd.validate_schema(self._bed(), self.item_schema, "$"))

    def test_unknown_physical_type_rejected(self):
        rec = self._site()
        rec["physicalType"] = "bu"
        errors = vd.validate_schema(rec, self.item_schema, "$")
        self.assertTrue(any("physicalType" in e for e in errors))


class LocationHierarchyTests(unittest.TestCase):
    def _records(self):
        return [
            {"locationId": "LOC-S1", "physicalType": "si", "partOfId": None,
             "organizationId": "ORG-X", "status": "active",
             "asOfTimestamp": "2026-06-12T08:00:00Z"},
            {"locationId": "LOC-W1", "physicalType": "wa", "partOfId": "LOC-S1",
             "organizationId": "ORG-X", "status": "active", "bedsTotal": 10,
             "bedsAvailable": 4, "specialtyServiceIds": ["HCS-X"],
             "asOfTimestamp": "2026-06-12T08:00:00Z"},
            {"locationId": "LOC-B1", "physicalType": "bd", "partOfId": "LOC-W1",
             "organizationId": "ORG-X", "status": "active",
             "operationalStatus": "U",
             "asOfTimestamp": "2026-06-12T08:00:00Z"},
        ]

    def test_well_formed_hierarchy_passes(self):
        report = vd.GateReport()
        vd.check_location_hierarchy(self._records(), "ds", report)
        self.assertTrue(all(r.passed for r in report.results))

    def test_site_with_parent_fails(self):
        recs = self._records()
        recs[0]["partOfId"] = "LOC-W1"
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_ward_parent_must_be_site(self):
        recs = self._records()
        recs[1]["partOfId"] = "LOC-B1"
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_bed_parent_must_be_ward(self):
        recs = self._records()
        recs[2]["partOfId"] = "LOC-S1"
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_overcommit_detected(self):
        recs = self._records()
        recs[1]["bedsAvailable"] = 99
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any("NFR-DQ-005" in r.control_id and not r.passed
                            for r in report.results))

    def test_ward_missing_specialty_services_detected(self):
        recs = self._records()
        recs[1]["specialtyServiceIds"] = []
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_bed_missing_operational_status_detected(self):
        recs = self._records()
        del recs[2]["operationalStatus"]
        report = vd.GateReport()
        vd.check_location_hierarchy(recs, "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))


if __name__ == "__main__":
    unittest.main()
