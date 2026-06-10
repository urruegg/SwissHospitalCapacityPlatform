# Policy-as-Code and Release Evidence Gates

This directory implements **Sprint 05 Phase 2**: it converts the documented
governance controls in
[`docs/adr/0010-policy-as-code-and-release-evidence-gates.md`](../docs/adr/0010-policy-as-code-and-release-evidence-gates.md)
and
[`docs/adr/0011-cantonal-legal-applicability-gate.md`](../docs/adr/0011-cantonal-legal-applicability-gate.md)
into an enforceable, testable CI and promotion gate.

It closes register item `RV-03` in
[`docs/sprints/sprint-05/requires-validation-register.md`](../docs/sprints/sprint-05/requires-validation-register.md).

## Contents

| File | Purpose |
| ----- | ----- |
| `policy_gate.py` | Dependency-free (Python 3 stdlib) policy gate evaluator. |
| `policy-pack.json` | Machine-readable policy pack: mandatory controls, promotion thresholds, residency allowlist, prohibited deployment types, cantonal-annex field schema. |
| `exceptions.json` | Governance exception register validated against the 90-day max-validity baseline. |
| `schema/evidence-schema.json` | JSON Schema for the canonical evidence artifact (ADR-0010 Target 3). |
| `tests/test_policy_gate.py` | Unit tests for the gate behaviour. |

## What the gate enforces

The gate evaluates the **mandatory controls** for the requested deployment
scope (`sit`, `prod`, or `all`):

1. **PHI residency and transfer guardrails** (`MC-RESIDENCY`, critical) — every
   environment must pin `location` to an approved Swiss region.
2. **Prohibited deployment-type restrictions** (`MC-DEPLOYMENT-TYPE`, critical) —
   no environment may select a `global` or data-zone deployment type.
3. **Mandatory identity controls** (`MC-IDENTITY`, critical) — managed-identity
   module must be enabled.
4. **Mandatory diagnostics controls** (`MC-DIAGNOSTICS`, critical) —
   observability / diagnostics module must be enabled.
5. **Cantonal annex completeness** (`MC-CANTONAL-ANNEX`, high) — every canton
   entry carries all ADR-0011 mandatory fields, a valid owner, and a valid
   status.

### Promotion threshold

Promotion requires **zero critical failures** and **100 percent mandatory-control
coverage** (ADR-0010 Targets 1 and 2). Any uncovered critical failure makes the
gate exit non-zero and blocks promotion.

### Exception behaviour

Each active exception in `exceptions.json` is validated against the
exception-management baseline (max 90-day validity). A **valid** exception
waives the matching control failure; an **expired**, **over-validity**, or
**malformed** exception is itself a hard promotion blocker (ADR-0010 Target 4,
ADR-0011 Target 4).

## Running locally

```bash
# Evaluate the SIT scope and write the evidence artifact.
python3 policy/policy_gate.py --scope sit --output policy-evidence/policy-gate-sit.json

# Evaluate the PROD promotion scope.
python3 policy/policy_gate.py --scope prod

# Run the unit tests.
python3 -m unittest discover -s policy/tests -v
```

The gate prints the canonical evidence JSON to stdout, writes it to `--output`
when supplied, and exits `0` on pass / `1` on fail.

## CI and promotion integration

| Surface | Workflow | Behaviour |
| ----- | ----- | ----- |
| CI (pull request / push) | `.github/workflows/policy-gate.yml` | Runs unit tests, then the SIT-scope gate; uploads the evidence artifact. |
| SIT deploy | `.github/workflows/cd-infra-deploy-sit.yml` | Blocking SIT-scope gate before any `az deployment`. |
| PROD promotion | `.github/workflows/cd-infra-deploy-prod.yml` | Blocking PROD-scope gate before any `az deployment`. |

Generated evidence for the Phase 2 SIT gate run is committed under
[`docs/sprints/sprint-05/evidence/`](../docs/sprints/sprint-05/evidence/).
