# Patient Capacity Planning Data Product — Implementation Plan (Sprint 07)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement four FHIR-aligned data contracts (`DC-SUPPLY-ORGANIZATION-v1`, `DC-SUPPLY-LOCATION-v1`, `DC-DEMAND-ENCOUNTER-v1`, `DC-MATCH-RECOMMENDATION-v1`), a synthetic-data generator with a deterministic stub matcher, validator extensions for the new cross-contract invariants, and the doc updates that register them — exiting Sprint 07 deliverables 1–10.

**Architecture:** Extend the existing `data/synthetic/` pack (JSON Schemas + stdlib-only `validate_datasets.py` + `traceability.json`). Per-contract JSON Schemas enforce per-record shape with `additionalProperties: false`; cross-contract invariants and discriminator-conditional rules live in new Python `check_*` functions (same pattern as Sprint 6 `check_capacity_invariants`). One generator script (`generate_planning_datasets.py`) produces the four datasets + a manifest. The stub matcher is deterministic rules (no ML).

**Tech Stack:** Python 3.11+ stdlib only (no `jsonschema`, no `faker`); JSON Schema Draft-7 subset; `unittest` for tests; existing CI gate `validate_datasets.py`.

**Source spec:** [docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](../specs/2026-06-12-patient-capacity-data-product-design.md)

---

## Pre-flight

- [ ] **Step 0.1: Create the worktree / branch**

Run from repo root:

```powershell
git checkout -b sprint-07/patient-capacity-data-product
```

- [ ] **Step 0.2: Confirm baseline gate passes on `main`**

Run:

```powershell
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: exit code `0`; report ends with `pass`. If it fails, stop and fix the baseline first.

- [ ] **Step 0.3: Confirm baseline unit tests pass**

Run:

```powershell
python -m unittest discover -s data/synthetic/tests -v
```

Expected: all Sprint 6 tests green.

---

## Task 1: Validator generic extensions — nullable types, `date-time` format, `format` registry

**Why first:** Three of the four new contracts use nullable fields (`partOfId`, `periodEnd`, `recommendedBedLocationId`) and `date-time` (ISO 8601 UTC) fields. The existing schema validator (`validate_datasets.py` §JSON Schema subset) only supports a single `type` value and the `date` format. We extend the subset with the **smallest possible additions** before writing any new schema.

**Files:**
- Modify: `data/synthetic/validate_datasets.py` (function `validate_schema` and the `_DATE_RE` neighbourhood)
- Modify: `data/synthetic/tests/test_validate_datasets.py` (extend `SchemaValidationTests`)

- [ ] **Step 1.1: Write the failing tests**

Append to `data/synthetic/tests/test_validate_datasets.py` inside `SchemaValidationTests`:

```python
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
```

- [ ] **Step 1.2: Run tests, confirm they fail**

Run:

```powershell
python -m unittest data.synthetic.tests.test_validate_datasets -v
```

Expected: 3 new tests fail with `AssertionError` or `KeyError`-style validator behavior.

- [ ] **Step 1.3: Implement nullable type support**

In `validate_datasets.py`, locate the top of `validate_schema` where it dispatches on `schema.get("type")`. Replace the single-type dispatch with this block (keep all surrounding logic intact):

```python
    type_decl = schema.get("type")
    if isinstance(type_decl, list):
        type_errors_per_branch = []
        for candidate in type_decl:
            branch = dict(schema)
            branch["type"] = candidate
            branch_errors = validate_schema(instance, branch, path)
            if not branch_errors:
                return []
            type_errors_per_branch.append(branch_errors)
        # All branches failed — report a concise summary.
        joined = " / ".join(repr(t) for t in type_decl)
        return [f"{path}: expected type {joined}, got {type(instance).__name__}"]
```

Place this guard **before** any single-`type` checks; if `type_decl` is a string, fall through to the existing single-type logic untouched.

- [ ] **Step 1.4: Implement `date-time` format support**

Add next to `_DATE_RE`:

```python
# Strict ISO-8601 UTC instants. We deliberately require the trailing 'Z'
# (no offsets) so every record can be safely compared lexicographically.
_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$"
)
```

Find the `format == "date"` branch in `validate_schema` and add a sibling branch for `"date-time"`:

```python
        if fmt == "date-time":
            if not isinstance(instance, str) or not _DATETIME_RE.match(instance):
                errors.append(f"{path}: invalid date-time {instance!r} "
                              f"(expected ISO-8601 UTC with trailing 'Z')")
            else:
                try:
                    _dt.datetime.strptime(
                        instance.split(".")[0].rstrip("Z"),
                        "%Y-%m-%dT%H:%M:%S",
                    )
                except ValueError:
                    errors.append(f"{path}: invalid date-time {instance!r}")
```

- [ ] **Step 1.5: Run tests, confirm they pass**

Run:

```powershell
python -m unittest data.synthetic.tests.test_validate_datasets -v
```

Expected: all tests pass, including the three new ones, with no regressions.

- [ ] **Step 1.6: Commit**

```powershell
git add data/synthetic/validate_datasets.py data/synthetic/tests/test_validate_datasets.py
git commit -m "feat(synthetic): support nullable types and ISO-8601 UTC date-time in schema validator"
```

---

## Task 2: `DC-SUPPLY-ORGANIZATION-v1` — schema + dataset + validator binding

**Files:**
- Create: `data/synthetic/schema/dc-supply-organization-v1.schema.json`
- Create: `data/synthetic/datasets/dc-supply-organization-v1.sample.json` (committed after Task 7 wires the generator; for now hand-author a 2-record fixture to drive the test)
- Modify: `data/synthetic/traceability.json` (new entry)
- Create: `data/synthetic/tests/test_planning_contracts.py`

- [ ] **Step 2.1: Write the failing test**

Create `data/synthetic/tests/test_planning_contracts.py`:

```python
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
        self.schema = _load("schema/dc-supply-organization-v1.schema.json")

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
        self.assertFalse(vd.validate_schema(record, self.schema, "$"))

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
        errors = vd.validate_schema(record, self.schema, "$")
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
        errors = vd.validate_schema(record, self.schema, "$")
        self.assertTrue(any("patientName" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
```

Expected: tests fail with `FileNotFoundError` for the schema.

- [ ] **Step 2.3: Create the schema**

Create `data/synthetic/schema/dc-supply-organization-v1.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dc-supply-organization-v1.schema.json",
  "title": "Supply Organization (Hospital) Contract (DC-SUPPLY-ORGANIZATION-v1)",
  "description": "FHIR R4 Organization-aligned supply catalog entry for the patient capacity planning data product (Sprint 07).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "datasetId",
    "contractId",
    "contractVersion",
    "classification",
    "residency",
    "records"
  ],
  "properties": {
    "datasetId":        { "type": "string", "pattern": "^DS-SUPPLY-ORG-[a-z0-9-]+$" },
    "contractId":       { "type": "string", "enum": ["DC-SUPPLY-ORGANIZATION-v1"] },
    "contractVersion":  { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "classification":   { "type": "string", "enum": ["operational-confidential"] },
    "residency":        { "type": "string", "enum": ["CH"] },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "contractId",
          "organizationId",
          "name",
          "organizationType",
          "active",
          "country",
          "canton",
          "dataResidencyRegion"
        ],
        "properties": {
          "contractId":          { "type": "string", "enum": ["DC-SUPPLY-ORGANIZATION-v1"] },
          "organizationId":      { "type": "string", "pattern": "^ORG-[A-Z0-9-]+$" },
          "name":                { "type": "string", "minimum": 1 },
          "organizationType":    { "type": "string", "enum": ["prov"] },
          "active":              { "type": "boolean" },
          "country":             { "type": "string", "enum": ["CH"] },
          "canton":              { "type": "string", "pattern": "^CH-[A-Z]{2}$" },
          "dataResidencyRegion": { "type": "string", "enum": ["switzerlandnorth", "switzerlandwest"] },
          "extensions":          { "type": "object" }
        }
      }
    }
  }
}
```

Note: the per-record test in Step 2.1 validates a single record against the `items` subschema. Update the test to call `vd.validate_schema(record, self.schema["properties"]["records"]["items"], "$")` for the per-record assertions. Fix the test before running again.

- [ ] **Step 2.4: Fix test to point at `items` subschema**

In `test_planning_contracts.py`, replace `self.schema` in each `SupplyOrganizationSchemaTests` test body with `self.schema["properties"]["records"]["items"]`. Re-run:

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
```

Expected: all 3 tests pass.

- [ ] **Step 2.5: Create the seed dataset fixture**

Create `data/synthetic/datasets/dc-supply-organization-v1.sample.json`:

```json
{
  "datasetId": "DS-SUPPLY-ORG-sit-2026-06-12",
  "contractId": "DC-SUPPLY-ORGANIZATION-v1",
  "contractVersion": "1.0.0",
  "classification": "operational-confidential",
  "residency": "CH",
  "records": [
    {
      "contractId": "DC-SUPPLY-ORGANIZATION-v1",
      "organizationId": "ORG-HIRSLANDEN",
      "name": "Klinik Hirslanden",
      "organizationType": "prov",
      "active": true,
      "country": "CH",
      "canton": "CH-ZH",
      "dataResidencyRegion": "switzerlandnorth"
    },
    {
      "contractId": "DC-SUPPLY-ORGANIZATION-v1",
      "organizationId": "ORG-ZOLLIKERBERG",
      "name": "Spital Zollikerberg",
      "organizationType": "prov",
      "active": true,
      "country": "CH",
      "canton": "CH-ZH",
      "dataResidencyRegion": "switzerlandnorth"
    }
  ]
}
```

- [ ] **Step 2.6: Register in `traceability.json`**

In `data/synthetic/traceability.json`, append to `datasets[]`:

```json
{
  "datasetId": "DS-SUPPLY-ORG-sit-2026-06-12",
  "lane": "planning-supply-organization",
  "providerScope": "none",
  "dataFile": "datasets/dc-supply-organization-v1.sample.json",
  "schemaFile": "schema/dc-supply-organization-v1.schema.json",
  "minimizationChecked": false,
  "fr": ["FR-DATA-002", "FR-DATA-005"],
  "nfr": ["NFR-COMP-011"],
  "ch": ["CH-C05"],
  "rv": ["RV-06-10"]
}
```

> `minimizationChecked: false` because Organization records carry no patient data and the existing `check_minimization` denylist would flag the field `name` (public legal entity name, no PHI risk — see spec §5.1). Patient-side PHI scans run later via a dedicated `check_planning_phi_denylist` (Task 4).

- [ ] **Step 2.7: Run the end-to-end gate**

```powershell
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: `pass`; new dataset evaluated; existing Sprint 6 datasets still pass.

- [ ] **Step 2.8: Commit**

```powershell
git add data/synthetic/schema/dc-supply-organization-v1.schema.json `
        data/synthetic/datasets/dc-supply-organization-v1.sample.json `
        data/synthetic/traceability.json `
        data/synthetic/tests/test_planning_contracts.py
git commit -m "feat(data): add DC-SUPPLY-ORGANIZATION-v1 contract, schema, and seed dataset"
```

---

## Task 3: `DC-SUPPLY-LOCATION-v1` — recursive schema + hierarchy validator

**Files:**
- Create: `data/synthetic/schema/dc-supply-location-v1.schema.json`
- Create: `data/synthetic/datasets/dc-supply-location-v1.sample.json` (hand-authored 3-record fixture: 1 site + 1 ward + 1 bed)
- Modify: `data/synthetic/traceability.json` (new entry + new lane `planning-supply-location`)
- Modify: `data/synthetic/validate_datasets.py` — add `check_location_hierarchy(...)`
- Modify: `data/synthetic/tests/test_planning_contracts.py` — `SupplyLocationSchemaTests` and `LocationHierarchyTests`

- [ ] **Step 3.1: Write failing schema tests**

Append to `data/synthetic/tests/test_planning_contracts.py`:

```python
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
```

