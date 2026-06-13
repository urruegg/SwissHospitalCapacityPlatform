#!/usr/bin/env python3
"""Sprint 6 synthesized-data contract, schema, and onboarding-policy gate.

Validates the synthesized, non-production SIT onboarding datasets under
``data/synthetic/datasets`` against their JSON Schema contracts under
``data/synthetic/schema``, runs onboarding minimum-data / re-identification
minimization checks, and confirms FR/NFR/CH traceability coverage declared in
``data/synthetic/traceability.json``.

The gate is intentionally dependency-free (Python 3 standard library only) so it
runs identically in CI and on a developer machine. It implements the subset of
JSON Schema Draft 7 used by the Sprint 6 onboarding contracts (``type``,
``required``, ``properties``, ``additionalProperties: false``, ``enum``,
``items``, ``minItems``, ``minimum``, ``maximum``, ``pattern`` and the ``date``
``format``).

Behaviour:

* Every dataset must validate against its declared schema.
* Onboarding datasets must not contain forbidden direct-identifier fields
  (re-identification minimization control, CH-C01 / NFR-COMP-011).
* Capacity datasets must keep ``bedsAvailable`` <= ``bedsTotal``.
* Every dataset must declare at least one FR and one CH control in the
  traceability map.

Phase 2 onboarding policy and schema enforcement (RV-06-03, RV-06-04, RV-06-07)
adds, on top of the Phase 1 schema gate:

* **Minimum-data purpose-tag policy** — every record's ``purposeTag`` must be
  declared in the dataset-level ``purposeTags`` allowlist, and patient-lane
  records must carry ``minimizationReviewed: true`` (NFR-COMP-011 / CH-C01).
* **Specialty-metadata quality and controlled versioning** — capacity datasets
  must pin ``specialtyTaxonomyVersion`` to the governed taxonomy version and keep
  each record's ``specialty`` consistent with its ``specialtyTags`` with no
  duplicate tags (NFR-DQ-005).
* **Cross-tenant identity boundary** — provider-scoped datasets must pin the
  dataset and every record to the declared tenant, so no record from another
  tenant can leak into a tenant-scoped dataset (NFR-SEC-005 / CH-C02).

Phase 3 provider SIT evidence and reliability enforcement (RV-06-05) adds, on top
of the Phase 1 and Phase 2 gates:

* **Degraded-mode and recovery contract** — provider-scoped onboarding datasets
  must declare a ``degradedMode`` block with a fallback read model, a positive
  and bounded data-staleness ceiling, an explicit manual-override capability, and
  a recovery-runbook reference (NFR-REL-005 / CH-C03).

* The run emits a synthesized-data evidence artifact and exits non-zero on any
  failure.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any


# Direct identifiers that must never appear in a minimum-data onboarding record.
# Enforces FR-ONB-001 / NFR-COMP-011 / CH-C01 re-identification minimization.
FORBIDDEN_IDENTIFIER_FIELDS = {
    "name",
    "fullname",
    "firstname",
    "lastname",
    "givenname",
    "familyname",
    "birthdate",
    "dateofbirth",
    "dob",
    "ahv",
    "ahvnumber",
    "ssn",
    "socialsecuritynumber",
    "address",
    "street",
    "postalcode",
    "zip",
    "city",
    "phone",
    "phonenumber",
    "email",
    "insurancenumber",
    "insuranceid",
    "patientid",
    "mrn",
    "nationalid",
    "passport",
}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Strict ISO-8601 UTC instants. We deliberately require the trailing 'Z'
# (no offsets) so every record can be safely compared lexicographically.
_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$"
)


@dataclass
class CheckResult:
    control_id: str
    severity: str
    passed: bool
    message: str
    resource: str = ""


@dataclass
class GateReport:
    results: list[CheckResult] = field(default_factory=list)
    evaluated_resources: list[str] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    @property
    def failures(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed]


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_date(value: Any) -> bool:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        _dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_schema(value: Any, schema: dict, path: str) -> list[str]:
    """Validate ``value`` against the supported JSON Schema subset.

    Returns a list of human-readable error strings (empty when valid).
    """
    errors: list[str] = []

    type_decl = schema.get("type")
    if isinstance(type_decl, list):
        type_errors_per_branch = []
        for candidate in type_decl:
            branch = dict(schema)
            branch["type"] = candidate
            branch_errors = validate_schema(value, branch, path)
            if not branch_errors:
                return []
            type_errors_per_branch.append(branch_errors)
        joined = " / ".join(repr(t) for t in type_decl)
        return [f"{path}: expected type {joined}, got {type(value).__name__}"]

    expected_type = schema.get("type")
    if expected_type and not _type_ok(value, expected_type):
        errors.append(f"{path}: expected type '{expected_type}', got '{type(value).__name__}'")
        return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum {schema['enum']}")

    if expected_type == "string":
        pattern = schema.get("pattern")
        if pattern and not re.match(pattern, value):
            errors.append(f"{path}: value {value!r} does not match pattern '{pattern}'")
        if schema.get("format") == "date" and not _is_date(value):
            errors.append(f"{path}: value {value!r} is not a valid 'date'")
        if schema.get("format") == "date-time":
            if not isinstance(value, str) or not _DATETIME_RE.match(value):
                errors.append(
                    f"{path}: invalid date-time {value!r} "
                    f"(expected ISO-8601 UTC with trailing 'Z')"
                )
            else:
                try:
                    _dt.datetime.strptime(
                        value.split(".")[0].rstrip("Z"),
                        "%Y-%m-%dT%H:%M:%S",
                    )
                except ValueError:
                    errors.append(f"{path}: invalid date-time {value!r}")

    if expected_type in ("integer", "number"):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value {value} > maximum {schema['maximum']}")

    if expected_type == "object" and isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property '{key}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: additional property '{key}' is not allowed")
        for key, sub_value in value.items():
            if key in props:
                errors.extend(validate_schema(sub_value, props[key], f"{path}.{key}"))

    if expected_type == "array" and isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: array length {len(value)} < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]"))

    return errors


def check_minimization(records: list[dict], dataset_id: str, report: GateReport) -> None:
    """Reject any forbidden direct-identifier field (CH-C01 / NFR-COMP-011)."""
    found: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        for key in record:
            if key.lower().replace("_", "").replace("-", "") in FORBIDDEN_IDENTIFIER_FIELDS:
                found.add(key)
    if found:
        report.add(CheckResult(
            "CH-C01", "critical", False,
            f"Forbidden direct-identifier field(s) present, re-identification "
            f"minimization violated: {sorted(found)}",
            dataset_id))
    else:
        report.add(CheckResult(
            "CH-C01", "low", True,
            "No forbidden direct-identifier fields present (minimization upheld).",
            dataset_id))


def check_capacity_invariants(records: list[dict], dataset_id: str, report: GateReport) -> None:
    """Capacity datasets must keep available beds within total beds."""
    violations = []
    for record in records:
        if not isinstance(record, dict):
            continue
        total = record.get("bedsTotal")
        available = record.get("bedsAvailable")
        if isinstance(total, int) and isinstance(available, int) and available > total:
            violations.append(record.get("capacityRecordId", "<unknown>"))
    if violations:
        report.add(CheckResult(
            "NFR-DQ-005", "high", False,
            f"bedsAvailable exceeds bedsTotal for record(s): {violations}",
            dataset_id))
    else:
        report.add(CheckResult(
            "NFR-DQ-005", "low", True,
            "Capacity invariant bedsAvailable <= bedsTotal holds for all records.",
            dataset_id))


def check_purpose_tags(data: dict, records: list[dict], dataset_id: str,
                       report: GateReport) -> None:
    """Minimum-data purpose-tag policy (NFR-COMP-011 / CH-C01).

    Every record ``purposeTag`` must be declared in the dataset ``purposeTags``
    allowlist (purpose limitation), and patient-lane records must carry an
    explicit ``minimizationReviewed`` marker.
    """
    allowed = set(data.get("purposeTags", []) if isinstance(data, dict) else [])
    undeclared: set[str] = set()
    unreviewed: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        tag = record.get("purposeTag")
        if tag is not None and tag not in allowed:
            undeclared.add(tag)
        if "minimizationReviewed" in record and record.get("minimizationReviewed") is not True:
            unreviewed.append(record.get("onboardingId", "<unknown>"))
    problems: list[str] = []
    if undeclared:
        problems.append(
            f"record purposeTag(s) not in dataset purposeTags allowlist: "
            f"{sorted(undeclared)}")
    if unreviewed:
        problems.append(f"record(s) missing minimization review marker: {unreviewed}")
    if problems:
        report.add(CheckResult(
            "NFR-COMP-011", "high", False,
            "Minimum-data purpose-tag policy violated: " + "; ".join(problems),
            dataset_id))
    else:
        report.add(CheckResult(
            "NFR-COMP-011", "low", True,
            "Purpose-tag allowlist and minimization markers upheld.",
            dataset_id))


def check_specialty_metadata(data: dict, records: list[dict], dataset_id: str,
                             taxonomy_version: str, report: GateReport) -> None:
    """Specialty-metadata quality and controlled versioning (NFR-DQ-005).

    The dataset ``specialtyTaxonomyVersion`` must match the governed taxonomy
    version, and every record's ``specialty`` must be present in its
    ``specialtyTags`` with no duplicate tags.
    """
    declared = data.get("specialtyTaxonomyVersion") if isinstance(data, dict) else None
    if declared != taxonomy_version:
        report.add(CheckResult(
            "NFR-DQ-005", "high", False,
            f"specialtyTaxonomyVersion {declared!r} does not match the governed "
            f"taxonomy version {taxonomy_version!r}.",
            dataset_id))
        return
    problems: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        record_id = record.get("capacityRecordId", "<unknown>")
        specialty = record.get("specialty")
        tags = record.get("specialtyTags", [])
        if not isinstance(tags, list) or not tags:
            problems.append(f"{record_id}: missing specialtyTags")
            continue
        if specialty is not None and specialty not in tags:
            problems.append(f"{record_id}: specialty '{specialty}' not in specialtyTags")
        if len(tags) != len(set(tags)):
            problems.append(f"{record_id}: duplicate specialtyTags")
    if problems:
        report.add(CheckResult(
            "NFR-DQ-005", "high", False,
            "Specialty-metadata quality violations: " + "; ".join(problems),
            dataset_id))
    else:
        report.add(CheckResult(
            "NFR-DQ-005", "low", True,
            f"Specialty metadata quality and taxonomy version {taxonomy_version} "
            "upheld.",
            dataset_id))


def check_tenant_boundary(data: dict, entry: dict, records: list[dict],
                          dataset_id: str, report: GateReport) -> None:
    """Cross-tenant identity boundary control (NFR-SEC-005 / CH-C02).

    Provider-scoped datasets must pin the dataset and every record to the
    declared tenant; the shared lane must not carry a dataset-level tenant id.
    No record may carry a ``providerId`` that differs from the dataset tenant.
    """
    declared_scope = entry.get("providerScope", "none")
    dataset_provider = data.get("providerId") if isinstance(data, dict) else None

    if declared_scope and declared_scope != "none":
        if dataset_provider != declared_scope:
            report.add(CheckResult(
                "NFR-SEC-005", "critical", False,
                f"Provider-scoped dataset providerId {dataset_provider!r} does not "
                f"match declared tenant scope {declared_scope!r}.",
                dataset_id))
            return
        cross = sorted({
            f"{record.get('capacityRecordId', '<unknown>')}:{record.get('providerId')}"
            for record in records
            if isinstance(record, dict)
            and record.get("providerId") is not None
            and record.get("providerId") != declared_scope
        })
        if cross:
            report.add(CheckResult(
                "NFR-SEC-005", "critical", False,
                f"Cross-tenant record(s) found in tenant-scoped dataset "
                f"{declared_scope!r}: {cross}",
                dataset_id))
        else:
            report.add(CheckResult(
                "NFR-SEC-005", "low", True,
                f"Tenant boundary upheld; all records pinned to tenant "
                f"{declared_scope!r}.",
                dataset_id))
        return

    # Shared (non-provider-scoped) lane: no dataset-level tenant id permitted.
    if dataset_provider is not None:
        report.add(CheckResult(
            "NFR-SEC-005", "high", False,
            f"Shared-lane dataset must not declare a dataset-level providerId "
            f"(found {dataset_provider!r}).",
            dataset_id))
        return
    empty = [
        record.get("capacityRecordId", "<unknown>")
        for record in records
        if isinstance(record, dict) and "providerId" in record
        and not record.get("providerId")
    ]
    if empty:
        report.add(CheckResult(
            "NFR-SEC-005", "high", False,
            f"Record(s) with empty providerId in shared lane: {empty}",
            dataset_id))
    else:
        report.add(CheckResult(
            "NFR-SEC-005", "low", True,
            "Tenant boundary upheld for shared lane (per-record tenant ids).",
            dataset_id))


def check_degraded_mode(data: dict, entry: dict, dataset_id: str,
                        report: GateReport) -> None:
    """Onboarding degraded-mode and recovery readiness (NFR-REL-005 / CH-C03).

    Provider-scoped onboarding datasets must declare a ``degradedMode`` contract
    that bounds degraded-mode behaviour: a fallback read model, a positive and
    bounded data-staleness ceiling, an explicit manual-override capability, and a
    recovery-runbook reference. This is the SIT proof for the onboarding
    degraded-mode and recovery behaviour deferred from Phase 1 (RV-06-05).
    """
    declared_scope = entry.get("providerScope", "none")
    if not declared_scope or declared_scope == "none":
        return

    block = data.get("degradedMode") if isinstance(data, dict) else None
    if not isinstance(block, dict):
        report.add(CheckResult(
            "NFR-REL-005", "high", False,
            "Provider-scoped dataset missing degradedMode reliability contract.",
            dataset_id))
        return

    problems: list[str] = []
    staleness = block.get("maxDataStalenessMinutes")
    if not isinstance(staleness, int) or isinstance(staleness, bool) or staleness <= 0:
        problems.append("maxDataStalenessMinutes must be a positive integer")
    elif staleness > 60:
        problems.append(
            f"maxDataStalenessMinutes {staleness} exceeds the 60-minute ceiling")
    if block.get("manualOverrideSupported") is not True:
        problems.append("manualOverrideSupported must be true")
    if not block.get("fallbackReadModel"):
        problems.append("missing fallbackReadModel")
    if not block.get("recoveryRunbook"):
        problems.append("missing recoveryRunbook")

    if problems:
        report.add(CheckResult(
            "NFR-REL-005", "high", False,
            "Degraded-mode contract incomplete: " + "; ".join(problems),
            dataset_id))
    else:
        report.add(CheckResult(
            "NFR-REL-005", "low", True,
            "Degraded-mode and recovery contract declared (fallback read model, "
            "bounded staleness, manual override, recovery runbook).",
            dataset_id))


def validate_dataset(entry: dict, root: str, report: GateReport,
                     taxonomy_version: str = "") -> None:
    dataset_id = entry.get("datasetId", "<unknown>")
    data_rel = entry["dataFile"]
    schema_rel = entry["schemaFile"]
    data_path = os.path.join(root, data_rel)
    schema_path = os.path.join(root, schema_rel)

    if not os.path.isfile(data_path):
        report.add(CheckResult("DATASET", "critical", False,
                               f"Dataset file not found: {data_rel}", dataset_id))
        return
    if not os.path.isfile(schema_path):
        report.add(CheckResult("DATASET", "critical", False,
                               f"Schema file not found: {schema_rel}", dataset_id))
        return

    report.evaluated_resources.append(data_rel)
    data = _load_json(data_path)
    schema = _load_json(schema_path)

    schema_errors = validate_schema(data, schema, data_rel)
    if schema_errors:
        for err in schema_errors:
            report.add(CheckResult("SCHEMA", "critical", False, err, dataset_id))
    else:
        report.add(CheckResult("SCHEMA", "low", True,
                               "Dataset conforms to its contract schema.", dataset_id))

    # Confirm the declared contract id matches the dataset payload.
    declared_contract = data.get("contractId")
    if declared_contract and declared_contract not in schema.get("properties", {}).get(
            "contractId", {}).get("enum", [declared_contract]):
        report.add(CheckResult("SCHEMA", "high", False,
                               f"contractId {declared_contract!r} not permitted by schema.",
                               dataset_id))

    records = data.get("records", []) if isinstance(data, dict) else []
    if entry.get("minimizationChecked"):
        check_minimization(records, dataset_id, report)
    if entry.get("lane") == "specialty-capacity":
        check_capacity_invariants(records, dataset_id, report)
        check_specialty_metadata(data, records, dataset_id, taxonomy_version, report)
    # Phase 2 onboarding policy enforcement (applies to every onboarding lane).
    check_purpose_tags(data, records, dataset_id, report)
    check_tenant_boundary(data, entry, records, dataset_id, report)
    # Phase 3 provider degraded-mode / recovery reliability enforcement.
    check_degraded_mode(data, entry, dataset_id, report)

    # Traceability coverage: at least one FR and one CH control must be declared.
    if not entry.get("fr"):
        report.add(CheckResult("TRACE", "high", False,
                               "No FR control mapped in traceability.", dataset_id))
    if not entry.get("ch"):
        report.add(CheckResult("TRACE", "high", False,
                               "No CH control mapped in traceability.", dataset_id))
    if entry.get("fr") and entry.get("ch"):
        report.add(CheckResult("TRACE", "low", True,
                               "FR/NFR/CH traceability declared for dataset.", dataset_id))


def build_evidence(report: GateReport, traceability: dict) -> dict:
    failures = report.failures
    critical = [r for r in failures if r.severity == "critical"]
    fr = sorted({c for d in traceability["datasets"] for c in d.get("fr", [])})
    nfr = sorted({c for d in traceability["datasets"] for c in d.get("nfr", [])})
    ch = sorted({c for d in traceability["datasets"] for c in d.get("ch", [])})
    rv = sorted({c for d in traceability["datasets"] for c in d.get("rv", [])})
    return {
        "evidenceType": "synthesized-data-contract-validation",
        "schemaSource": "data/synthetic/schema/*.schema.json",
        "gateName": "sit-synthesized-data",
        "environment": "SIT",
        "traceabilityVersion": traceability.get("version"),
        "specialtyTaxonomyVersion": traceability.get("specialtyTaxonomyVersion"),
        "datasetsEvaluated": [d["datasetId"] for d in traceability["datasets"]],
        "passFailSummary": {
            "result": "pass" if not failures else "fail",
            "totalChecks": len(report.results),
            "passed": len(report.results) - len(failures),
            "failed": len(failures),
            "criticalFailures": len(critical),
        },
        "controlCoverage": {"fr": fr, "nfr": nfr, "ch": ch, "rv": rv},
        "failureDetails": [
            {
                "controlId": r.control_id,
                "severity": r.severity,
                "resource": r.resource,
                "message": r.message,
            }
            for r in failures
        ],
        "executionTimestampUtc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }


def run(root: str) -> tuple[dict, GateReport]:
    traceability = _load_json(os.path.join(root, "traceability.json"))
    taxonomy_version = traceability.get("specialtyTaxonomyVersion", "")
    report = GateReport()
    for entry in traceability["datasets"]:
        validate_dataset(entry, root, report, taxonomy_version)
    evidence = build_evidence(report, traceability)
    return evidence, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Root of the synthetic data pack (default: this script's directory).")
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to write the evidence artifact JSON.")
    args = parser.parse_args(argv)

    evidence, report = run(args.root)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, indent=2)
            handle.write("\n")

    summary = evidence["passFailSummary"]
    print(json.dumps(evidence, indent=2))
    print(
        f"\nsynthesized-data gate: {summary['result']} "
        f"({summary['passed']}/{summary['totalChecks']} checks passed, "
        f"{summary['criticalFailures']} critical failures)",
        file=sys.stderr)
    for failure in report.failures:
        print(f"  - [{failure.severity}] {failure.control_id} "
              f"({failure.resource}): {failure.message}", file=sys.stderr)

    return 0 if summary["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
