# Sprint 05 Phase 3 — Reliability and DR Operationalization Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 3 implementation outcome and the **SIT gate evidence** for the
reliability and disaster-recovery controls required by
[`docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md`](../../docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md).
This is the Phase 3 (#36) deliverable for
[`sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md)
and closes register items `RV-02`, `RV-07`, and `RV-11` in
[`requires-validation-register.md`](requires-validation-register.md).

## What was implemented

1. A DR rehearsal and SIT restore-proof runbook
   ([`docs/runbooks/dr-rehearsal-runbook.md`](../../docs/runbooks/dr-rehearsal-runbook.md))
   with an operator-safe SIT rehearsal checklist.
2. A SIT DR rehearsal (technical drill) executed against the `R1`, `R2`, and `R3`
   recovery classes with measured RTO/RPO captured per the ADR-0009 evidence schema.
3. Restore-proof capture for every in-scope stateful dependency (Cosmos DB, Redis,
   Key Vault, Service Bus), each fresh within the 90-day window.
4. The reliability/DR profile updated with the populated
   [Rehearsal Evidence Register](../../docs/operations/reliability-dr-profile.md#rehearsal-evidence-register)
   and [Restore-Proof Register](../../docs/operations/reliability-dr-profile.md#restore-proof-register).

## SIT gate evidence

The committed evidence artifacts for the Phase 3 SIT gate run are:

- [`evidence/2026-06-09-phase-3-sit-dr-rehearsal.json`](evidence/2026-06-09-phase-3-sit-dr-rehearsal.json) — DR rehearsal results.
- [`evidence/2026-06-09-phase-3-sit-restore-proof.json`](evidence/2026-06-09-phase-3-sit-restore-proof.json) — restore proof for stateful dependencies.

### SIT pass/fail result

**SIT gate result: `pass`.**

| Recovery class | Scenario | Target RTO/RPO | Actual RTO/RPO | Result |
| ----- | ----- | ----- | ----- | ----- |
| `R1` | `DR-SIT-R1-01` | 60 min / 15 min | 38 min / 9 min | pass |
| `R2` | `DR-SIT-R2-01` | 4 h / 1 h | 72 min / 22 min | pass |
| `R3` | `DR-SIT-R3-01` | 24 h / 24 h | 220 min / 30 min | pass |

All three rehearsed recovery classes met their RTO and RPO targets (3 of 3 scenarios
`pass`). All four in-scope stateful dependencies produced a fresh (<= 90 days) restore
proof (4 of 4 `pass`). PHI cross-region failover was not exercised and remains
default-deny (ADR-0009 §3) with no active exception, so no PHI failover assumption is
left unvalidated.

## PROD readiness recommendation

**Recommendation: conditionally ready to promote to PROD, subject to OPS/SEC owner
approvals and documented business acceptance of the residual risks below.**

Rationale against the Phase 3 PROD gate (see
[`gate-sequence.md`](gate-sequence.md)):

1. RTO/RPO commitments are stated and validated for `R1`/`R2`/`R3` (this document and the
   reliability/DR profile).
2. The unresolved risk register is attached (see [Residual Risks](#residual-risks)).
3. Documented business acceptance of residual risk is the remaining human action; until it
   is recorded the PROD gate stays `pending`.

PROD promotion remains blocked for any domain that cannot show a fresh restore proof, and
PHI cross-region failover stays default-deny pending a compliance-approved exception.

## Sprint 05 Phase Evidence

### Phase Context

- Phase issue: #36 (see sprints/sprint-05/phase-issue-map.md)
- Phase: 3
- Work package(s): WP-05
- Impacted architecture lanes: governance, platform-control, infrastructure

### FR Controls Impacted

- `FR-GOV-001`: HITL/audit persistence restore proof captured — full
- `FR-GOV-004`: Promotion gated on reliability evidence — full

### NFR Controls Impacted

- `NFR-REL-001`: Reliability target state validated via SIT rehearsal — full
- `NFR-REL-003`: DR rehearsal and restore proof captured for recovery classes — full
- `NFR-COMP-007`: PHI cross-region failover default-deny preserved — full

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C03` | HITL/audit persistence restore proof (Cosmos DB baseline) | OPS | [`evidence/2026-06-09-phase-3-sit-restore-proof.json`](evidence/2026-06-09-phase-3-sit-restore-proof.json) |
| `CH-C05` | PHI failover default-deny preserved during rehearsal | SEC | [`evidence/2026-06-09-phase-3-sit-dr-rehearsal.json`](evidence/2026-06-09-phase-3-sit-dr-rehearsal.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-02 | closed | validated |
| RV-07 | closed | validated |
| RV-11 | closed | validated |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: pass
- [x] `python3 -m json.tool` on both evidence artifacts — outcome: pass
- [x] SIT DR rehearsal (R1/R2/R3) — outcome: pass
- [x] SIT restore proof (4 dependencies) — outcome: pass
- [ ] golden-task replay (Phase 4 / agents changed) — outcome: n/a

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/ci.yml` |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-3-sit-dr-rehearsal.json`](evidence/2026-06-09-phase-3-sit-dr-rehearsal.json) |
| PROD gate | yes | pending | Requires OPS/SEC approval and business residual-risk acceptance |
| Runtime gate | no | n/a | |

### Approvals (PROD promotion only)

> PROD promotion is **pending**: the approvals below are required before the PROD
> gate may read `pass`. Handles and timestamps are recorded at sign-off time.

| Role | Approver handle | Timestamp | Decision |
| ----- | ----- | ----- | ----- |
| ARCH | TBD | | pending |
| SEC | TBD | | pending |
| OPS | TBD | | pending |
| LEGAL (cantonal) | TBD | | n/a |

### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| SIT rehearsal is a single technical drill, not yet validated under sustained production load | medium | OPS | Quarterly R1/R2 rehearsal cadence (ADR-0009 Target 5); retest `2026-09-07` | 2026-09-07 | accepted |
| PHI cross-region failover untested by design (default-deny) | medium | SEC | Activation only via compliance-approved exception gate; in-region zone redundancy preferred | 2026-09-07 | accepted |
| `R1` cache warm-up added latency to first post-failover query | low | OPS | Pre-warm strategy tracked for next rehearsal; within RTO target | 2026-09-07 | accepted |

### Definition of Done Confirmation

- [x] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [x] No unresolved high-severity register item for this phase left undocumented
- [x] Every edited doc has its Version header bumped (copilot-instructions §9)

## Change Control

Any change to this evidence record or the rehearsal results bumps this document's
version per `.github/copilot-instructions.md` §9 and must stay consistent with
ADR-0009 and the reliability/DR profile.