- [ ] **Step 3.2: Run, confirm failures (no schema yet)**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
```

Expected: 4 new tests fail with `FileNotFoundError`.

- [ ] **Step 3.3: Create the Location schema**

Create `data/synthetic/schema/dc-supply-location-v1.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dc-supply-location-v1.schema.json",
  "title": "Supply Location (Site/Ward/Bed) Contract (DC-SUPPLY-LOCATION-v1)",
  "description": "FHIR R4 Location + HealthcareService aligned recursive supply contract. Discriminated by physicalType: si=site, wa=ward/station, bd=bed. Hierarchy and bed/ward invariants are enforced by check_location_hierarchy in validate_datasets.py.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "datasetId", "contractId", "contractVersion",
    "classification", "residency", "records"
  ],
  "properties": {
    "datasetId":        { "type": "string", "pattern": "^DS-SUPPLY-LOC-[a-z0-9-]+$" },
    "contractId":       { "type": "string", "enum": ["DC-SUPPLY-LOCATION-v1"] },
    "contractVersion":  { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "classification":   { "type": "string", "enum": ["operational-confidential"] },
    "residency":        { "type": "string", "enum": ["CH"] },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "contractId", "locationId", "organizationId",
          "physicalType", "partOfId", "name", "status", "asOfTimestamp"
        ],
        "properties": {
          "contractId":         { "type": "string", "enum": ["DC-SUPPLY-LOCATION-v1"] },
          "locationId":         { "type": "string", "pattern": "^LOC-[A-Z0-9-]+$" },
          "organizationId":     { "type": "string", "pattern": "^ORG-[A-Z0-9-]+$" },
          "physicalType":       { "type": "string", "enum": ["si", "wa", "bd"] },
          "partOfId":           { "type": ["string", "null"], "pattern": "^LOC-[A-Z0-9-]+$" },
          "name":               { "type": "string" },
          "status":             { "type": "string", "enum": ["active", "suspended", "inactive"] },
          "operationalStatus":  { "type": "string", "enum": ["U", "O", "H", "I", "K", "C"] },
          "bedsTotal":          { "type": "integer", "minimum": 0, "maximum": 2000 },
          "bedsAvailable":      { "type": "integer", "minimum": 0, "maximum": 2000 },
          "specialtyServiceIds": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string", "pattern": "^HCS-[A-Z0-9-]+$" }
          },
          "characteristic": {
            "type": "array",
            "items": { "type": "string", "enum": [
              "isolation", "cardiac-monitoring", "negative-pressure",
              "bariatric", "single-room", "pediatric-equipped",
              "female-only", "male-only"
            ]}
          },
          "healthcareServices": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["healthcareServiceId", "specialty", "specialtyTaxonomyVersion", "category"],
              "properties": {
                "healthcareServiceId":      { "type": "string", "pattern": "^HCS-[A-Z0-9-]+$" },
                "specialty":                { "type": "string", "pattern": "^[a-z][a-z-]+$" },
                "specialtyTaxonomyVersion": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
                "category":                 { "type": "string", "enum": ["inpatient", "surgical", "icu", "rehab"] }
              }
            }
          },
          "asOfTimestamp": { "type": "string", "format": "date-time" },
          "extensions":    { "type": "object" }
        }
      }
    }
  }
}
```

> The discriminator-conditional `required` rules (e.g. `bedsTotal` mandatory only when `physicalType=wa`) are enforced by `check_location_hierarchy` (Step 3.5) — not by the JSON Schema subset, which has no `if/then/oneOf`. This is the same architectural pattern Sprint 6 used for `check_capacity_invariants`.

- [ ] **Step 3.4: Re-run schema tests, confirm pass**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.SupplyLocationSchemaTests -v
```

Expected: 4 tests pass.

- [ ] **Step 3.5: Write failing hierarchy-validator tests**

Append to `data/synthetic/tests/test_planning_contracts.py`:

```python
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
```

- [ ] **Step 3.6: Run, confirm failures (no validator function yet)**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.LocationHierarchyTests -v
```

Expected: 7 tests fail with `AttributeError: module ... has no attribute 'check_location_hierarchy'`.

- [ ] **Step 3.7: Implement `check_location_hierarchy`**

Add to `data/synthetic/validate_datasets.py` (next to `check_capacity_invariants`):

```python
def check_location_hierarchy(records: list[dict], dataset_id: str,
                              report: GateReport) -> None:
    """Validate the recursive Site/Ward/Bed hierarchy and per-discriminator
    required fields for DC-SUPPLY-LOCATION-v1 (spec §5.2)."""
    by_id = {r.get("locationId"): r for r in records}
    failures = 0

    for rec in records:
        loc_id = rec.get("locationId", "<unknown>")
        phys = rec.get("physicalType")
        parent_id = rec.get("partOfId")

        # Rule 1-3: physicalType / partOfId hierarchy.
        if phys == "si" and parent_id is not None:
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Site {loc_id!r} must have partOfId=null.", dataset_id))
            failures += 1
        elif phys == "wa":
            parent = by_id.get(parent_id)
            if parent is None or parent.get("physicalType") != "si":
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Ward {loc_id!r} partOfId must reference a Site.", dataset_id))
                failures += 1
        elif phys == "bd":
            parent = by_id.get(parent_id)
            if parent is None or parent.get("physicalType") != "wa":
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Bed {loc_id!r} partOfId must reference a Ward.", dataset_id))
                failures += 1

        # Rule 4: bedsAvailable <= bedsTotal (only for wards).
        if phys == "wa":
            total = rec.get("bedsTotal")
            avail = rec.get("bedsAvailable")
            if not isinstance(total, int) or not isinstance(avail, int):
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Ward {loc_id!r} missing bedsTotal/bedsAvailable.", dataset_id))
                failures += 1
            elif avail > total:
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Ward {loc_id!r} bedsAvailable {avail} > bedsTotal {total}.",
                    dataset_id))
                failures += 1
            # Rule 5: ward requires >= 1 specialty service.
            services = rec.get("specialtyServiceIds") or []
            if len(services) < 1:
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Ward {loc_id!r} must declare >= 1 specialtyServiceId.",
                    dataset_id))
                failures += 1

        # Rule (spec §5.2): bed requires operationalStatus.
        if phys == "bd" and not rec.get("operationalStatus"):
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Bed {loc_id!r} missing operationalStatus.", dataset_id))
            failures += 1

    if failures == 0:
        report.add(CheckResult("NFR-DQ-005", "low", True,
            "Location hierarchy and ward/bed invariants OK.", dataset_id))
```

- [ ] **Step 3.8: Wire the check into `validate_dataset` dispatch**

In `validate_datasets.py`, find the lane-based dispatch (`if entry.get("lane") == "specialty-capacity":`) and add a sibling block:

```python
    if entry.get("lane") == "planning-supply-location":
        check_location_hierarchy(records, dataset_id, report)
```

- [ ] **Step 3.9: Create the seed dataset fixture**

Create `data/synthetic/datasets/dc-supply-location-v1.sample.json`:

```json
{
  "datasetId": "DS-SUPPLY-LOC-sit-2026-06-12",
  "contractId": "DC-SUPPLY-LOCATION-v1",
  "contractVersion": "1.0.0",
  "classification": "operational-confidential",
  "residency": "CH",
  "records": [
    {
      "contractId": "DC-SUPPLY-LOCATION-v1",
      "locationId": "LOC-HIRSL-SITE-01",
      "organizationId": "ORG-HIRSLANDEN",
      "physicalType": "si",
      "partOfId": null,
      "name": "Hirslanden Zurich Campus",
      "status": "active",
      "asOfTimestamp": "2026-06-12T08:00:00Z"
    },
    {
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
      "healthcareServices": [
        {
          "healthcareServiceId": "HCS-CARD-01",
          "specialty": "cardiology",
          "specialtyTaxonomyVersion": "1.0.0",
          "category": "inpatient"
        }
      ],
      "asOfTimestamp": "2026-06-12T08:00:00Z"
    },
    {
      "contractId": "DC-SUPPLY-LOCATION-v1",
      "locationId": "LOC-HIRSL-BED-001",
      "organizationId": "ORG-HIRSLANDEN",
      "physicalType": "bd",
      "partOfId": "LOC-HIRSL-WARD-01",
      "name": "Bed 1A",
      "status": "active",
      "operationalStatus": "U",
      "characteristic": ["single-room", "cardiac-monitoring"],
      "asOfTimestamp": "2026-06-12T08:00:00Z"
    }
  ]
}
```

- [ ] **Step 3.10: Add traceability entry**

Append to `traceability.json` `datasets[]`:

```json
{
  "datasetId": "DS-SUPPLY-LOC-sit-2026-06-12",
  "lane": "planning-supply-location",
  "providerScope": "none",
  "dataFile": "datasets/dc-supply-location-v1.sample.json",
  "schemaFile": "schema/dc-supply-location-v1.schema.json",
  "minimizationChecked": false,
  "fr": ["FR-DATA-002", "FR-DATA-005", "FR-ONB-003"],
  "nfr": ["NFR-DQ-005", "NFR-COMP-011"],
  "ch": ["CH-C05"],
  "rv": ["RV-06-10"]
}
```

- [ ] **Step 3.11: Run unit tests + end-to-end gate**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: all schema + hierarchy unit tests pass; e2e gate exits `0`.

- [ ] **Step 3.12: Commit**

```powershell
git add data/synthetic/schema/dc-supply-location-v1.schema.json `
        data/synthetic/datasets/dc-supply-location-v1.sample.json `
        data/synthetic/traceability.json `
        data/synthetic/validate_datasets.py `
        data/synthetic/tests/test_planning_contracts.py
git commit -m "feat(data): add DC-SUPPLY-LOCATION-v1 recursive contract with hierarchy validator"
```

---

## Task 4: `DC-DEMAND-ENCOUNTER-v1` — schema + lifecycle/PHI validator

**Files:**
- Create: `data/synthetic/schema/dc-demand-encounter-v1.schema.json`
- Create: `data/synthetic/datasets/dc-demand-encounter-v1.sample.json` (hand-authored 2-record fixture: one `planned`, one mid-lifecycle)
- Modify: `data/synthetic/traceability.json`
- Modify: `data/synthetic/validate_datasets.py` — add `check_encounter_lifecycle`, extend `check_planning_phi_denylist`
- Modify: `data/synthetic/tests/test_planning_contracts.py` — `DemandEncounterSchemaTests`, `EncounterLifecycleTests`, `PlanningPhiDenylistTests`

- [ ] **Step 4.1: Write failing schema test**

Append to `test_planning_contracts.py`:

```python
class DemandEncounterSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        full = _load("schema/dc-demand-encounter-v1.schema.json")
        self.item_schema = full["properties"]["records"]["items"]

    def _record(self):
        return {
            "contractId": "DC-DEMAND-ENCOUNTER-v1",
            "encounterId": "ENC-2026-0001",
            "pseudonymId": "PID-9F2A1B7C",
            "organizationId": "ORG-HIRSLANDEN",
            "class": "IMP",
            "status": "planned",
            "admissionType": "elective",
            "requestedSpecialtyServiceId": "HCS-CARD-01",
            "requiredCharacteristics": ["cardiac-monitoring"],
            "acuityBand": "routine",
            "expectedArrivalTimestamp": "2026-06-14T10:00:00Z",
            "expectedLOSDays": 4,
            "statusHistory": [{
                "status": "planned",
                "periodStart": "2026-06-12T08:00:00Z",
                "periodEnd": None,
                "locationId": None
            }],
            "purposeTag": "capacity-planning",
            "dataResidencyRegion": "switzerlandnorth",
            "asOfTimestamp": "2026-06-12T08:00:00Z"
        }

    def test_minimal_valid_record_passes(self):
        self.assertFalse(vd.validate_schema(self._record(), self.item_schema, "$"))

    def test_outpatient_class_rejected(self):
        rec = self._record()
        rec["class"] = "AMB"
        errors = vd.validate_schema(rec, self.item_schema, "$")
        self.assertTrue(any("class" in e for e in errors))

    def test_phi_field_in_extensions_path_rejected(self):
        rec = self._record()
        rec["firstName"] = "Anna"
        errors = vd.validate_schema(rec, self.item_schema, "$")
        self.assertTrue(any("firstName" in e for e in errors))
```

- [ ] **Step 4.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.DemandEncounterSchemaTests -v
```

Expected: tests fail with `FileNotFoundError`.

- [ ] **Step 4.3: Create the Encounter schema**

