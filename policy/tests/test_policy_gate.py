#!/usr/bin/env python3
"""Unit tests for the Sprint 05 policy-as-code gate (``policy/policy_gate.py``).

Run with: ``python3 -m unittest discover -s policy/tests``
"""

import datetime as dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import policy_gate as pg  # noqa: E402


BASE_PACK = {
    "policyPackVersion": "1.0.0",
    "promotionThreshold": {
        "maxCriticalFailures": 0,
        "requiredMandatoryControlCoveragePercent": 100,
    },
    "exceptions": {"maxValidityDays": 90},
    "residency": {"allowedRegions": ["switzerlandnorth", "switzerlandwest"]},
    "prohibitedDeploymentTypes": ["global", "data-zone-standard"],
    "mandatoryControls": [
        {"id": "MC-RESIDENCY", "name": "residency", "severity": "critical", "check": "residency"},
        {"id": "MC-DEPLOYMENT-TYPE", "name": "dt", "severity": "critical", "check": "deploymentType"},
        {"id": "MC-IDENTITY", "name": "id", "severity": "critical", "check": "moduleEnabled",
         "requiredParam": "enableIdentityModule"},
        {"id": "MC-DIAGNOSTICS", "name": "diag", "severity": "critical", "check": "moduleEnabled",
         "requiredParam": "enableObservabilityModule"},
        {"id": "MC-CANTONAL-ANNEX", "name": "annex", "severity": "high", "check": "cantonalAnnex"},
    ],
    "cantonalAnnex": {
        "file": "docs/compliance/cantonal-annex.md",
        "requiredFields": ["cantonId", "legalSource", "obligationSummary", "controlMappings",
                           "controlOwner", "evidenceArtifacts", "status", "openValidationPoints"],
        "allowedStatuses": ["design-aligned", "implemented", "requires-validation"],
        "allowedOwners": ["LEGAL", "SEC", "OPS", "ARCH"],
    },
    "environmentParamFiles": ["infra/environments/sit.bicepparam"],
}


GOOD_PARAM = """using '../main.bicep'

param environmentName = 'sit'
param location = 'switzerlandnorth'
param enableIdentityModule = true
param enableObservabilityModule = true
"""

GOOD_ANNEX = """# Cantonal Annex

| `cantonId` | `legalSource` | `obligationSummary` | `controlMappings` | `controlOwner` | `evidenceArtifacts` | `status` | `openValidationPoints` |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| `ZH` | statute | summary | `CH-C01` | LEGAL | link | `requires-validation` | none |
"""


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _build_repo(root, param=GOOD_PARAM, annex=GOOD_ANNEX):
    _write(root, "infra/environments/sit.bicepparam", param)
    _write(root, "docs/compliance/cantonal-annex.md", annex)


def _evidence(root, pack=BASE_PACK, exceptions=None, scope="sit"):
    exceptions = exceptions or {"requiredFields": [], "exceptions": []}
    report = pg.run_gate(pack, exceptions, root, scope)
    return pg.build_evidence(report, pack, "test-gate", "local")


class ParamParsingTests(unittest.TestCase):
    def test_parse_bicepparam_strips_quotes(self):
        params = pg.parse_bicepparam(GOOD_PARAM)
        self.assertEqual(params["location"], "switzerlandnorth")
        self.assertEqual(params["enableIdentityModule"], "true")


class HappyPathTests(unittest.TestCase):
    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            ev = _evidence(root)
            self.assertEqual(ev["passFailSummary"]["result"], "pass")
            self.assertEqual(ev["passFailSummary"]["criticalFailures"], 0)
            self.assertEqual(ev["passFailSummary"]["mandatoryControlCoveragePercent"], 100.0)

    def test_evidence_has_canonical_fields(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            ev = _evidence(root)
            for field in ["policyPackVersion", "gateName", "evaluatedResources",
                          "passFailSummary", "failureDetails", "exceptionRefs",
                          "executionTimestampUtc", "pipelineRunId"]:
                self.assertIn(field, ev)


class ResidencyTests(unittest.TestCase):
    def test_non_swiss_region_fails_critical(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, param=GOOD_PARAM.replace("switzerlandnorth", "eastus"))
            ev = _evidence(root)
            self.assertEqual(ev["passFailSummary"]["result"], "fail")
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-RESIDENCY", ids)


class DeploymentTypeTests(unittest.TestCase):
    def test_prohibited_type_fails(self):
        bad = GOOD_PARAM + "param deploymentType = 'global'\n"
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, param=bad)
            ev = _evidence(root)
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-DEPLOYMENT-TYPE", ids)
            self.assertEqual(ev["passFailSummary"]["result"], "fail")


