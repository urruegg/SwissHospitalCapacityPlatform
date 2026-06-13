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


if __name__ == "__main__":
    unittest.main()