Create `data/synthetic/schema/dc-demand-encounter-v1.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dc-demand-encounter-v1.schema.json",
  "title": "Demand Encounter Contract (DC-DEMAND-ENCOUNTER-v1)",
  "description": "FHIR R4 Encounter (class=IMP) + EncounterStatusHistory aligned demand contract for inpatient hospitalisation planning (Sprint 07).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "datasetId", "contractId", "contractVersion",
    "classification", "residency", "records"
  ],
  "properties": {
    "datasetId":        { "type": "string", "pattern": "^DS-DEMAND-ENC-[a-z0-9-]+$" },
    "contractId":       { "type": "string", "enum": ["DC-DEMAND-ENCOUNTER-v1"] },
    "contractVersion":  { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "classification":   { "type": "string", "enum": ["operational-confidential"] },
    "residency":        { "type": "string", "enum": ["CH"] },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "contractId", "encounterId", "pseudonymId", "organizationId",
          "class", "status", "admissionType", "requestedSpecialtyServiceId",
          "acuityBand", "expectedArrivalTimestamp", "expectedLOSDays",
          "statusHistory", "purposeTag", "dataResidencyRegion", "asOfTimestamp"
        ],
        "properties": {
          "contractId":                  { "type": "string", "enum": ["DC-DEMAND-ENCOUNTER-v1"] },
          "encounterId":                 { "type": "string", "pattern": "^ENC-[0-9]{4}-[0-9]{4,}$" },
          "pseudonymId":                 { "type": "string", "pattern": "^PID-[A-F0-9]{8}$" },
          "organizationId":              { "type": "string", "pattern": "^ORG-[A-Z0-9-]+$" },
          "class":                       { "type": "string", "enum": ["IMP"] },
          "status":                      { "type": "string", "enum": ["planned", "arrived", "triaged", "in-progress", "onleave", "finished", "cancelled"] },
          "admissionType":               { "type": "string", "enum": ["emergency", "elective", "transfer", "observation"] },
          "requestedSpecialtyServiceId": { "type": "string", "pattern": "^HCS-[A-Z0-9-]+$" },
          "requiredCharacteristics": {
            "type": "array",
            "items": { "type": "string", "enum": [
              "isolation", "cardiac-monitoring", "negative-pressure",
              "bariatric", "single-room", "pediatric-equipped",
              "female-only", "male-only"
            ]}
          },
          "acuityBand":                  { "type": "string", "enum": ["routine", "urgent", "asap", "stat"] },
          "expectedArrivalTimestamp":    { "type": "string", "format": "date-time" },
          "expectedLOSDays":             { "type": "integer", "minimum": 1, "maximum": 365 },
          "expectedDischargeTimestamp":  { "type": "string", "format": "date-time" },
          "statusHistory": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["status", "periodStart", "periodEnd"],
              "properties": {
                "status":      { "type": "string", "enum": ["planned", "arrived", "triaged", "in-progress", "onleave", "finished", "cancelled"] },
                "periodStart": { "type": "string", "format": "date-time" },
                "periodEnd":   { "type": ["string", "null"], "format": "date-time" },
                "locationId":  { "type": ["string", "null"], "pattern": "^LOC-[A-Z0-9-]+$" }
              }
            }
          },
          "purposeTag":          { "type": "string", "enum": ["capacity-planning", "bed-management"] },
          "dataResidencyRegion": { "type": "string", "enum": ["switzerlandnorth", "switzerlandwest"] },
          "asOfTimestamp":       { "type": "string", "format": "date-time" },
          "extensions":          { "type": "object" }
        }
      }
    }
  }
}
```

