#!/usr/bin/env python3
"""Sprint 05 Phase 2 policy-as-code gate.

Evaluates the mandatory release controls defined in
``docs/adr/0010-policy-as-code-and-release-evidence-gates.md`` and
``docs/adr/0011-cantonal-legal-applicability-gate.md`` against the
repository's infrastructure parameters, governance exception register, and
cantonal legal-applicability annex.

The gate is intentionally dependency-free (Python 3 standard library only) so
it runs identically in CI and on a developer machine.

Behaviour (per ADR-0010 / ADR-0011):

* Mandatory controls are checked for the requested deployment scope.
* The promotion threshold is **zero critical failures**; any uncovered
  critical failure makes the gate fail (non-zero exit).
* Governance exceptions are validated against the 90-day max-validity
  baseline. A valid exception waives the matching control failure; an
  expired / over-validity / malformed exception is itself a hard blocker.
* The run emits a canonical evidence artifact (ADR-0010 Target 3 schema).
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


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass
class CheckResult:
    control_id: str
    severity: str
    passed: bool
    message: str
    resource: str = ""
    waived_by: str = ""


@dataclass
class GateReport:
    results: list[CheckResult] = field(default_factory=list)
    evaluated_resources: list[str] = field(default_factory=list)
    exception_refs: list[str] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)


# --------------------------------------------------------------------------
# Loading helpers
# --------------------------------------------------------------------------

def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def parse_bicepparam(text: str) -> dict[str, str]:
    """Extract ``param <name> = <value>`` assignments from a .bicepparam file."""
    params: dict[str, str] = {}
    pattern = re.compile(r"^\s*param\s+(\w+)\s*=\s*(.+?)\s*$", re.MULTILINE)
    for name, raw in pattern.findall(text):
        value = raw.strip()
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            value = value[1:-1]
        params[name] = value
    return params


def _today_date_utc() -> _dt.date:
    return _dt.datetime.now(_dt.timezone.utc).date()


def _parse_date(value: str) -> _dt.date | None:
    try:
        return _dt.datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


# --------------------------------------------------------------------------
# Infrastructure checks
# --------------------------------------------------------------------------

def _scope_param_files(pack: dict, scope: str) -> list[str]:
    files = list(pack.get("environmentParamFiles", []))
    if scope in ("sit", "prod"):
        scoped = [f for f in files if f"/{scope}." in f or f.endswith(f"{scope}.bicepparam")]
        return scoped or files
    return files


def check_residency(pack: dict, root: str, param_files: list[str], report: GateReport) -> None:
    allowed = {r.lower() for r in pack.get("residency", {}).get("allowedRegions", [])}
    for rel in param_files:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            report.add(CheckResult(
                "MC-RESIDENCY", "critical", False,
                f"Environment parameter file not found: {rel}", rel))
            continue
        report.evaluated_resources.append(rel)
        params = parse_bicepparam(_read_text(path))
        location = (params.get("location") or "").lower()
        if not location:
            report.add(CheckResult(
                "MC-RESIDENCY", "critical", False,
                "No 'location' parameter declared; PHI residency cannot be guaranteed.",
                rel))
        elif location not in allowed:
            report.add(CheckResult(
                "MC-RESIDENCY", "critical", False,
                f"Region '{location}' is not an approved Swiss residency region "
                f"({sorted(allowed)}).",
                rel))
        else:
            report.add(CheckResult(
                "MC-RESIDENCY", "critical", True,
                f"Region '{location}' is an approved Swiss residency region.", rel))


def check_deployment_type(pack: dict, root: str, param_files: list[str], report: GateReport) -> None:
    prohibited = {p.lower() for p in pack.get("prohibitedDeploymentTypes", [])}
    for rel in param_files:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            report.add(CheckResult(
                "MC-DEPLOYMENT-TYPE", "critical", False,
                f"Environment parameter file not found: {rel}", rel))
            continue
        params = parse_bicepparam(_read_text(path))
        hits = sorted({
            v for v in params.values() if v.lower() in prohibited
        })
        if hits:
            report.add(CheckResult(
                "MC-DEPLOYMENT-TYPE", "critical", False,
                f"Prohibited deployment type(s) selected: {hits}.", rel))
        else:
            report.add(CheckResult(
                "MC-DEPLOYMENT-TYPE", "critical", True,
                "No prohibited deployment types selected.", rel))


def check_module_enabled(control: dict, root: str, param_files: list[str], report: GateReport) -> None:
    param = control["requiredParam"]
    for rel in param_files:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            report.add(CheckResult(
                control["id"], control["severity"], False,
                f"Environment parameter file not found: {rel}", rel))
            continue
        params = parse_bicepparam(_read_text(path))
        value = (params.get(param) or "").lower()
        if value == "true":
            report.add(CheckResult(
                control["id"], control["severity"], True,
                f"{param} is enabled.", rel))
        else:
            report.add(CheckResult(
                control["id"], control["severity"], False,
                f"{param} must be 'true' for affected resources; found '{value or 'unset'}'.",
                rel))


# --------------------------------------------------------------------------
# Cantonal annex check
# --------------------------------------------------------------------------

def parse_annex_register(text: str, required_fields: list[str]) -> list[dict[str, str]]:
    """Parse the canton register Markdown table into a list of row dicts.

    The register table is identified by a header row that contains every
    required field name (wrapped in backticks in the annex).
    """
    rows: list[dict[str, str]] = []
    lines = text.splitlines()
    header_idx = None
    headers: list[str] = []
    for idx, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip(" `") for c in line.strip().strip("|").split("|")]
        if all(f in cells for f in required_fields):
            header_idx = idx
            headers = cells
            break
    if header_idx is None:
        return rows
    for line in lines[header_idx + 1:]:
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Skip the markdown separator row (e.g. | ----- | ----- |).
        if all(set(c) <= {"-", ":", " "} and c for c in cells):
            continue
        if len(cells) != len(headers):
            continue
        row = {headers[i]: cells[i].strip(" `") for i in range(len(headers))}
        rows.append(row)
    return rows


def check_cantonal_annex(pack: dict, control: dict, root: str, report: GateReport) -> None:
    cfg = pack.get("cantonalAnnex", {})
    rel = cfg.get("file", "")
    path = os.path.join(root, rel)
    severity = control["severity"]
    if not rel or not os.path.isfile(path):
        report.add(CheckResult(
            control["id"], severity, False,
            f"Cantonal annex file not found: {rel}", rel))
        return
    report.evaluated_resources.append(rel)
    required_fields = cfg.get("requiredFields", [])
    allowed_statuses = set(cfg.get("allowedStatuses", []))
    allowed_owners = set(cfg.get("allowedOwners", []))
    rows = parse_annex_register(_read_text(path), required_fields)
    if not rows:
        report.add(CheckResult(
            control["id"], severity, False,
            "Cantonal annex register table is missing or has no canton entries.", rel))
        return

    problems: list[str] = []
    for row in rows:
        canton = row.get("cantonId", "<unknown>")
        missing = [f for f in required_fields if not row.get(f)]
        if missing:
            problems.append(f"canton {canton}: missing field(s) {missing}")
        owner = row.get("controlOwner", "")
        if owner and allowed_owners and owner not in allowed_owners:
            problems.append(f"canton {canton}: owner '{owner}' not in {sorted(allowed_owners)}")
        status = row.get("status", "")
        if status and allowed_statuses and status not in allowed_statuses:
            problems.append(f"canton {canton}: status '{status}' not in {sorted(allowed_statuses)}")

    if problems:
        report.add(CheckResult(
            control["id"], severity, False,
            "Cantonal annex schema incomplete: " + "; ".join(problems), rel))
    else:
        report.add(CheckResult(
            control["id"], severity, True,
            f"Cantonal annex schema complete for {len(rows)} canton entr(y/ies).", rel))


# --------------------------------------------------------------------------
# Exception handling
# --------------------------------------------------------------------------

def evaluate_exceptions(pack: dict, exceptions_doc: dict, report: GateReport) -> dict[str, dict]:
    """Validate active governance exceptions.

    Returns a mapping of control-id -> exception for currently *valid*
    exceptions (which may waive a matching control failure). Invalid or
    expired exceptions are themselves recorded as critical failures.
    """
    valid_by_control: dict[str, dict] = {}
    required_fields = exceptions_doc.get("requiredFields", [])
    max_days = pack.get("exceptions", {}).get("maxValidityDays", 90)
    today = _today_date_utc()

    for exc in exceptions_doc.get("exceptions", []):
        exc_id = exc.get("id", "<unknown>")
        if exc.get("status", "active") not in ("active", "", None):
            continue
        report.exception_refs.append(exc_id)

        missing = [f for f in required_fields if not exc.get(f)]
        if missing:
            report.add(CheckResult(
                "EXC-SCHEMA", "critical", False,
                f"Exception {exc_id} is missing required field(s) {missing}.", exc_id,
            ))
            continue

        expiry = _parse_date(str(exc.get("expiry", "")))
        approval = _parse_date(str(exc.get("approvalDate", "")))
        if expiry is None:
            report.add(CheckResult(
                "EXC-EXPIRY", "critical", False,
                f"Exception {exc_id} has an invalid expiry date.", exc_id))
            continue
        if expiry < today:
            report.add(CheckResult(
                "EXC-EXPIRY", "critical", False,
                f"Exception {exc_id} expired on {expiry.isoformat()}; expired exceptions "
                "are hard promotion blockers.", exc_id))
            continue
        if approval is not None and (expiry - approval).days > max_days:
            report.add(CheckResult(
                "EXC-EXPIRY", "critical", False,
                f"Exception {exc_id} validity exceeds the {max_days}-day maximum "
                f"({approval.isoformat()} -> {expiry.isoformat()}).", exc_id))
            continue

        report.add(CheckResult(
            "EXC-VALID", "low", True,
            f"Exception {exc_id} is valid until {expiry.isoformat()}.", exc_id))
        valid_by_control[exc.get("control", "")] = exc

    return valid_by_control


def apply_waivers(report: GateReport, valid_by_control: dict[str, dict]) -> None:
    """Mark failing control results as waived when a valid exception covers them."""
    for result in report.results:
        if result.passed:
            continue
        exc = valid_by_control.get(result.control_id)
        if exc:
            result.waived_by = exc.get("id", "")
            result.message += f" [waived by exception {result.waived_by} until {exc.get('expiry')}]"


# --------------------------------------------------------------------------
# Orchestration and evidence emission
# --------------------------------------------------------------------------

def run_gate(pack: dict, exceptions_doc: dict, root: str, scope: str) -> GateReport:
    report = GateReport()
    param_files = _scope_param_files(pack, scope)
    mandatory = pack.get("mandatoryControls", [])

    for control in mandatory:
        check = control.get("check")
        if check == "residency":
            check_residency(pack, root, param_files, report)
        elif check == "deploymentType":
            check_deployment_type(pack, root, param_files, report)
        elif check == "moduleEnabled":
            check_module_enabled(control, root, param_files, report)
        elif check == "cantonalAnnex":
            check_cantonal_annex(pack, control, root, report)

    valid_by_control = evaluate_exceptions(pack, exceptions_doc, report)
    apply_waivers(report, valid_by_control)

    # De-duplicate evaluated resources while preserving order.
    seen: set[str] = set()
    deduped = []
    for item in report.evaluated_resources:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    report.evaluated_resources = deduped
    return report


def build_evidence(report: GateReport, pack: dict, gate_name: str,
                   pipeline_run_id: str) -> dict:
    mandatory_ids = {c["id"] for c in pack.get("mandatoryControls", [])}
    evaluated_ids = {r.control_id for r in report.results if r.control_id in mandatory_ids}
    coverage = (
        round(100.0 * len(evaluated_ids) / len(mandatory_ids), 1) if mandatory_ids else 100.0
    )

    failures = [r for r in report.results if not r.passed and not r.waived_by]
    critical_failures = [r for r in failures if r.severity == "critical"]
    passed = sum(1 for r in report.results if r.passed)

    threshold = pack.get("promotionThreshold", {})
    max_critical = threshold.get("maxCriticalFailures", 0)
    required_coverage = threshold.get("requiredMandatoryControlCoveragePercent", 100)

    result = "pass"
    if len(critical_failures) > max_critical or coverage < required_coverage:
        result = "fail"

    failure_details = [
        {
            "controlId": r.control_id,
            "severity": r.severity,
            "resource": r.resource,
            "message": r.message,
        }
        for r in failures
    ]

    return {
        "policyPackVersion": pack.get("policyPackVersion", "unknown"),
        "gateName": gate_name,
        "evaluatedResources": report.evaluated_resources,
        "passFailSummary": {
            "result": result,
            "totalChecks": len(report.results),
            "passed": passed,
            "failed": len(failures),
            "criticalFailures": len(critical_failures),
            "mandatoryControlCoveragePercent": coverage,
        },
        "failureDetails": failure_details,
        "exceptionRefs": report.exception_refs,
        "executionTimestampUtc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "pipelineRunId": pipeline_run_id,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Sprint 05 policy-as-code gate.")
    parser.add_argument("--scope", default="sit", choices=["sit", "prod", "all"],
                        help="Deployment scope to evaluate (default: sit).")
    parser.add_argument("--gate-name", default=None,
                        help="Gate name recorded in evidence (default: <scope>-policy-gate).")
    parser.add_argument("--repo-root", default=".",
                        help="Repository root used to resolve relative paths.")
    parser.add_argument("--policy-pack", default=None,
                        help="Path to the policy pack JSON (default: <root>/policy/policy-pack.json).")
    parser.add_argument("--exceptions", default=None,
                        help="Path to the exception register JSON (default: <root>/policy/exceptions.json).")
    parser.add_argument("--pipeline-run-id", default=os.environ.get("GITHUB_RUN_ID", "local"),
                        help="Pipeline run id recorded in evidence.")
    parser.add_argument("--output", default=None,
                        help="Write the evidence artifact to this path in addition to stdout.")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.repo_root)
    pack_path = args.policy_pack or os.path.join(root, "policy", "policy-pack.json")
    exc_path = args.exceptions or os.path.join(root, "policy", "exceptions.json")
    gate_name = args.gate_name or f"{args.scope}-policy-gate"

    pack = _load_json(pack_path)
    exceptions_doc = _load_json(exc_path) if os.path.isfile(exc_path) else {"exceptions": []}

    report = run_gate(pack, exceptions_doc, root, args.scope)
    evidence = build_evidence(report, pack, gate_name, args.pipeline_run_id)

    rendered = json.dumps(evidence, indent=2)
    print(rendered)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")

    summary = evidence["passFailSummary"]
    sys.stderr.write(
        f"\nGate '{gate_name}' result: {summary['result'].upper()} "
        f"(critical failures: {summary['criticalFailures']}, "
        f"coverage: {summary['mandatoryControlCoveragePercent']}%)\n"
    )
    return 0 if summary["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