class ModuleControlTests(unittest.TestCase):
    def test_identity_disabled_fails(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, param=GOOD_PARAM.replace(
                "param enableIdentityModule = true", "param enableIdentityModule = false"))
            ev = _evidence(root)
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-IDENTITY", ids)


class CantonalAnnexTests(unittest.TestCase):
    def test_missing_field_fails(self):
        bad_annex = GOOD_ANNEX.replace("| LEGAL |", "|  |")
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, annex=bad_annex)
            ev = _evidence(root)
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-CANTONAL-ANNEX", ids)

    def test_invalid_owner_fails(self):
        bad_annex = GOOD_ANNEX.replace("| LEGAL |", "| NOBODY |")
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, annex=bad_annex)
            ev = _evidence(root)
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-CANTONAL-ANNEX", ids)

    def test_missing_table_fails(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, annex="# Annex with no register table\n")
            ev = _evidence(root)
            ids = {f["controlId"] for f in ev["failureDetails"]}
            self.assertIn("MC-CANTONAL-ANNEX", ids)


def _exc(**overrides):
    today = pg._today_utc()
    base = {
        "id": "EX-1",
        "control": "MC-RESIDENCY",
        "rationale": "r",
        "compensatingControls": "c",
        "owner": "SEC",
        "approvedBy": "@owner",
        "approvalDate": today.isoformat(),
        "expiry": (today + dt.timedelta(days=30)).isoformat(),
        "mitigationPlan": "m",
        "followUpValidationDate": (today + dt.timedelta(days=15)).isoformat(),
    }
    base.update(overrides)
    return base


REQ_FIELDS = ["id", "control", "rationale", "compensatingControls", "owner", "approvedBy",
              "approvalDate", "expiry", "mitigationPlan", "followUpValidationDate"]


class ExceptionTests(unittest.TestCase):
    def _run(self, exceptions_list, param=GOOD_PARAM):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root, param=param)
            doc = {"requiredFields": REQ_FIELDS, "exceptions": exceptions_list}
            return _evidence(root, exceptions=doc)

    def test_valid_exception_waives_failure(self):
        # Residency fails, but a valid exception covers MC-RESIDENCY.
        ev = self._run([_exc()], param=GOOD_PARAM.replace("switzerlandnorth", "eastus"))
        self.assertEqual(ev["passFailSummary"]["result"], "pass")
        self.assertIn("EX-1", ev["exceptionRefs"])

    def test_expired_exception_blocks(self):
        today = pg._today_utc()
        ev = self._run([_exc(expiry=(today - dt.timedelta(days=1)).isoformat())])
        self.assertEqual(ev["passFailSummary"]["result"], "fail")
        ids = {f["controlId"] for f in ev["failureDetails"]}
        self.assertIn("EXC-EXPIRY", ids)

    def test_over_validity_exception_blocks(self):
        today = pg._today_utc()
        ev = self._run([_exc(
            approvalDate=today.isoformat(),
            expiry=(today + dt.timedelta(days=120)).isoformat())])
        self.assertEqual(ev["passFailSummary"]["result"], "fail")
        ids = {f["controlId"] for f in ev["failureDetails"]}
        self.assertIn("EXC-EXPIRY", ids)

    def test_missing_field_exception_blocks(self):
        exc = _exc()
        del exc["mitigationPlan"]
        ev = self._run([exc])
        self.assertEqual(ev["passFailSummary"]["result"], "fail")
        ids = {f["controlId"] for f in ev["failureDetails"]}
        self.assertIn("EXC-SCHEMA", ids)


if __name__ == "__main__":
    unittest.main()