- [ ] **Step 4.4: Re-run schema tests, confirm pass**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.DemandEncounterSchemaTests -v
```

Expected: 3 tests pass.

- [ ] **Step 4.5: Write failing lifecycle + PHI validator tests**

Append to `test_planning_contracts.py`:

```python
class EncounterLifecycleTests(unittest.TestCase):
    def _record(self, status="planned", history=None):
        return {
            "encounterId": "ENC-2026-0001",
            "status": status,
            "statusHistory": history or [
                {"status": "planned", "periodStart": "2026-06-12T08:00:00Z",
                 "periodEnd": None}
            ],
            "expectedLOSDays": 4,
            "dataResidencyRegion": "switzerlandnorth",
            "organizationId": "ORG-X",
        }

    def test_well_formed_passes(self):
        report = vd.GateReport()
        vd.check_encounter_lifecycle([self._record()], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))

    def test_current_status_must_match_last_history(self):
        rec = self._record(status="finished")  # history still ends on "planned"
        report = vd.GateReport()
        vd.check_encounter_lifecycle([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_periods_must_be_strictly_ordered(self):
        rec = self._record(status="in-progress", history=[
            {"status": "planned",     "periodStart": "2026-06-12T10:00:00Z",
             "periodEnd": "2026-06-12T08:00:00Z"},
            {"status": "in-progress", "periodStart": "2026-06-12T08:00:00Z",
             "periodEnd": None},
        ])
        report = vd.GateReport()
        vd.check_encounter_lifecycle([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_only_last_entry_may_have_null_period_end(self):
        rec = self._record(status="in-progress", history=[
            {"status": "planned",     "periodStart": "2026-06-12T08:00:00Z",
             "periodEnd": None},
            {"status": "in-progress", "periodStart": "2026-06-12T10:00:00Z",
             "periodEnd": None},
        ])
        report = vd.GateReport()
        vd.check_encounter_lifecycle([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_long_los_emits_warning_not_failure(self):
        rec = self._record()
        rec["expectedLOSDays"] = 120
        report = vd.GateReport()
        vd.check_encounter_lifecycle([rec], "ds", report)
        warnings = [r for r in report.results
                    if r.control_id == "NFR-DQ-005" and r.severity == "low" and not r.passed]
        # Long-stay note appears, but no critical/high failures.
        self.assertFalse(any(r.severity in ("critical", "high")
                             for r in report.results if not r.passed))


class PlanningPhiDenylistTests(unittest.TestCase):
    def test_clinical_code_field_detected(self):
        rec = {"encounterId": "ENC-1", "icdCode": "I21.4"}
        report = vd.GateReport()
        vd.check_planning_phi_denylist([rec], "ds", report)
        self.assertTrue(any(not r.passed and r.control_id == "CH-C01"
                            for r in report.results))

    def test_clean_record_passes(self):
        rec = {"encounterId": "ENC-1", "pseudonymId": "PID-AAAAAAAA"}
        report = vd.GateReport()
        vd.check_planning_phi_denylist([rec], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))
```

- [ ] **Step 4.6: Run, confirm failures**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.EncounterLifecycleTests data.synthetic.tests.test_planning_contracts.PlanningPhiDenylistTests -v
```

Expected: tests fail (`AttributeError`).

- [ ] **Step 4.7: Implement the two validator functions**

Add to `validate_datasets.py`:

```python
PLANNING_CLINICAL_DENYLIST = {
    "icdcode", "icd10", "icd11", "snomed", "snomedcode",
    "diagnosis", "diagnoses", "diagnosiscode",
    "clinicalnote", "clinicalnotes", "notes",
    "procedurecode", "drgcode",
}


def check_encounter_lifecycle(records: list[dict], dataset_id: str,
                              report: GateReport) -> None:
    """Validate DC-DEMAND-ENCOUNTER-v1 lifecycle invariants (spec §6.4)."""
    failures = 0
    for rec in records:
        enc_id = rec.get("encounterId", "<unknown>")
        history = rec.get("statusHistory") or []
        if not history:
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Encounter {enc_id!r} has empty statusHistory.", dataset_id))
            failures += 1
            continue

        # Strictly ordered periodStart values.
        starts = [h.get("periodStart") for h in history]
        if starts != sorted(starts):
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Encounter {enc_id!r} statusHistory periodStart not strictly ordered.",
                dataset_id))
            failures += 1

        # Only last entry may have periodEnd=null.
        for idx, h in enumerate(history[:-1]):
            if h.get("periodEnd") is None:
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Encounter {enc_id!r} non-terminal statusHistory[{idx}] has null periodEnd.",
                    dataset_id))
                failures += 1

        # Per-entry: periodEnd >= periodStart (when present).
        for idx, h in enumerate(history):
            end = h.get("periodEnd")
            if end is not None and end < h.get("periodStart", ""):
                report.add(CheckResult("NFR-DQ-005", "high", False,
                    f"Encounter {enc_id!r} statusHistory[{idx}] periodEnd < periodStart.",
                    dataset_id))
                failures += 1

        # Current status equals last entry's status.
        if rec.get("status") != history[-1].get("status"):
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Encounter {enc_id!r} status {rec.get('status')!r} does not match "
                f"last statusHistory entry {history[-1].get('status')!r}.",
                dataset_id))
            failures += 1

        # LOS soft bound: warn-only above 90 days.
        los = rec.get("expectedLOSDays")
        if isinstance(los, int) and los > 90:
            report.add(CheckResult("NFR-DQ-005", "low", True,
                f"Encounter {enc_id!r} expectedLOSDays={los} exceeds 90-day soft bound "
                "(legitimate for long-stay rehab; informational).", dataset_id))

    if failures == 0:
        report.add(CheckResult("NFR-DQ-005", "low", True,
            "Encounter lifecycle invariants OK.", dataset_id))


def check_planning_phi_denylist(records: list[dict], dataset_id: str,
                                report: GateReport) -> None:
    """Reject clinical / direct-identifier fields on planning records (spec §6.5)."""
    failures = 0
    for rec in records:
        rec_id = rec.get("encounterId") or rec.get("recommendationId") or "<unknown>"
        for key in rec.keys():
            lk = key.lower()
            if lk in FORBIDDEN_IDENTIFIER_FIELDS or lk in PLANNING_CLINICAL_DENYLIST:
                report.add(CheckResult("CH-C01", "critical", False,
                    f"Planning record {rec_id!r} carries forbidden field {key!r}.",
                    dataset_id))
                failures += 1
    if failures == 0:
        report.add(CheckResult("CH-C01", "low", True,
            "Planning PHI/clinical denylist clean.", dataset_id))
```

- [ ] **Step 4.8: Wire the new lane into `validate_dataset`**

Add to the lane dispatch in `validate_datasets.py`:

```python
    if entry.get("lane") == "planning-demand-encounter":
        check_encounter_lifecycle(records, dataset_id, report)
        check_planning_phi_denylist(records, dataset_id, report)
```

- [ ] **Step 4.9: Create the seed dataset fixture**

Create `data/synthetic/datasets/dc-demand-encounter-v1.sample.json`:

```json
{
  "datasetId": "DS-DEMAND-ENC-sit-2026-06-12",
  "contractId": "DC-DEMAND-ENCOUNTER-v1",
  "contractVersion": "1.0.0",
  "classification": "operational-confidential",
  "residency": "CH",
  "records": [
    {
      "contractId": "DC-DEMAND-ENCOUNTER-v1",
      "encounterId": "ENC-2026-0001",
      "pseudonymId": "PID-9F2A1B7C",
      "organizationId": "ORG-HIRSLANDEN",
      "class": "IMP",
      "status": "planned",
      "admissionType": "elective",
      "requestedSpecialtyServiceId": "HCS-CARD-01",
      "requiredCharacteristics": ["cardiac-monitoring"],
      "acuityBand": "routine",
      "expectedArrivalTimestamp": "2026-06-14T10:00:00Z",
      "expectedLOSDays": 4,
      "statusHistory": [
        {
          "status": "planned",
          "periodStart": "2026-06-12T08:00:00Z",
          "periodEnd": null,
          "locationId": null
        }
      ],
      "purposeTag": "capacity-planning",
      "dataResidencyRegion": "switzerlandnorth",
      "asOfTimestamp": "2026-06-12T08:00:00Z"
    },
    {
      "contractId": "DC-DEMAND-ENCOUNTER-v1",
      "encounterId": "ENC-2026-0002",
      "pseudonymId": "PID-12345678",
      "organizationId": "ORG-HIRSLANDEN",
      "class": "IMP",
      "status": "in-progress",
      "admissionType": "emergency",
      "requestedSpecialtyServiceId": "HCS-CARD-01",
      "requiredCharacteristics": ["isolation"],
      "acuityBand": "urgent",
      "expectedArrivalTimestamp": "2026-06-12T06:00:00Z",
      "expectedLOSDays": 6,
      "statusHistory": [
        {"status": "arrived",     "periodStart": "2026-06-12T06:00:00Z", "periodEnd": "2026-06-12T06:30:00Z", "locationId": null},
        {"status": "triaged",     "periodStart": "2026-06-12T06:30:00Z", "periodEnd": "2026-06-12T07:15:00Z", "locationId": null},
        {"status": "in-progress", "periodStart": "2026-06-12T07:15:00Z", "periodEnd": null,                    "locationId": "LOC-HIRSL-WARD-01"}
      ],
      "purposeTag": "bed-management",
      "dataResidencyRegion": "switzerlandnorth",
      "asOfTimestamp": "2026-06-12T08:00:00Z"
    }
  ]
}
```

- [ ] **Step 4.10: Add traceability entry**

Append to `traceability.json`:

```json
{
  "datasetId": "DS-DEMAND-ENC-sit-2026-06-12",
  "lane": "planning-demand-encounter",
  "providerScope": "none",
  "dataFile": "datasets/dc-demand-encounter-v1.sample.json",
  "schemaFile": "schema/dc-demand-encounter-v1.schema.json",
  "minimizationChecked": false,
  "fr": ["FR-DATA-001", "FR-DATA-002", "FR-DATA-005"],
  "nfr": ["NFR-COMP-011", "NFR-DQ-005"],
  "ch": ["CH-C01", "CH-C05"],
  "rv": ["RV-06-10"]
}
```

- [ ] **Step 4.11: Run all tests + e2e gate**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: all tests pass; gate exits `0`.

- [ ] **Step 4.12: Commit**

```powershell
git add data/synthetic/schema/dc-demand-encounter-v1.schema.json `
        data/synthetic/datasets/dc-demand-encounter-v1.sample.json `
        data/synthetic/traceability.json `
        data/synthetic/validate_datasets.py `
        data/synthetic/tests/test_planning_contracts.py
git commit -m "feat(data): add DC-DEMAND-ENCOUNTER-v1 contract with lifecycle and PHI denylist validators"
```

---

## Task 5: `DC-MATCH-RECOMMENDATION-v1` — schema + invariants validator

**Files:**
- Create: `data/synthetic/schema/dc-match-recommendation-v1.schema.json`
- Create: `data/synthetic/datasets/dc-match-recommendation-v1.sample.json` (hand-authored 1-record fixture with 2 candidates)
- Modify: `data/synthetic/traceability.json`
- Modify: `data/synthetic/validate_datasets.py` — add `check_recommendation_invariants`
- Modify: `data/synthetic/tests/test_planning_contracts.py` — `MatchRecommendationSchemaTests`, `RecommendationInvariantsTests`

- [ ] **Step 5.1: Write failing schema test**

Append to `test_planning_contracts.py`:

```python
class MatchRecommendationSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        full = _load("schema/dc-match-recommendation-v1.schema.json")
        self.item_schema = full["properties"]["records"]["items"]

    def _record(self):
        return {
            "contractId": "DC-MATCH-RECOMMENDATION-v1",
            "recommendationId": "REC-2026-06-12T08:00:00Z-ENC-2026-0001",
            "encounterId": "ENC-2026-0001",
            "organizationId": "ORG-HIRSLANDEN",
            "generatedAt": "2026-06-12T08:00:00Z",
            "validUntil":  "2026-06-12T08:30:00Z",
            "algorithmId": "stub-rules-v1",
            "algorithmVersion": "1.0.0",
            "status": "advisory",
            "dataResidencyRegion": "switzerlandnorth",
            "inputSnapshot": {
                "encounterAsOf": "2026-06-12T08:00:00Z",
                "supplyAsOf":    "2026-06-12T08:00:00Z",
                "consideredStationIds": ["LOC-HIRSL-WARD-01"]
            },
            "candidates": [{
                "rank": 1,
                "stationLocationId": "LOC-HIRSL-WARD-01",
                "recommendedBedLocationId": None,
                "fitScore": 0.92,
                "capacityHeadroom": 5,
                "expectedAdmitWindowStart": "2026-06-14T08:00:00Z",
                "expectedAdmitWindowEnd":   "2026-06-14T14:00:00Z",
                "explanationFactors": [
                    {"factor": "specialty-match",  "weight": 0.6},
                    {"factor": "capacity-headroom","weight": 0.4}
                ],
                "hardConstraintsMet": True
            }]
        }

    def test_minimal_valid_record_passes(self):
        self.assertFalse(vd.validate_schema(self._record(), self.item_schema, "$"))

    def test_more_than_five_candidates_rejected(self):
        rec = self._record()
        rec["candidates"] = [dict(rec["candidates"][0], rank=i + 1) for i in range(6)]
        errors = vd.validate_schema(rec, self.item_schema, "$")
        self.assertTrue(any("maxItems" in e or "candidates" in e for e in errors))

    def test_unknown_factor_rejected(self):
        rec = self._record()
        rec["candidates"][0]["explanationFactors"][0]["factor"] = "vibes"
        errors = vd.validate_schema(rec, self.item_schema, "$")
        self.assertTrue(any("vibes" in e or "factor" in e for e in errors))
```

> The third test depends on the validator supporting `maxItems`. If `validate_schema` does not implement `maxItems`, add it in this task (mirror the `minItems` branch). The skill rule "Type consistency" applies — keep the test honest.

- [ ] **Step 5.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.MatchRecommendationSchemaTests -v
```

Expected: tests fail with `FileNotFoundError`.

- [ ] **Step 5.3: Implement `maxItems` if missing**

Inspect `validate_schema` in `validate_datasets.py`. If `maxItems` is absent, find the `minItems` branch and add directly after it:

```python
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                errors.append(f"{path}: maxItems violated "
                              f"({len(instance)} > {schema['maxItems']})")
```

Add a sibling unit test in `SchemaValidationTests` (test_validate_datasets.py):

```python
    def test_max_items_reported(self):
        schema = {"type": "array", "maxItems": 1, "items": {"type": "string"}}
        errors = vd.validate_schema(["a", "b"], schema, "$")
        self.assertTrue(any("maxItems" in e for e in errors))
```

Run `python -m unittest data.synthetic.tests.test_validate_datasets -v` and confirm the new test passes.

- [ ] **Step 5.4: Create the Recommendation schema**

Create `data/synthetic/schema/dc-match-recommendation-v1.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dc-match-recommendation-v1.schema.json",
  "title": "Match Recommendation Contract (DC-MATCH-RECOMMENDATION-v1)",
  "description": "Ranked top-N candidate Stations per Encounter, advisory only (Sprint 07).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "datasetId", "contractId", "contractVersion",
    "classification", "residency", "records"
  ],
  "properties": {
    "datasetId":        { "type": "string", "pattern": "^DS-MATCH-REC-[a-z0-9-]+$" },
    "contractId":       { "type": "string", "enum": ["DC-MATCH-RECOMMENDATION-v1"] },
    "contractVersion":  { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "classification":   { "type": "string", "enum": ["operational-confidential"] },
    "residency":        { "type": "string", "enum": ["CH"] },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "contractId", "recommendationId", "encounterId", "organizationId",
          "generatedAt", "validUntil", "algorithmId", "algorithmVersion",
          "status", "dataResidencyRegion", "inputSnapshot", "candidates"
        ],
        "properties": {
          "contractId":          { "type": "string", "enum": ["DC-MATCH-RECOMMENDATION-v1"] },
          "recommendationId":    { "type": "string", "pattern": "^REC-[0-9TZ:.-]+-ENC-[0-9-]+$" },
          "encounterId":         { "type": "string", "pattern": "^ENC-[0-9]{4}-[0-9]{4,}$" },
          "organizationId":      { "type": "string", "pattern": "^ORG-[A-Z0-9-]+$" },
          "generatedAt":         { "type": "string", "format": "date-time" },
          "validUntil":          { "type": "string", "format": "date-time" },
          "algorithmId":         { "type": "string", "pattern": "^[a-z][a-z0-9-]+$" },
          "algorithmVersion":    { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
          "status":              { "type": "string", "enum": ["advisory"] },
          "dataResidencyRegion": { "type": "string", "enum": ["switzerlandnorth", "switzerlandwest"] },
          "inputSnapshot": {
            "type": "object",
            "additionalProperties": false,
            "required": ["encounterAsOf", "supplyAsOf", "consideredStationIds"],
            "properties": {
              "encounterAsOf":         { "type": "string", "format": "date-time" },
              "supplyAsOf":            { "type": "string", "format": "date-time" },
              "consideredStationIds":  { "type": "array", "items": { "type": "string", "pattern": "^LOC-[A-Z0-9-]+$" } },
              "excludedStationIds": {
                "type": "array",
                "items": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": ["stationId", "reason"],
                  "properties": {
                    "stationId": { "type": "string", "pattern": "^LOC-[A-Z0-9-]+$" },
                    "reason":    { "type": "string", "enum": [
                      "specialty-mismatch", "hard-characteristic-missing",
                      "capacity-zero", "ward-suspended", "ward-inactive"
                    ]}
                  }
                }
              }
            }
          },
          "candidates": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "rank", "stationLocationId", "recommendedBedLocationId",
                "fitScore", "capacityHeadroom",
                "expectedAdmitWindowStart", "expectedAdmitWindowEnd",
                "explanationFactors", "hardConstraintsMet"
              ],
              "properties": {
                "rank":                     { "type": "integer", "minimum": 1, "maximum": 5 },
                "stationLocationId":        { "type": "string", "pattern": "^LOC-[A-Z0-9-]+$" },
                "recommendedBedLocationId": { "type": ["string", "null"], "pattern": "^LOC-[A-Z0-9-]+$" },
                "fitScore":                 { "type": "number", "minimum": 0, "maximum": 1 },
                "capacityHeadroom":         { "type": "integer", "minimum": 0, "maximum": 2000 },
                "expectedAdmitWindowStart": { "type": "string", "format": "date-time" },
                "expectedAdmitWindowEnd":   { "type": "string", "format": "date-time" },
                "explanationFactors": {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "additionalProperties": false,
                    "required": ["factor", "weight"],
                    "properties": {
                      "factor":   { "type": "string", "enum": [
                        "specialty-match", "capacity-headroom",
                        "characteristic-match", "admit-window-fit",
                        "acuity-fit", "partial-characteristic-match"
                      ]},
                      "weight":   { "type": "number", "minimum": 0, "maximum": 1 },
                      "evidence": { "type": "string" }
                    }
                  }
                },
                "bedFitFactors": {
                  "type": "array",
                  "items": { "type": "string", "enum": [
                    "single-room-available", "isolation-capable",
                    "monitoring-equipped", "bariatric-equipped",
                    "last-cleaned-within-2h", "gender-constraint-met"
                  ]}
                },
                "hardConstraintsMet": { "type": "boolean" },
                "softConstraintGaps": { "type": "array", "items": { "type": "string" } }
              }
            }
          },
          "extensions": { "type": "object" }
        }
      }
    }
  }
}
```

- [ ] **Step 5.5: Re-run schema tests, confirm pass**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.MatchRecommendationSchemaTests -v
```

Expected: 3 tests pass.

- [ ] **Step 5.6: Write failing invariants tests**

Append to `test_planning_contracts.py`:

```python
class RecommendationInvariantsTests(unittest.TestCase):
    def _record(self):
        return {
            "recommendationId": "REC-1",
            "generatedAt": "2026-06-12T08:00:00Z",
            "validUntil":  "2026-06-12T08:30:00Z",
            "candidates": [
                {"rank": 1, "fitScore": 0.9, "hardConstraintsMet": True,
                 "recommendedBedLocationId": None,
                 "explanationFactors": [
                     {"factor": "specialty-match", "weight": 0.7},
                     {"factor": "capacity-headroom", "weight": 0.3}]},
                {"rank": 2, "fitScore": 0.7, "hardConstraintsMet": True,
                 "recommendedBedLocationId": None,
                 "explanationFactors": [
                     {"factor": "specialty-match", "weight": 1.0}]},
            ],
        }

    def test_well_formed_passes(self):
        report = vd.GateReport()
        vd.check_recommendation_invariants([self._record()], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))

    def test_ranks_must_be_dense_and_ascending(self):
        rec = self._record()
        rec["candidates"][1]["rank"] = 3  # gap
        report = vd.GateReport()
        vd.check_recommendation_invariants([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_fitscore_must_be_non_increasing(self):
        rec = self._record()
        rec["candidates"][0]["fitScore"] = 0.5
        rec["candidates"][1]["fitScore"] = 0.9
        report = vd.GateReport()
        vd.check_recommendation_invariants([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_weights_must_sum_to_one(self):
        rec = self._record()
        rec["candidates"][0]["explanationFactors"][0]["weight"] = 0.3
        rec["candidates"][0]["explanationFactors"][1]["weight"] = 0.3
        report = vd.GateReport()
        vd.check_recommendation_invariants([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_hard_constraints_must_be_met(self):
        rec = self._record()
        rec["candidates"][0]["hardConstraintsMet"] = False
        report = vd.GateReport()
        vd.check_recommendation_invariants([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_valid_until_staleness_bound(self):
        rec = self._record()
        rec["validUntil"] = "2026-06-12T10:00:00Z"  # 2h after generatedAt > 60min
        report = vd.GateReport()
        vd.check_recommendation_invariants([rec], "ds", report)
        self.assertTrue(any(not r.passed for r in report.results))
```

