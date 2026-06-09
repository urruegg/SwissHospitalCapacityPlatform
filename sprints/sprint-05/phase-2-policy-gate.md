# Sprint 05 Phase 2 — Policy-as-Code Gate Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 2 implementation outcome and the **SIT gate evidence** for the
policy-as-code and governance gates required by
[`docs/adr/0010-policy-as-code-and-release-evidence-gates.md`](../../docs/adr/0010-policy-as-code-and-release-evidence-gates.md)
and
[`docs/adr/0011-cantonal-legal-applicability-gate.md`](../../docs/adr/0011-cantonal-legal-applicability-gate.md).
This is the Phase 2 (#35) deliverable for
[`sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md)
and closes register item `RV-03` in
[`requires-validation-register.md`](requires-validation-register.md).

## What was implemented

1. A dependency-free policy gate (`policy/policy_gate.py`) that evaluates the
   mandatory release controls for a deployment scope (`sit`, `prod`, `all`).
2. A machine-readable policy pack (`policy/policy-pack.json`) and governance
   exception register (`policy/exceptions.json`).
3. The canonical evidence-artifact JSON schema
   (`policy/schema/evidence-schema.json`, ADR-0010 Target 3).
4. Zero critical-failure promotion threshold and 100 percent mandatory-control
   coverage enforcement.
5. Exception expiry blocker behaviour (expired / over-90-day / malformed
   exceptions are hard blockers; valid exceptions waive a matching failure).
6. Cantonal annex checks (schema completeness, owner assignment, status
   validity) wired into the same gate.
7. CI workflow (`.github/workflows/policy-gate.yml`) plus blocking gate steps on
   the SIT and PROD deploy workflows.
8. Unit tests (`policy/tests/test_policy_gate.py`).

See [`policy/README.md`](../../policy/README.md) for the full control list and
run instructions.

## SIT gate evidence

The committed evidence artifact for the Phase 2 SIT gate run is
[`evidence/2026-06-09-phase-2-sit-policy-gate.json`](evidence/2026-06-09-phase-2-sit-policy-gate.json),
produced by:

```bash
python3 policy/policy_gate.py --scope sit --pipeline-run-id local \
  --output sprints/sprint-05/evidence/2026-06-09-phase-2-sit-policy-gate.json
```

Result summary: `pass` — 5 of 5 checks passed, 0 critical failures, 100 percent
mandatory-control coverage. In CI the same gate runs in
`.github/workflows/policy-gate.yml` and uploads the artifact under the
`policy-gate-evidence` name.

## Sprint 05 Phase Evidence

### Phase Context

- Phase issue: #35 (see sprints/sprint-05/phase-issue-map.md)
- Phase: 2
- Work package(s): WP-04
- Impacted architecture lanes: governance, platform-control, infrastructure

### FR Controls Impacted

- `FR-GOV-003`: Governance controls enforced as policy-as-code in CI/CD — full
- `FR-GOV-004`: Promotion gated on control evidence — full
- `FR-GOV-005`: Exception lifecycle (approval, expiry) enforced — full

### NFR Controls Impacted

- `NFR-COMP-007`: Audit-grade evidence artifact produced per gate run — full
- `NFR-SEC-001`: Mandatory identity controls enforced for affected scope — partial
- `NFR-SEC-002`: PHI residency / transfer guardrails enforced — full

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C05` | PHI residency and transfer guardrails enforced in CI | SEC | [`evidence/2026-06-09-phase-2-sit-policy-gate.json`](evidence/2026-06-09-phase-2-sit-policy-gate.json) |
| `CH-C03` | Landing-zone / diagnostics and identity control coverage | ARCH | [`evidence/2026-06-09-phase-2-sit-policy-gate.json`](evidence/2026-06-09-phase-2-sit-policy-gate.json) |
| `CH-C10` | Control-effectiveness evidence schema | SEC | [`policy/schema/evidence-schema.json`](../../policy/schema/evidence-schema.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-03 | closed | validated |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: pass
- [x] `python3 -m unittest discover -s policy/tests -v` — outcome: pass
- [x] `python3 policy/policy_gate.py --scope sit` — outcome: pass
- [ ] DR rehearsal / restore proof (Phase 3) — outcome: n/a
- [ ] golden-task replay (Phase 4 / agents changed) — outcome: n/a

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/policy-gate.yml` |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-2-sit-policy-gate.json`](evidence/2026-06-09-phase-2-sit-policy-gate.json) |
| PROD gate | yes | pending | Requires legal/compliance sign-off |
| Runtime gate | no | n/a | |

### Approvals (PROD promotion only)

> PROD promotion is **pending**: the approvals below are required before the PROD
> gate may read `pass`. Handles and timestamps are recorded at sign-off time.

| Role | Approver handle | Timestamp | Decision |
| ----- | ----- | ----- | ----- |
| ARCH | TBD | | pending |
| SEC | TBD | | pending |
| OPS | TBD | | pending |
| LEGAL (cantonal) | TBD | | pending |

### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Policy gate validates declared IaC parameters, not deployed-state drift (closed in Phase 4 RV-12) | medium | ARCH | Phase 4 drift-detection control note; `what-if` parity check already runs in `ci-infra-validate` | 2026-09-07 | accepted |
| Cantonal annex entries remain `requires-validation` pending legal sign-off | high | LEGAL | PROD limited to SIT/non-production for affected cantons until sign-off (ADR-0011 §3) | 2026-09-07 | open |

### Definition of Done Confirmation

- [x] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [x] No unresolved high-severity register item for this phase left undocumented
- [x] Every edited doc has its Version header bumped (copilot-instructions §9)

## Change Control

Any change to this evidence record or the gate behaviour bumps this document's
version per `.github/copilot-instructions.md` §9 and must stay consistent with
ADR-0010 and ADR-0011.
