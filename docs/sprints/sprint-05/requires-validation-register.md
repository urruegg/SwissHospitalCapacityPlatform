# Sprint 05 Requires-Validation Register

| Field | Value |
| ----- | ----- |
| **Version** | 1.4.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.3.0 (Phase 3 reliability/DR closure validated RV-02, RV-07, RV-11) |

## Purpose

Track every item the Sprint 05 review baselines flagged as **Requires validation**
or **Partial / open**, with an owner role, target phase, and the evidence needed
to close it. This is the Phase 0 control artifact for Phase 0 task 2 of
[`docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md)
and the `Requires validation` register requested in the CAF/WAF review
[quick wins](<../../reviews/2026-06-09-ama-caf-waf-review session.md#quick-wins-0-30-days>).

## Source Findings

1. `docs/reviews/2026-06-09-ama-caf-waf-review session.md` (primary CAF/WAF baseline)
2. `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md` (cantonal baseline)
3. `docs/adr/0007-0011-hardening-delta-summary.md` (hardening targets)

## Status Legend

| Status | Meaning |
| ----- | ----- |
| `open` | Not yet evidenced; validation work not started. |
| `in-validation` | Evidence collection or implementation in progress. |
| `validated` | Evidence captured and accepted at the relevant gate. |
| `deferred` | Explicitly deferred with owner, due phase, and risk rationale. |

## Owner Roles

Owner roles follow the approval ownership baseline in
`docs/adr/0007-0011-hardening-delta-summary.md`:

1. **ARCH** — Architecture Owner
2. **SEC** — Security and Compliance Owner
3. **OPS** — Operations and Release Owner
4. **LEGAL** — Legal and Compliance Owner (cantonal gate specific)

## Register

| ID | Finding (Requires validation) | Source | Severity | FR / NFR | CH Control | Owner | Target Phase | Evidence Needed | Status |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| RV-01 | Canton-specific legal applicability not operationalized into a control annex | CAF/WAF §1, §8; cantonal review | High | `NFR-COMP-004` | `CH-C05` | LEGAL | Phase 1 | `docs/compliance/cantonal-annex.md` with canonical fields and legal sign-off | in-validation |
| RV-02 | Reliability / DR target state (RTO/RPO, failover by data class, DR runbooks) undefined | CAF/WAF §4.2, §6 | High | `NFR-REL-003` | Reliability baseline | OPS | Phase 3 | `docs/operations/reliability-dr-profile.md` with R1/R2/R3 targets + rehearsal evidence | validated |
| RV-03 | Policy-as-code enforcement for residency, deployment-type, and PHI transfer not evidenced in CI | CAF/WAF §4.3, §9 | High | `NFR-COMP-004` | `CH-C05` | SEC | Phase 2 | CI policy checks + generated evidence artifact for one SIT run | validated |
| RV-04 | DSR operations and privacy-incident timing matrix not executable workflows | CAF/WAF §1, §8 | High | `FR-GOV-001` | `CH-C02` | SEC | Phase 2 | DSR + incident runbooks with owner/SLA and evidence cycle | open |
| RV-05 | Runtime pattern drift (application-hosted vs Foundry-hosted) target state per workload class unresolved | CAF/WAF §3.4, §5.1 | Medium | `NFR-AI-001` | `CH-C10` | ARCH | Phase 1 | Runtime decision matrix + ADR consistency confirmation | validated |
| RV-06 | CAF landing-zone governance evidence (MG hierarchy, policy assignment, RBAC scopes) weaker than intent | CAF/WAF §4.1, §7 | Medium | `FR-GOV-003` | `CH-C03` | ARCH | Phase 2 | Landing-zone governance evidence document | open |
| RV-07 | HITL/audit persistence implementation evidence required (Cosmos DB baseline) | CAF/WAF §10 matrix `FR-GOV-001` | High | `FR-GOV-001` | `CH-C03` | OPS | Phase 3 | HITL evidence schema captured; persistence restore proof | validated |
| RV-08 | Least-privilege operational recertification evidence missing | CAF/WAF §10 matrix `NFR-SEC-001` | Medium | `NFR-SEC-001` | `CH-C02` | SEC | Phase 2 | Access recertification run + evidence artifact | open |
| RV-09 | Cost governance (token/telemetry budgets) lacks evidence loop | CAF/WAF §4.2, §9 | Low | `NFR-COMP-004` | n/a | OPS | Phase 3 | FinOps thresholds + telemetry sampling policy | deferred |
| RV-10 | Control-effectiveness metrics (security, AI safety, HITL) in SIT/PROD not consolidated | CAF/WAF §4.3, §7 | Medium | `NFR-AI-001` | `CH-C10` | SEC | Phase 4 | Consolidated control-effectiveness report artifact | validated |
| RV-11 | DR game-day / restore proof for memory and audit stores missing | CAF/WAF §5.2 | High | `NFR-REL-003` | Reliability baseline | OPS | Phase 3 | SIT DR rehearsal output + restore proof (<= 90 days) | validated |
| RV-12 | Architecture drift detection between ADRs and deployed IaC not formalized | CAF/WAF §5.1 | Medium | `FR-GOV-003` | `CH-C03` | ARCH | Phase 4 | Drift detection golden task / control note | validated |

## Phase 1 Documentation Baseline Closure (2026-06-09)

The Phase 1 document-first baseline created the artifacts that advance the Phase 1 register
items and seed the Phase 2/Phase 3 items:

| RV ID | Phase 1 action | New status | Evidence artifact |
| ----- | ----- | ----- | ----- |
| RV-01 | Cantonal annex schema + seed register created | `in-validation` | [`docs/compliance/cantonal-annex.md`](../../compliance/cantonal-annex.md) — pending legal sign-off (Phase 2) |
| RV-02 | Reliability/DR profile with R1/R2/R3 targets created | `in-validation` | [`docs/operations/reliability-dr-profile.md`](../../operations/reliability-dr-profile.md) — rehearsal evidence Phase 3 |
| RV-05 | Runtime decision matrix + AI/ARCHITECTURE consistency confirmed | `validated` | [`docs/architecture/runtime-pattern-decision-matrix.md`](../../architecture/runtime-pattern-decision-matrix.md) |

CAF/WAF delta closure across all findings is tracked in
[`docs/architecture/caf-waf-alignment-matrix.md`](../../architecture/caf-waf-alignment-matrix.md).
All other items remain at their target phase; high-severity `open`/`in-validation` items
stay PROD-promotion blockers per the closure rules below.

## Phase 2 Policy-as-Code Closure (2026-06-09)

The Phase 2 policy-as-code implementation converts the documented residency,
deployment-type, and PHI-transfer controls into an enforceable CI and promotion
gate, advancing the Phase 2 register item:

| RV ID | Phase 2 action | New status | Evidence artifact |
| ----- | ----- | ----- | ----- |
| RV-03 | Policy gate, evidence schema, exception-expiry blocker, and cantonal annex checks implemented and run for the SIT scope | `validated` | [`phase-2-policy-gate.md`](phase-2-policy-gate.md) and [`evidence/2026-06-09-phase-2-sit-policy-gate.json`](evidence/2026-06-09-phase-2-sit-policy-gate.json) |

## Phase 3 Reliability and DR Closure (2026-06-09)

The Phase 3 reliability/DR operationalization executed a SIT DR rehearsal and captured
restore proof, advancing the Phase 3 register items:

| RV ID | Phase 3 action | New status | Evidence artifact |
| ----- | ----- | ----- | ----- |
| RV-02 | R1/R2/R3 targets validated; DR runbook added; SIT rehearsal executed | `validated` | [`phase-3-reliability-dr.md`](phase-3-reliability-dr.md) and [`evidence/2026-06-09-phase-3-sit-dr-rehearsal.json`](evidence/2026-06-09-phase-3-sit-dr-rehearsal.json) |
| RV-07 | HITL/audit persistence point-in-time restore proof captured | `validated` | [`evidence/2026-06-09-phase-3-sit-restore-proof.json`](evidence/2026-06-09-phase-3-sit-restore-proof.json) |
| RV-11 | SIT DR game-day rehearsal + restore proof (<= 90 days) captured | `validated` | [`phase-3-reliability-dr.md`](phase-3-reliability-dr.md) and [`evidence/2026-06-09-phase-3-sit-restore-proof.json`](evidence/2026-06-09-phase-3-sit-restore-proof.json) |

PROD promotion for the reliability domain stays `pending` until OPS/SEC approvals and
documented business acceptance of the residual risks recorded in the phase-3 evidence
record are captured.

## Phase 4 Autonomous Agent Execution Hardening Closure (2026-06-09)

The Phase 4 agent-hardening implementation enforced deny-by-default for missing
HITL evidence, validated runtime boundary enforcement, and formalized ADR-vs-IaC
drift detection, advancing the Phase 4 register items:

| RV ID | Phase 4 action | New status | Evidence artifact |
| ----- | ----- | ----- | ----- |
| RV-10 | HITL / AI-safety / boundary control-effectiveness consolidated into the phase evidence record | `validated` | [`phase-4-agent-hardening.md`](phase-4-agent-hardening.md) Control-Effectiveness Summary and [`evidence/2026-06-09-phase-4-sit-golden-replay.json`](evidence/2026-06-09-phase-4-sit-golden-replay.json) |
| RV-12 | ADR-vs-IaC drift detection golden task / control note formalized | `validated` | [`agents/drift-analyzer/golden-tasks.md`](../../agents/drift-analyzer/golden-tasks.md) `adr-iac-drift` fixture |

PROD promotion for the autonomous-execution domain stays `pending` until governance
reviewers confirm the controls are sufficient for subsequent sprints (Phase 4 PROD gate).

## Closure Rules

1. An item may move to `validated` only when its **Evidence Needed** is attached
   to a PR and accepted at the gate named in **Target Phase** (see
   [`gate-sequence.md`](gate-sequence.md)).
2. An item may move to `deferred` only with an explicit owner, due phase, and
   risk rationale recorded in the PR that defers it, per the sprint Acceptance
   Criteria.
3. High-severity `open` or `in-validation` items are PROD promotion blockers for
   their target phase, consistent with the consolidated enforcement gate model.
4. Any change to this register bumps the document version per
   `.github/copilot-instructions.md` §9.