- [ ] **Step 5.7: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.RecommendationInvariantsTests -v
```

Expected: tests fail (`AttributeError`).

- [ ] **Step 5.8: Implement `check_recommendation_invariants`**

Add to `validate_datasets.py`:

```python
def check_recommendation_invariants(records: list[dict], dataset_id: str,
                                    report: GateReport) -> None:
    """Validate DC-MATCH-RECOMMENDATION-v1 invariants (spec §7.5)."""
    failures = 0
    for rec in records:
        rec_id = rec.get("recommendationId", "<unknown>")
        candidates = rec.get("candidates") or []

        # Rule 2: dense, ascending ranks; non-increasing fitScore.
        ranks = [c.get("rank") for c in candidates]
        if ranks != list(range(1, len(candidates) + 1)):
            report.add(CheckResult("NFR-AI-003", "high", False,
                f"Recommendation {rec_id!r} ranks must be 1..N dense ascending; got {ranks}.",
                dataset_id))
            failures += 1
        scores = [c.get("fitScore", 0) for c in candidates]
        if any(scores[i] < scores[i + 1] for i in range(len(scores) - 1)):
            report.add(CheckResult("NFR-AI-003", "high", False,
                f"Recommendation {rec_id!r} fitScore must be non-increasing; got {scores}.",
                dataset_id))
            failures += 1

        for c in candidates:
            # Rule 6: all included candidates must satisfy hard constraints.
            if c.get("hardConstraintsMet") is not True:
                report.add(CheckResult("NFR-AI-004", "high", False,
                    f"Recommendation {rec_id!r} candidate rank {c.get('rank')} "
                    "hardConstraintsMet=False (must be excluded).", dataset_id))
                failures += 1
            # Rule 8: weights sum ~= 1.0.
            weights = [f.get("weight", 0) for f in (c.get("explanationFactors") or [])]
            total = sum(weights)
            if abs(total - 1.0) > 0.01:
                report.add(CheckResult("NFR-AI-004", "high", False,
                    f"Recommendation {rec_id!r} candidate rank {c.get('rank')} "
                    f"explanationFactors weight sum {total:.3f} != 1.0.", dataset_id))
                failures += 1

        # Rule 7: validUntil > generatedAt and diff <= 60 min (MVP).
        gen = rec.get("generatedAt")
        val = rec.get("validUntil")
        if gen and val:
            try:
                g = _dt.datetime.strptime(gen.rstrip("Z").split(".")[0],
                                          "%Y-%m-%dT%H:%M:%S")
                v = _dt.datetime.strptime(val.rstrip("Z").split(".")[0],
                                          "%Y-%m-%dT%H:%M:%S")
                if v <= g:
                    report.add(CheckResult("NFR-AI-003", "high", False,
                        f"Recommendation {rec_id!r} validUntil <= generatedAt.",
                        dataset_id))
                    failures += 1
                elif (v - g).total_seconds() > 60 * 60:
                    report.add(CheckResult("NFR-AI-003", "high", False,
                        f"Recommendation {rec_id!r} staleness window > 60 minutes.",
                        dataset_id))
                    failures += 1
            except ValueError:
                pass  # date-time format check already runs in schema validation

    if failures == 0:
        report.add(CheckResult("NFR-AI-003", "low", True,
            "Recommendation invariants OK.", dataset_id))
```

- [ ] **Step 5.9: Wire the lane into `validate_dataset` dispatch**

```python
    if entry.get("lane") == "planning-match-recommendation":
        check_recommendation_invariants(records, dataset_id, report)
        check_planning_phi_denylist(records, dataset_id, report)
```

- [ ] **Step 5.10: Create seed dataset fixture**

Create `data/synthetic/datasets/dc-match-recommendation-v1.sample.json`:

```json
{
  "datasetId": "DS-MATCH-REC-sit-2026-06-12",
  "contractId": "DC-MATCH-RECOMMENDATION-v1",
  "contractVersion": "1.0.0",
  "classification": "operational-confidential",
  "residency": "CH",
  "records": [
    {
      "contractId": "DC-MATCH-RECOMMENDATION-v1",
      "recommendationId": "REC-2026-06-12T08:00:00Z-ENC-2026-0001",
      "encounterId": "ENC-2026-0001",
      "organizationId": "ORG-HIRSLANDEN",
      "generatedAt": "2026-06-12T08:00:00Z",
      "validUntil":  "2026-06-12T08:30:00Z",
      "algorithmId": "stub-rules-v1",
      "algorithmVersion": "1.0.0",
      "status": "advisory",
      "dataResidencyRegion": "switzerlandnorth",
      "inputSnapshot": {
        "encounterAsOf": "2026-06-12T08:00:00Z",
        "supplyAsOf":    "2026-06-12T08:00:00Z",
        "consideredStationIds": ["LOC-HIRSL-WARD-01"]
      },
      "candidates": [
        {
          "rank": 1,
          "stationLocationId": "LOC-HIRSL-WARD-01",
          "recommendedBedLocationId": "LOC-HIRSL-BED-001",
          "fitScore": 0.92,
          "capacityHeadroom": 5,
          "expectedAdmitWindowStart": "2026-06-14T08:00:00Z",
          "expectedAdmitWindowEnd":   "2026-06-14T14:00:00Z",
          "explanationFactors": [
            {"factor": "specialty-match",       "weight": 0.5},
            {"factor": "capacity-headroom",     "weight": 0.3},
            {"factor": "characteristic-match",  "weight": 0.2}
          ],
          "bedFitFactors": ["single-room-available", "monitoring-equipped"],
          "hardConstraintsMet": true
        }
      ]
    }
  ]
}
```

- [ ] **Step 5.11: Add traceability entry**

Append to `traceability.json`:

```json
{
  "datasetId": "DS-MATCH-REC-sit-2026-06-12",
  "lane": "planning-match-recommendation",
  "providerScope": "none",
  "dataFile": "datasets/dc-match-recommendation-v1.sample.json",
  "schemaFile": "schema/dc-match-recommendation-v1.schema.json",
  "minimizationChecked": false,
  "fr": ["FR-DATA-002", "FR-DATA-005", "FR-DATA-008"],
  "nfr": ["NFR-AI-003", "NFR-AI-004", "NFR-COMP-011"],
  "ch": ["CH-C01", "CH-C03", "CH-C05"],
  "rv": ["RV-06-10"]
}
```

- [ ] **Step 5.12: Run all tests + e2e gate**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts -v
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: all green.

- [ ] **Step 5.13: Commit**

```powershell
git add data/synthetic/schema/dc-match-recommendation-v1.schema.json `
        data/synthetic/datasets/dc-match-recommendation-v1.sample.json `
        data/synthetic/traceability.json `
        data/synthetic/validate_datasets.py `
        data/synthetic/tests/test_planning_contracts.py `
        data/synthetic/tests/test_validate_datasets.py
git commit -m "feat(data): add DC-MATCH-RECOMMENDATION-v1 contract with invariants validator"
```

---

## Task 6: Cross-contract FK + residency + bed-required-when-supply checks

**Files:**
- Modify: `data/synthetic/validate_datasets.py` — add `check_planning_cross_contract`
- Modify: `data/synthetic/tests/test_planning_contracts.py` — `CrossContractTests`

- [ ] **Step 6.1: Write failing cross-contract tests**

Append to `test_planning_contracts.py`:

```python
class CrossContractTests(unittest.TestCase):
    def _bundle(self):
        return {
            "organizations": [{"organizationId": "ORG-X",
                               "dataResidencyRegion": "switzerlandnorth"}],
            "locations": [
                {"locationId": "LOC-S", "physicalType": "si",
                 "organizationId": "ORG-X", "partOfId": None},
                {"locationId": "LOC-W", "physicalType": "wa",
                 "organizationId": "ORG-X", "partOfId": "LOC-S",
                 "specialtyServiceIds": ["HCS-X"],
                 "healthcareServices": [
                   {"healthcareServiceId": "HCS-X", "specialty": "cardiology",
                    "specialtyTaxonomyVersion": "1.0.0", "category": "inpatient"}]}
            ],
            "encounters": [
                {"encounterId": "ENC-1", "organizationId": "ORG-X",
                 "requestedSpecialtyServiceId": "HCS-X",
                 "dataResidencyRegion": "switzerlandnorth"}
            ],
            "recommendations": [
                {"recommendationId": "REC-1", "encounterId": "ENC-1",
                 "organizationId": "ORG-X",
                 "dataResidencyRegion": "switzerlandnorth",
                 "candidates": [
                   {"rank": 1, "stationLocationId": "LOC-W",
                    "recommendedBedLocationId": None}
                 ]}
            ],
        }

    def test_well_formed_passes(self):
        report = vd.GateReport()
        vd.check_planning_cross_contract(self._bundle(), report)
        self.assertTrue(all(r.passed for r in report.results))

    def test_encounter_org_must_exist(self):
        b = self._bundle()
        b["encounters"][0]["organizationId"] = "ORG-MISSING"
        report = vd.GateReport()
        vd.check_planning_cross_contract(b, report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_encounter_specialty_must_resolve(self):
        b = self._bundle()
        b["encounters"][0]["requestedSpecialtyServiceId"] = "HCS-NOPE"
        report = vd.GateReport()
        vd.check_planning_cross_contract(b, report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_recommendation_station_must_be_ward(self):
        b = self._bundle()
        b["recommendations"][0]["candidates"][0]["stationLocationId"] = "LOC-S"
        report = vd.GateReport()
        vd.check_planning_cross_contract(b, report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_residency_mismatch_detected(self):
        b = self._bundle()
        b["encounters"][0]["dataResidencyRegion"] = "switzerlandwest"
        report = vd.GateReport()
        vd.check_planning_cross_contract(b, report)
        self.assertTrue(any(not r.passed for r in report.results))

    def test_bed_required_when_supply_emits_beds(self):
        b = self._bundle()
        b["locations"].append({"locationId": "LOC-B", "physicalType": "bd",
                               "organizationId": "ORG-X", "partOfId": "LOC-W"})
        # Recommendation still has recommendedBedLocationId=None — must fail.
        report = vd.GateReport()
        vd.check_planning_cross_contract(b, report)
        self.assertTrue(any(not r.passed for r in report.results))
```

- [ ] **Step 6.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.CrossContractTests -v
```

Expected: tests fail (`AttributeError`).

- [ ] **Step 6.3: Implement `check_planning_cross_contract`**

Add to `validate_datasets.py`:

```python
def check_planning_cross_contract(bundle: dict, report: GateReport) -> None:
    """Cross-contract validation for the Sprint 07 planning data product.

    `bundle` is a dict with keys: organizations, locations, encounters,
    recommendations — each a flat list of record dicts (as found under
    `records[]` in the four planning datasets)."""
    orgs = {o["organizationId"]: o for o in bundle.get("organizations", [])}
    locs = {l["locationId"]: l for l in bundle.get("locations", [])}
    services = {
        s["healthcareServiceId"]: s
        for l in bundle.get("locations", [])
        for s in (l.get("healthcareServices") or [])
    }
    org_emits_beds = {l["organizationId"] for l in bundle.get("locations", [])
                      if l.get("physicalType") == "bd"}
    failures = 0

    # Encounter → Organization, Encounter → HealthcareService, residency match.
    for enc in bundle.get("encounters", []):
        eid = enc.get("encounterId", "<unknown>")
        org_id = enc.get("organizationId")
        if org_id not in orgs:
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Encounter {eid!r} organizationId {org_id!r} not found.", eid))
            failures += 1
        elif orgs[org_id].get("dataResidencyRegion") != enc.get("dataResidencyRegion"):
            report.add(CheckResult("CH-C05", "high", False,
                f"Encounter {eid!r} dataResidencyRegion mismatches its Organization.", eid))
            failures += 1
        svc = enc.get("requestedSpecialtyServiceId")
        if svc not in services:
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Encounter {eid!r} requestedSpecialtyServiceId {svc!r} does not resolve.",
                eid))
            failures += 1

    # Recommendation → Encounter + Station (+ Bed).
    enc_ids = {e["encounterId"] for e in bundle.get("encounters", [])}
    for rec in bundle.get("recommendations", []):
        rid = rec.get("recommendationId", "<unknown>")
        if rec.get("encounterId") not in enc_ids:
            report.add(CheckResult("NFR-DQ-005", "high", False,
                f"Recommendation {rid!r} encounterId not found.", rid))
            failures += 1
        org_id = rec.get("organizationId")
        if org_id in orgs and orgs[org_id].get("dataResidencyRegion") != rec.get("dataResidencyRegion"):
            report.add(CheckResult("CH-C05", "high", False,
                f"Recommendation {rid!r} dataResidencyRegion mismatches its Organization.",
                rid))
            failures += 1
        for c in rec.get("candidates", []):
            station = locs.get(c.get("stationLocationId"))
            if station is None or station.get("physicalType") != "wa":
                report.add(CheckResult("NFR-AI-004", "high", False,
                    f"Recommendation {rid!r} candidate rank {c.get('rank')} "
                    "stationLocationId must reference a ward.", rid))
                failures += 1
            bed_id = c.get("recommendedBedLocationId")
            if org_id in org_emits_beds and bed_id is None:
                report.add(CheckResult("NFR-AI-004", "high", False,
                    f"Recommendation {rid!r} candidate rank {c.get('rank')} "
                    "must include recommendedBedLocationId when supply emits beds.",
                    rid))
                failures += 1
            if bed_id is not None:
                bed = locs.get(bed_id)
                if bed is None or bed.get("physicalType") != "bd":
                    report.add(CheckResult("NFR-AI-004", "high", False,
                        f"Recommendation {rid!r} bed {bed_id!r} not found or not a bed.",
                        rid))
                    failures += 1
                elif bed.get("partOfId") != c.get("stationLocationId"):
                    report.add(CheckResult("NFR-AI-004", "high", False,
                        f"Recommendation {rid!r} bed {bed_id!r} does not belong to "
                        f"station {c.get('stationLocationId')!r}.", rid))
                    failures += 1

    if failures == 0:
        report.add(CheckResult("NFR-DQ-005", "low", True,
            "Cross-contract FK + residency + bed-requirement checks OK.",
            "planning-bundle"))
```

- [ ] **Step 6.4: Run unit tests**

```powershell
python -m unittest data.synthetic.tests.test_planning_contracts.CrossContractTests -v
```

Expected: 6 tests pass.

- [ ] **Step 6.5: Hook the cross-contract check into the gate**

In `validate_datasets.py` `run(root)`, after the per-dataset loop, add:

```python
    # Sprint 07 planning data product cross-contract checks.
    bundle = {"organizations": [], "locations": [],
              "encounters": [], "recommendations": []}
    lane_to_key = {
        "planning-supply-organization": "organizations",
        "planning-supply-location":     "locations",
        "planning-demand-encounter":    "encounters",
        "planning-match-recommendation":"recommendations",
    }
    for entry in traceability["datasets"]:
        key = lane_to_key.get(entry.get("lane"))
        if not key:
            continue
        data = _load_json(os.path.join(root, entry["dataFile"]))
        bundle[key].extend(data.get("records", []))
    if any(bundle.values()):
        check_planning_cross_contract(bundle, report)
```

- [ ] **Step 6.6: Run end-to-end gate**

```powershell
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: `pass`; the cross-contract check appears in the report.

- [ ] **Step 6.7: Commit**

```powershell
git add data/synthetic/validate_datasets.py data/synthetic/tests/test_planning_contracts.py
git commit -m "feat(data): cross-contract FK, residency, and bed-required-when-supply validator"
```

---

## Task 7: Generator script — Organizations + Locations (Site/Ward/Bed)

**Files:**
- Create: `data/synthetic/generate_planning_datasets.py`
- Create: `data/synthetic/tests/test_generate_planning_datasets.py`

- [ ] **Step 7.1: Write failing generator tests**

Create `data/synthetic/tests/test_generate_planning_datasets.py`:

```python
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
        # 2 organizations * 1 site * 2 stations * 3 beds = 12
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
```

- [ ] **Step 7.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets -v
```

Expected: `ImportError` — module not yet created.

- [ ] **Step 7.3: Create the generator skeleton with Organization + Location builders**

Create `data/synthetic/generate_planning_datasets.py`:

```python
#!/usr/bin/env python3
"""Sprint 07 planning datasets generator.

Builds four pseudonymised synthetic datasets for the Patient Capacity
Planning data product:

  * DC-SUPPLY-ORGANIZATION-v1
  * DC-SUPPLY-LOCATION-v1   (Site / Ward / Bed, recursive)
  * DC-DEMAND-ENCOUNTER-v1
  * DC-MATCH-RECOMMENDATION-v1  (via a deterministic stub matcher)

Pure Python stdlib; deterministic for a given --seed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import random
from dataclasses import dataclass, field, asdict


CONTRACT_VERSION = "1.0.0"
TAXONOMY_VERSION = "1.0.0"
RESIDENCY_REGIONS = ("switzerlandnorth", "switzerlandwest")
SPECIALTIES = (
    ("cardiology",    "inpatient"),
    ("orthopedics",   "surgical"),
    ("internal-med",  "inpatient"),
    ("neurology",     "inpatient"),
    ("oncology",      "inpatient"),
    ("rehab",         "rehab"),
)
BED_CHARACTERISTICS = (
    "single-room", "cardiac-monitoring", "isolation",
    "negative-pressure", "bariatric", "pediatric-equipped",
)
OPS_STATUS = ("U", "O", "H", "I", "K", "C")
DEFAULT_ORGS = (
    ("ORG-HIRSLANDEN",    "Klinik Hirslanden",   "CH-ZH", "switzerlandnorth"),
    ("ORG-ZOLLIKERBERG",  "Spital Zollikerberg", "CH-ZH", "switzerlandnorth"),
)


@dataclass
class GeneratorConfig:
    organizations:    int = 2
    sites_per_org:    int = 2
    stations_per_site:int = 6
    beds_per_station: int = 12
    with_beds:        bool = False
    encounters:       int = 500
    horizon_days:     int = 14
    seed:             int = 42
    as_of:            str = "2026-06-12T08:00:00Z"


def _rng(cfg: GeneratorConfig, salt: str) -> random.Random:
    """Deterministic per-purpose RNG so adding new builders never re-shuffles
    earlier ones (avoids fixture churn)."""
    seed = int(hashlib.sha256(f"{cfg.seed}:{salt}".encode()).hexdigest(), 16)
    return random.Random(seed & 0xFFFFFFFF)


def build_organizations(cfg: GeneratorConfig) -> list[dict]:
    records = []
    for org_id, name, canton, region in DEFAULT_ORGS[: cfg.organizations]:
        records.append({
            "contractId": "DC-SUPPLY-ORGANIZATION-v1",
            "organizationId": org_id,
            "name": name,
            "organizationType": "prov",
            "active": True,
            "country": "CH",
            "canton": canton,
            "dataResidencyRegion": region,
        })
    return records


def build_locations(cfg: GeneratorConfig) -> list[dict]:
    rng = _rng(cfg, "locations")
    records: list[dict] = []
    for org_id, _, _, _ in DEFAULT_ORGS[: cfg.organizations]:
        org_short = org_id.split("-", 1)[1][:5]
        for s in range(1, cfg.sites_per_org + 1):
            site_id = f"LOC-{org_short}-SITE-{s:02d}"
            records.append({
                "contractId": "DC-SUPPLY-LOCATION-v1",
                "locationId": site_id,
                "organizationId": org_id,
                "physicalType": "si",
                "partOfId": None,
                "name": f"{org_short} Campus {s}",
                "status": "active",
                "asOfTimestamp": cfg.as_of,
            })
            for w in range(1, cfg.stations_per_site + 1):
                ward_id = f"LOC-{org_short}-WARD-{s:02d}{w:02d}"
                specialty, category = SPECIALTIES[(w - 1) % len(SPECIALTIES)]
                hcs_id = f"HCS-{specialty.upper()}-{s:02d}{w:02d}"
                beds_total = cfg.beds_per_station
                beds_available = rng.randint(0, beds_total)
                records.append({
                    "contractId": "DC-SUPPLY-LOCATION-v1",
                    "locationId": ward_id,
                    "organizationId": org_id,
                    "physicalType": "wa",
                    "partOfId": site_id,
                    "name": f"{specialty.title()} Ward {s}-{w}",
                    "status": "active",
                    "bedsTotal": beds_total,
                    "bedsAvailable": beds_available,
                    "specialtyServiceIds": [hcs_id],
                    "healthcareServices": [{
                        "healthcareServiceId": hcs_id,
                        "specialty": specialty,
                        "specialtyTaxonomyVersion": TAXONOMY_VERSION,
                        "category": category,
                    }],
                    "asOfTimestamp": cfg.as_of,
                })
                if cfg.with_beds:
                    for b in range(1, cfg.beds_per_station + 1):
                        bed_id = f"LOC-{org_short}-BED-{s:02d}{w:02d}{b:03d}"
                        chars = rng.sample(BED_CHARACTERISTICS,
                                           k=rng.randint(0, 2))
                        records.append({
                            "contractId": "DC-SUPPLY-LOCATION-v1",
                            "locationId": bed_id,
                            "organizationId": org_id,
                            "physicalType": "bd",
                            "partOfId": ward_id,
                            "name": f"Bed {s}-{w}-{b}",
                            "status": "active",
                            "operationalStatus": rng.choice(OPS_STATUS),
                            "characteristic": chars,
                            "asOfTimestamp": cfg.as_of,
                        })
    return records


def build_bundle(cfg: GeneratorConfig) -> dict:
    return {
        "organizations": build_organizations(cfg),
        "locations":     build_locations(cfg),
        "encounters":    [],          # filled in Task 8
        "recommendations":[],         # filled in Task 9
    }
```

- [ ] **Step 7.4: Run, confirm tests pass**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets -v
```

Expected: 4 tests pass.

- [ ] **Step 7.5: Commit**

```powershell
git add data/synthetic/generate_planning_datasets.py `
        data/synthetic/tests/test_generate_planning_datasets.py
git commit -m "feat(data): planning dataset generator scaffold with Organization and Location builders"
```

---

## Task 8: Generator — Encounter builder with lifecycle

**Files:**
- Modify: `data/synthetic/generate_planning_datasets.py` — add `build_encounters`
- Modify: `data/synthetic/tests/test_generate_planning_datasets.py` — `GeneratorEncounterTests`

- [ ] **Step 8.1: Write failing tests**

Append to `test_generate_planning_datasets.py`:

```python
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
        # Routine should dominate per spec §8.3 (60% target).
        self.assertGreater(counts["routine"], counts["urgent"])
        self.assertGreater(counts["urgent"], counts["asap"])
        self.assertGreater(counts["asap"], counts["stat"])

    def test_phi_denylist_clean(self):
        cfg = gen.GeneratorConfig(seed=42, encounters=20)
        bundle = gen.build_bundle(cfg)
        report = vd.GateReport()
        vd.check_planning_phi_denylist(bundle["encounters"], "ds", report)
        self.assertTrue(all(r.passed for r in report.results))
```

- [ ] **Step 8.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets.GeneratorEncounterTests -v
```

Expected: `test_default_encounter_count` fails (empty list).

- [ ] **Step 8.3: Implement `build_encounters`**

Append to `generate_planning_datasets.py`:

```python
ACUITY_WEIGHTS = [("routine", 60), ("urgent", 25), ("asap", 12), ("stat", 3)]
ADMISSION_TYPES = ("emergency", "elective", "transfer", "observation")
PURPOSE_TAGS = ("capacity-planning", "bed-management")


def _weighted_choice(rng: random.Random, weighted: list[tuple[str, int]]) -> str:
    total = sum(w for _, w in weighted)
    pick = rng.randint(1, total)
    cum = 0
    for value, weight in weighted:
        cum += weight
        if pick <= cum:
            return value
    return weighted[-1][0]


def _iso(ts: _dt.datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _pseudonym(rng: random.Random) -> str:
    return f"PID-{rng.randint(0, 0xFFFFFFFF):08X}"


def _build_status_history(rng: random.Random, start: _dt.datetime,
                          admission_type: str
                          ) -> tuple[str, list[dict], str | None]:
    """Return (final_status, history, last_locationId).

    Lifecycle subsets the spec state machine (§6.3); deterministic for a
    given RNG state."""
    history: list[dict] = []
    cursor = start - _dt.timedelta(days=2)

    history.append({"status": "planned", "periodStart": _iso(cursor),
                    "periodEnd": _iso(start), "locationId": None})
    cursor = start
    if admission_type == "emergency":
        triage_end = cursor + _dt.timedelta(minutes=rng.randint(15, 60))
        history.append({"status": "arrived", "periodStart": _iso(cursor),
                        "periodEnd": _iso(triage_end), "locationId": None})
        in_progress_start = triage_end + _dt.timedelta(minutes=rng.randint(10, 45))
        history.append({"status": "triaged", "periodStart": _iso(triage_end),
                        "periodEnd": _iso(in_progress_start), "locationId": None})
        cursor = in_progress_start
    else:
        cursor = cursor + _dt.timedelta(minutes=rng.randint(0, 30))

    # Roll the final status — 70% in-progress (open period), 30% finished.
    if rng.random() < 0.7:
        history.append({"status": "in-progress", "periodStart": _iso(cursor),
                        "periodEnd": None, "locationId": None})
        return "in-progress", history, None
    finished_at = cursor + _dt.timedelta(hours=rng.randint(8, 96))
    history.append({"status": "in-progress", "periodStart": _iso(cursor),
                    "periodEnd": _iso(finished_at), "locationId": None})
    history.append({"status": "finished", "periodStart": _iso(finished_at),
                    "periodEnd": None, "locationId": None})
    return "finished", history, None


def build_encounters(cfg: GeneratorConfig, locations: list[dict]) -> list[dict]:
    rng = _rng(cfg, "encounters")
    base = _dt.datetime.strptime(cfg.as_of.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    services_by_org: dict[str, list[dict]] = {}
    for loc in locations:
        for svc in loc.get("healthcareServices", []):
            services_by_org.setdefault(loc["organizationId"], []).append({
                "id": svc["healthcareServiceId"],
                "wardId": loc["locationId"],
            })

    org_ids = sorted(services_by_org.keys())
    records: list[dict] = []
    for i in range(1, cfg.encounters + 1):
        org_id = rng.choice(org_ids)
        svc = rng.choice(services_by_org[org_id])
        admission_type = rng.choice(ADMISSION_TYPES)
        arrival_offset = rng.randint(0, cfg.horizon_days * 24 * 60)
        arrival = base + _dt.timedelta(minutes=arrival_offset)
        status, history, _ = _build_status_history(rng, arrival, admission_type)
        records.append({
            "contractId": "DC-DEMAND-ENCOUNTER-v1",
            "encounterId": f"ENC-2026-{i:04d}",
            "pseudonymId": _pseudonym(rng),
            "organizationId": org_id,
            "class": "IMP",
            "status": status,
            "admissionType": admission_type,
            "requestedSpecialtyServiceId": svc["id"],
            "requiredCharacteristics": rng.sample(
                ["isolation", "cardiac-monitoring", "single-room"],
                k=rng.randint(0, 1)),
            "acuityBand": _weighted_choice(rng, ACUITY_WEIGHTS),
            "expectedArrivalTimestamp": _iso(arrival),
            "expectedLOSDays": rng.randint(1, 14),
            "statusHistory": history,
            "purposeTag": rng.choice(PURPOSE_TAGS),
            "dataResidencyRegion": "switzerlandnorth",
            "asOfTimestamp": cfg.as_of,
        })
    return records
```

Modify `build_bundle` to wire it:

```python
def build_bundle(cfg: GeneratorConfig) -> dict:
    organizations = build_organizations(cfg)
    locations     = build_locations(cfg)
    encounters    = build_encounters(cfg, locations)
    return {
        "organizations":   organizations,
        "locations":       locations,
        "encounters":      encounters,
        "recommendations": [],
    }
```

- [ ] **Step 8.4: Run encounter tests**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets.GeneratorEncounterTests -v
```

Expected: 4 tests pass.

- [ ] **Step 8.5: Commit**

```powershell
git add data/synthetic/generate_planning_datasets.py `
        data/synthetic/tests/test_generate_planning_datasets.py
git commit -m "feat(data): generator builds DC-DEMAND-ENCOUNTER-v1 records with lifecycle"
```

---

## Task 9: Generator — stub matcher + Recommendation builder + manifest

**Files:**
- Modify: `data/synthetic/generate_planning_datasets.py` — add `build_recommendations`, `build_manifest`, CLI entrypoint
- Modify: `data/synthetic/tests/test_generate_planning_datasets.py` — `RecommendationGeneratorTests`, `ManifestTests`

- [ ] **Step 9.1: Write failing tests**

Append to `test_generate_planning_datasets.py`:

```python
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
```

- [ ] **Step 9.2: Run, confirm failure**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets.RecommendationGeneratorTests data.synthetic.tests.test_generate_planning_datasets.ManifestTests -v
```

Expected: tests fail (`AttributeError`).

- [ ] **Step 9.3: Implement stub matcher, recommendation builder, manifest, and CLI**

Append to `generate_planning_datasets.py`:

```python
ALGORITHM_ID      = "stub-rules-v1"
ALGORITHM_VERSION = "1.0.0"
STALENESS_MIN     = 30  # minutes


def _bed_fit_factors(bed: dict) -> list[str]:
    factors = []
    chars = bed.get("characteristic", [])
    if "single-room" in chars:
        factors.append("single-room-available")
    if "cardiac-monitoring" in chars:
        factors.append("monitoring-equipped")
    if "isolation" in chars or "negative-pressure" in chars:
        factors.append("isolation-capable")
    if "bariatric" in chars:
        factors.append("bariatric-equipped")
    return factors or ["last-cleaned-within-2h"]


def _score_station(ward: dict, encounter: dict) -> tuple[float, list[dict]]:
    """Deterministic scoring — not an algorithm commitment."""
    factors: list[dict] = []
    specialty_match = ward["specialtyServiceIds"][0] == encounter["requestedSpecialtyServiceId"]
    headroom_norm = min(ward.get("bedsAvailable", 0) / max(ward.get("bedsTotal", 1), 1), 1.0)
    required = set(encounter.get("requiredCharacteristics", []))
    bed_chars = set()  # ward-level characteristics not modelled in MVP
    char_match = 1.0 if not required else (1.0 if required.issubset(bed_chars | {"isolation", "cardiac-monitoring", "single-room"}) else 0.5)

    weights = [
        ("specialty-match",      0.5 if specialty_match else 0.0),
        ("capacity-headroom",    0.3 * headroom_norm),
        ("characteristic-match", 0.2 * char_match),
    ]
    total = sum(w for _, w in weights) or 1.0
    # Renormalise so weights sum to 1.0.
    norm = [{"factor": f, "weight": round(w / total, 4)} for f, w in weights]
    return round(total, 4), norm


def build_recommendations(cfg: GeneratorConfig, bundle: dict) -> list[dict]:
    locs = bundle["locations"]
    org_emits_beds = {l["organizationId"] for l in locs if l["physicalType"] == "bd"}
    wards_by_org: dict[str, list[dict]] = {}
    beds_by_ward: dict[str, list[dict]] = {}
    for loc in locs:
        if loc["physicalType"] == "wa":
            wards_by_org.setdefault(loc["organizationId"], []).append(loc)
        elif loc["physicalType"] == "bd":
            beds_by_ward.setdefault(loc["partOfId"], []).append(loc)

    rng = _rng(cfg, "recommendations")
    gen_at = _dt.datetime.strptime(cfg.as_of.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    valid_until = gen_at + _dt.timedelta(minutes=STALENESS_MIN)
    results: list[dict] = []
    for enc in bundle["encounters"]:
        org_id = enc["organizationId"]
        candidate_wards = [w for w in wards_by_org.get(org_id, [])
                           if w["specialtyServiceIds"][0] == enc["requestedSpecialtyServiceId"]]
        if not candidate_wards:
            continue
        considered_ids = [w["locationId"] for w in candidate_wards]
        scored = [(w, *_score_station(w, enc)) for w in candidate_wards]
        scored.sort(key=lambda t: t[1], reverse=True)
        top = scored[:5]
        arrival = _dt.datetime.strptime(enc["expectedArrivalTimestamp"].rstrip("Z"),
                                        "%Y-%m-%dT%H:%M:%S")

        candidates = []
        for rank, (ward, score, factors) in enumerate(top, start=1):
            bed = None
            if org_id in org_emits_beds:
                available = [b for b in beds_by_ward.get(ward["locationId"], [])
                             if b.get("operationalStatus") == "U"]
                bed = available[0] if available else beds_by_ward.get(ward["locationId"], [None])[0]
            candidate = {
                "rank": rank,
                "stationLocationId": ward["locationId"],
                "recommendedBedLocationId": bed["locationId"] if bed else None,
                "fitScore": score,
                "capacityHeadroom": ward.get("bedsAvailable", 0),
                "expectedAdmitWindowStart": _iso(arrival),
                "expectedAdmitWindowEnd": _iso(arrival + _dt.timedelta(hours=6)),
                "explanationFactors": factors,
                "hardConstraintsMet": True,
            }
            if bed:
                candidate["bedFitFactors"] = _bed_fit_factors(bed)
            candidates.append(candidate)

        if not candidates:
            continue

        results.append({
            "contractId": "DC-MATCH-RECOMMENDATION-v1",
            "recommendationId": f"REC-{cfg.as_of}-{enc['encounterId']}",
            "encounterId": enc["encounterId"],
            "organizationId": org_id,
            "generatedAt": cfg.as_of,
            "validUntil": _iso(valid_until),
            "algorithmId": ALGORITHM_ID,
            "algorithmVersion": ALGORITHM_VERSION,
            "status": "advisory",
            "dataResidencyRegion": enc["dataResidencyRegion"],
            "inputSnapshot": {
                "encounterAsOf": enc["asOfTimestamp"],
                "supplyAsOf":    cfg.as_of,
                "consideredStationIds": considered_ids,
            },
            "candidates": candidates,
        })
    return results


def build_manifest(cfg: GeneratorConfig, bundle: dict) -> dict:
    return {
        "manifestVersion": "1.0.0",
        "generatedAt": cfg.as_of,
        "seed": cfg.seed,
        "config": asdict(cfg),
        "counts": {k: len(v) for k, v in bundle.items()},
        "checksums": {
            k: hashlib.sha256(
                json.dumps(v, sort_keys=True).encode()
            ).hexdigest()
            for k, v in bundle.items()
        },
    }


def _wrap_dataset(records: list[dict], contract_id: str,
                  dataset_id: str, ds_prefix: str) -> dict:
    return {
        "datasetId": dataset_id,
        "contractId": contract_id,
        "contractVersion": CONTRACT_VERSION,
        "classification": "operational-confidential",
        "residency": "CH",
        "records": records,
    }


def write_datasets(cfg: GeneratorConfig, out_dir: str) -> dict:
    bundle = build_bundle(cfg)
    bundle["recommendations"] = build_recommendations(cfg, bundle)
    os.makedirs(out_dir, exist_ok=True)
    plan = [
        ("dc-supply-organization-v1.sample.json",
         "DC-SUPPLY-ORGANIZATION-v1",
         "DS-SUPPLY-ORG-sit-2026-06-12", bundle["organizations"]),
        ("dc-supply-location-v1.sample.json",
         "DC-SUPPLY-LOCATION-v1",
         "DS-SUPPLY-LOC-sit-2026-06-12", bundle["locations"]),
        ("dc-demand-encounter-v1.sample.json",
         "DC-DEMAND-ENCOUNTER-v1",
         "DS-DEMAND-ENC-sit-2026-06-12", bundle["encounters"]),
        ("dc-match-recommendation-v1.sample.json",
         "DC-MATCH-RECOMMENDATION-v1",
         "DS-MATCH-REC-sit-2026-06-12", bundle["recommendations"]),
    ]
    for fname, contract_id, ds_id, records in plan:
        payload = _wrap_dataset(records, contract_id, ds_id, "")
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=False)
            fh.write("\n")
    manifest = build_manifest(cfg, bundle)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return manifest


def _parse_args(argv: list[str] | None = None) -> GeneratorConfig:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--organizations",     type=int,  default=2)
    p.add_argument("--sites-per-org",     type=int,  default=2)
    p.add_argument("--stations-per-site", type=int,  default=6)
    p.add_argument("--beds-per-station",  type=int,  default=12)
    p.add_argument("--with-beds",         action="store_true")
    p.add_argument("--encounters",        type=int,  default=500)
    p.add_argument("--horizon-days",      type=int,  default=14)
    p.add_argument("--seed",              type=int,  default=42)
    p.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "datasets"))
    args = p.parse_args(argv)
    cfg = GeneratorConfig(
        organizations=args.organizations,
        sites_per_org=args.sites_per_org,
        stations_per_site=args.stations_per_site,
        beds_per_station=args.beds_per_station,
        with_beds=args.with_beds,
        encounters=args.encounters,
        horizon_days=args.horizon_days,
        seed=args.seed,
    )
    cfg.__dict__["_out_dir"] = args.out
    return cfg


def main(argv: list[str] | None = None) -> int:
    cfg = _parse_args(argv)
    out_dir = cfg.__dict__.pop("_out_dir")
    manifest = write_datasets(cfg, out_dir)
    print(json.dumps(manifest["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 9.4: Run all generator tests**

```powershell
python -m unittest data.synthetic.tests.test_generate_planning_datasets -v
```

Expected: all tests pass.

- [ ] **Step 9.5: Commit**

```powershell
git add data/synthetic/generate_planning_datasets.py `
        data/synthetic/tests/test_generate_planning_datasets.py
git commit -m "feat(data): stub matcher, recommendation builder, manifest, and CLI"
```

---

## Task 10: Regenerate the seed datasets from the generator + e2e gate

The hand-authored fixtures from Tasks 2–5 prove the contracts; we now replace them with deterministic generator output (`--seed 42 --with-beds --encounters 50`) so the committed sample matches what the generator produces. This avoids drift between docs, tests, and committed data.

- [ ] **Step 10.1: Regenerate**

```powershell
python data/synthetic/generate_planning_datasets.py `
    --with-beds --encounters 50 --seed 42 `
    --out data/synthetic/datasets
```

Expected output: a JSON block with non-zero counts for all four contracts.

- [ ] **Step 10.2: Diff the regenerated files**

```powershell
git diff --stat data/synthetic/datasets
```

Inspect that only the four planning sample files and `manifest.json` changed; nothing in Sprint 6 datasets.

- [ ] **Step 10.3: Run the full gate**

```powershell
python data/synthetic/validate_datasets.py --root data/synthetic
```

Expected: exit `0`; `pass`; new planning lanes show their checks; Sprint 6 datasets still pass.

- [ ] **Step 10.4: Run all unit tests**

```powershell
python -m unittest discover -s data/synthetic/tests -v
```

Expected: all green.

- [ ] **Step 10.5: Commit regenerated datasets**

```powershell
git add data/synthetic/datasets/dc-supply-organization-v1.sample.json `
        data/synthetic/datasets/dc-supply-location-v1.sample.json `
        data/synthetic/datasets/dc-demand-encounter-v1.sample.json `
        data/synthetic/datasets/dc-match-recommendation-v1.sample.json `
        data/synthetic/datasets/manifest.json
git commit -m "chore(data): regenerate planning datasets from generator with --seed 42 --with-beds"
```

---

## Task 11: Register the contracts in `docs/DATA.md` (MINOR bump)

**Why MINOR:** additive — four new contracts registered + deprecation note on `DC-ONB-CAPACITY-v1`. No anchor or ID renames (`.github/copilot-instructions.md` §9).

**Files:**
- Modify: `docs/DATA.md` — bump `Version`, update `Previous Version`, add a new "Planning data product contracts (Sprint 07)" subsection, add deprecation note row, and link to the spec.

- [ ] **Step 11.1: Read current header + relevant section**

```powershell
Select-String -Path docs/DATA.md -Pattern "^\| \*\*Version|DC-ONB-CAPACITY-v1" -Context 1,1
```

Identify current `Version` (assume `0.4.0` per session notes) and the contracts table.

- [ ] **Step 11.2: Bump header**

In `docs/DATA.md`, change the header block:

```markdown
| **Version** | 0.5.0 |
| **Date** | 2026-06-12 |
| ...
| **Previous Version** | 0.4.0 (Sprint 6 onboarding contracts) |
```

- [ ] **Step 11.3: Add a "Sprint 07 planning data product contracts" subsection**

Place this new subsection directly after the existing Sprint 6 contracts table:

```markdown
### Sprint 07 — Patient capacity planning data product contracts

| Contract ID | Role | CDM/FHIR source | Dataset |
| ----- | ----- | ----- | ----- |
| `DC-SUPPLY-ORGANIZATION-v1` | Tenancy and legal-entity catalog (Hospital) | `Organization` (Commoncore) | `datasets/dc-supply-organization-v1.sample.json` |
| `DC-SUPPLY-LOCATION-v1`     | Recursive supply hierarchy (Site/Ward/Bed)  | `Location` + embedded `HealthcareService` | `datasets/dc-supply-location-v1.sample.json` |
| `DC-DEMAND-ENCOUNTER-v1`    | Inpatient demand (`Encounter.class=IMP`)    | `Encounter` + `EncounterStatusHistory`     | `datasets/dc-demand-encounter-v1.sample.json` |
| `DC-MATCH-RECOMMENDATION-v1`| Ranked top-N candidate Stations (advisory)  | *(bespoke)*                                | `datasets/dc-match-recommendation-v1.sample.json` |

Design rationale, validator rules, partition-key strategy, and the deterministic stub matcher are documented in [docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](superpowers/specs/2026-06-12-patient-capacity-data-product-design.md).
```

- [ ] **Step 11.4: Add a deprecation note for `DC-ONB-CAPACITY-v1`**

Append a "Deprecations" subsection or table row:

```markdown
### Deprecations

| Contract | Superseded by | Removal | Notes |
| ----- | ----- | ----- | ----- |
| `DC-ONB-CAPACITY-v1` (incl. provider variants `*-HIRSLANDEN-v1`, `*-ZOLLIKERBERG-v1`) | `DC-SUPPLY-LOCATION-v1` + `DC-SUPPLY-ORGANIZATION-v1` | Later sprint — migration PR will move provider variants to `extensions.<provider>` on the new `Location` contract | Sprint 07 keeps both in place; CI continues to validate the deprecated contract until removal. |
```

- [ ] **Step 11.5: Verify markdown lint**

```powershell
npx --yes markdownlint-cli2 "docs/DATA.md"
```

Expected: no lint errors.

- [ ] **Step 11.6: Commit**

```powershell
git add docs/DATA.md
git commit -m "docs(data): register Sprint 07 planning contracts and deprecate DC-ONB-CAPACITY-v1 (MINOR)"
```

---

## Task 12: Sprint 06 terminology follow-up note

**Why:** the spec §13 risks table calls out that Sprint 06 docs still use "episode" loosely; per CDM the right term is `Encounter`. The rename is **a separate PR**, but we leave a tracked note so it isn't lost.

**Files:**
- Create: `docs/sprints/sprint-07/cdm-terminology-followup.md`

- [ ] **Step 12.1: Confirm the directory exists**

```powershell
Test-Path docs/sprints/sprint-07
```

If `False`, create it: `New-Item -ItemType Directory docs/sprints/sprint-07`.

- [ ] **Step 12.2: Create the note**

Create `docs/sprints/sprint-07/cdm-terminology-followup.md`:

```markdown
# Sprint 07 follow-up — CDM terminology alignment (Episode → Encounter)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | Urs Rüegg (with GitHub Copilot) |
| **Status** | Open (separate PR required) |
| **Previous Version** | — |

## Background

The Sprint 07 patient capacity data product spec ([docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](../../superpowers/specs/2026-06-12-patient-capacity-data-product-design.md), decision D-07) adopts Microsoft Healthcare CDM / HL7 FHIR R4 terminology. In FHIR, `EpisodeOfCare` denotes a **multi-Encounter care relationship** (e.g. a chronic-disease management programme), which is **not** what Sprint 06 documents meant when they said "episode".

Sprint 06 documents used "episode" to refer to a single hospitalisation, which is `Encounter` (`class=IMP`) in FHIR.

## Scope of the follow-up

A separate PR must:

1. Rename loose uses of "episode" to "encounter" (or "hospitalisation encounter") in:
   - `docs/PRD.md`
   - `docs/ARCHITECTURE.md`
   - `docs/SD.md`
   - `docs/DATA.md` (any pre-Sprint-07 prose still using "episode")
   - `docs/reviews/*-ama-sd-review.md` (only if pulled into a follow-up review)
2. Preserve `FR-*` / `NFR-*` IDs (no renames — that would force MAJOR doc bumps per `.github/copilot-instructions.md` §9).
3. Add a one-line glossary entry in `docs/DATA.md` clarifying `EpisodeOfCare` vs `Encounter`.

## Out of scope for this follow-up

- Renaming requirement IDs.
- Touching the Sprint 06 contracts `DC-ONB-PATIENT-v1` and `DC-ONB-CAPACITY-v1`.
- Reverting any decision recorded in `docs/adr/`.

## Acceptance criteria

- All Sprint-06-and-earlier prose uses "encounter" (or "hospitalisation encounter") where it refers to a single hospitalisation.
- Markdownlint and link checks pass.
- PR description references this follow-up note.
```

- [ ] **Step 12.3: Lint**

```powershell
npx --yes markdownlint-cli2 "docs/sprints/sprint-07/cdm-terminology-followup.md"
```

- [ ] **Step 12.4: Commit**

```powershell
git add docs/sprints/sprint-07/cdm-terminology-followup.md
git commit -m "docs(sprint-07): record CDM Episode->Encounter terminology follow-up"
```

---

## Task 13: PR-readiness sweep + final evidence

**Files:** none modified — final verification gate before PR.

- [ ] **Step 13.1: Re-run full test suite**

```powershell
python -m unittest discover -s data/synthetic/tests -v
```

Expected: all green; no skips.

- [ ] **Step 13.2: Re-run the validation gate and capture evidence**

```powershell
python data/synthetic/validate_datasets.py --root data/synthetic --output evidence-sprint-07-planning.json
Get-Content evidence-sprint-07-planning.json | Select-String -Pattern "result|criticalFailures"
```

Expected: `"result": "pass"` and `"criticalFailures": 0`. **Do not commit the evidence file** — it's an ephemeral CI artefact.

- [ ] **Step 13.3: Re-run markdown lint over edited docs**

```powershell
npx --yes markdownlint-cli2 "docs/DATA.md" "docs/sprints/sprint-07/cdm-terminology-followup.md" "docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md" "docs/superpowers/plans/2026-06-12-patient-capacity-data-product-implementation.md"
```

Expected: no errors.

- [ ] **Step 13.4: Confirm `traceability.json` validates**

```powershell
python -c "import json; json.load(open('data/synthetic/traceability.json'))"
```

Expected: silent (valid JSON).

- [ ] **Step 13.5: Cleanup ephemeral files**

```powershell
Remove-Item -ErrorAction SilentlyContinue evidence-sprint-07-planning.json
git status
```

Expected: working tree clean.

- [ ] **Step 13.6: Push and open PR**

```powershell
git push -u origin sprint-07/patient-capacity-data-product
```

PR description must list `FR-DATA-001`, `FR-DATA-002`, `FR-DATA-003`, `FR-DATA-005`, `FR-DATA-006`, `FR-DATA-008`, `FR-ONB-003`, `NFR-COMP-011`, `NFR-DQ-005`, `NFR-AI-003`, `NFR-AI-004`, `CH-C01`, `CH-C03`, `CH-C05`, AMA `ER-01`, and `ADR-0003` (per `.github/copilot-instructions.md` §6 PR Output Contract). Reference the spec, this plan, and the CDM terminology follow-up note.

---

## Self-review summary

1. **Spec coverage**
   - §3 Decisions D-01..D-10 → all baked into Tasks 2–5 (contract IDs, recursive Location, FHIR Encounter naming, ranked top-N with bed-level recommendation).
   - §4 Four contracts → Tasks 2 (Organization), 3 (Location), 4 (Encounter), 5 (Recommendation).
   - §4.2 Extensibility rules → `extensions` object permitted in every schema.
   - §4.3 Sprint 6 supersede note → Task 11 deprecation row.
   - §5/§6/§7 Validator rules → Task 3 `check_location_hierarchy`, Task 4 `check_encounter_lifecycle` + `check_planning_phi_denylist`, Task 5 `check_recommendation_invariants`, Task 6 `check_planning_cross_contract`.
   - §5.3/§6.6/§7.6 HPK strategies → documented in spec only; Sprint 07 does not provision Cosmos containers (spec §12 guard #1).
   - §8 Generator → Tasks 7–9.
   - §9 Validator extensions → Tasks 1 (generic), 3, 4, 5, 6 (contract-specific).
   - §10 Deliverables 1–10 → Tasks 2, 3, 4, 5, 9 (generator inc. stub matcher), 10 (datasets), 6 (validator extensions cross), 7-9 (validator tests via planning tests), 11 (DATA.md), 12 (terminology note). Deliverable 11 (the spec) is pre-existing.
   - §11 Requirements traceability → Task 13.6 PR-description checklist.
   - §12 Scope guards → no Cosmos / no real algorithm / no bed-level allocation / no DP-EPISODE / no Sprint-06 removal — all preserved.

2. **Placeholder scan** — no `TBD`/`TODO`/"implement later" entries; every code step has the actual code or exact command.

3. **Type consistency** — function names used across tasks are pinned: `check_location_hierarchy`, `check_encounter_lifecycle`, `check_planning_phi_denylist`, `check_recommendation_invariants`, `check_planning_cross_contract`, `build_organizations`, `build_locations`, `build_encounters`, `build_recommendations`, `build_bundle`, `build_manifest`, `write_datasets`, `GeneratorConfig`. Schema discriminator values `si`/`wa`/`bd` are consistent; contract IDs match the spec verbatim.

4. **Frequent commits** — 12 commits across 13 tasks (Task 13 is verification-only and produces no commit).
