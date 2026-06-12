# Reliability and Disaster Recovery Profile

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (Phase 1 target-state baseline; rehearsal/restore evidence pending) |

## Purpose

Define the reliability and disaster-recovery (DR) target state â€” recovery classes,
RTO/RPO targets, failover boundaries by data class, and the DR evidence model â€” so that
reliability moves from intent to a measurable, release-gated baseline. This is the Phase 1
deliverable for the reliability/DR baseline gate in
[`docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md`](../adr/0009-reliability-and-dr-baseline-for-sit-prod.md)
and seeds register items `RV-02`, `RV-07`, and `RV-11` in
[`docs/sprints/sprint-05/requires-validation-register.md`\](../sprints/sprint-05/requires-validation-register.md).

It addresses CAF/WAF review findings Â§4.2 (Reliability), Â§5.2, and Â§6, and the Â§9 High 2
recommendation.

## Scope

1. Defines reliability/DR targets and the evidence model for SIT and PROD promotion.
2. The Phase 3 SIT DR rehearsal and restore-proof capture are recorded in the
   [Rehearsal Evidence Register](#rehearsal-evidence-register) and
   [Restore-Proof Register](#restore-proof-register) below.
3. This profile is governance documentation; it provisions no infrastructure.

## Recovery Classes and Targets

Per ADR-0009 Target 1, every in-scope workflow is assigned a recovery class. The baseline
targets below are mandatory unless an approved exception is recorded.

| Recovery class | Workflow type | Example flows | RTO target | RPO target |
| ----- | ----- | ----- | ----- | ----- |
| `R1` | Patient-affecting critical | Bed/flow status, discharge coordination triggers (FR-CX, FR-DC) | <= 60 minutes | <= 15 minutes |
| `R2` | High-priority operational | Forecast inference, capacity recommendations (FR-FC) | <= 4 hours | <= 1 hour |
| `R3` | Supporting / reporting | Aggregated reporting, non-critical analytics | <= 24 hours | <= 24 hours |

## Failover Boundaries by Data Class

| Data class | Failover posture | Rule |
| ----- | ----- | ----- |
| PHI-sensitive | Cross-region failover **default-deny** | PHI cross-region failover requires a compliance-approved exception (ADR-0009 Â§3, ADR-0003/`AR-D-003`). Within Switzerland regions, prefer zone redundancy over cross-region. |
| Operational (non-PHI) | Zone-redundant, region failover allowed with evidence | Region failover permitted where supporting services are GA-in-region and restore proof exists. |
| Reporting / derived | Best-effort recovery | Recovery within `R3` targets; no PHI may be reintroduced via failover paths. |

## Dependency Redundancy Posture

| Dependency | Reliability posture | Restore-proof requirement |
| ----- | ----- | ----- |
| Conversation / audit store (Cosmos DB baseline per ADR-0007) | Zone-redundant writes; point-in-time restore enabled | SIT restore proof <= 90 days (`RV-07`, `RV-11`) |
| Session cache (Azure Cache for Redis) | Zone-redundant tier where supported | Rebuild-from-source validated; no PHI persisted beyond policy |
| Secrets (Key Vault) | Zone-redundant; soft-delete + purge protection | Recovery procedure documented |
| Async messaging (Service Bus) | Premium for isolation; geo-DR pairing for non-PHI | Dead-letter and replay validated |

## DR Rehearsal Evidence Schema

Per ADR-0009 Target 2, each rehearsal records all fields below. This schema is the
"DR test evidence placeholder" requested in the review Â§9 quick wins.

| Field | Description |
| ----- | ----- |
| `scenarioId` | Unique rehearsal scenario identifier. |
| `systemsInScope` | Systems/dependencies covered by the rehearsal. |
| `targetRtoRpo` | Target RTO/RPO for the recovery class under test. |
| `actualRtoRpo` | Measured RTO/RPO achieved. |
| `passFailResult` | `pass` or `fail` against target. |
| `gaps` | Gaps or deviations observed. |
| `owner` | Accountable owner role (`OPS`). |
| `retestDate` | Scheduled retest date. |

### Rehearsal Evidence Register

The first SIT DR rehearsal (technical drill) was executed on 2026-06-09 (Phase 3, `RV-11`).
Full evidence: [`docs/sprints/sprint-05/evidence/2026-06-09-phase-3-sit-dr-rehearsal.json`\](../sprints/sprint-05/evidence/2026-06-09-phase-3-sit-dr-rehearsal.json).

| `scenarioId` | Recovery class | Target RTO/RPO | Actual RTO/RPO | Status |
| ----- | ----- | ----- | ----- | ----- |
| `DR-SIT-R1-01` | `R1` | 60 min / 15 min | 38 min / 9 min | pass |
| `DR-SIT-R2-01` | `R2` | 4 h / 1 h | 72 min / 22 min | pass |
| `DR-SIT-R3-01` | `R3` | 24 h / 24 h | 220 min / 30 min | pass |

PHI cross-region failover was not exercised; it remains default-deny (ADR-0009 Â§3) with no
active exception.

### Restore-Proof Register

SIT restore proof captured on 2026-06-09 (Phase 3, `RV-07`, `RV-11`). Full evidence:
[`docs/sprints/sprint-05/evidence/2026-06-09-phase-3-sit-restore-proof.json`\](../sprints/sprint-05/evidence/2026-06-09-phase-3-sit-restore-proof.json).

| Dependency | Restore method | Result | Freshness |
| ----- | ----- | ----- | ----- |
| Conversation/audit store (Cosmos DB) | Point-in-time restore | pass | <= 90 days |
| Session cache (Redis) | Rebuild-from-source | pass | <= 90 days |
| Secrets (Key Vault) | Soft-delete recovery | pass | <= 90 days |
| Async messaging (Service Bus) | Dead-letter drain and replay | pass | <= 90 days |

## Restore-Proof Freshness Rule

Per ADR-0009 Target 3, every in-scope stateful dependency must have at least one
successful SIT restore-proof artifact within the previous **90 days** before PROD
promotion. A missing or stale restore proof is a PROD-promotion blocker.

## PHI Failover Exception Gate

Per ADR-0009 Target 4, a PHI cross-region failover exception requires LEGAL, SEC, and OPS
approval, documented compensating controls, and an explicit expiry not exceeding 90 days,
consistent with the exception-management baseline in
[`docs/adr/0007-0011-hardening-delta-summary.md`](../adr/0007-0011-hardening-delta-summary.md#exception-management-baseline).

## Revalidation Cadence

Per ADR-0009 Target 5:

1. Monthly evidence-freshness review.
2. Quarterly DR rehearsal minimum for `R1` and `R2` workflows.
3. Semiannual DR rehearsal minimum for `R3` workflows.

## Promotion Gate Summary

| Gate | Reliability exit evidence |
| ----- | ----- |
| SIT | At least one DR rehearsal/tabletop documented; restore/failover assumptions validated or bounded-risk accepted; restore proof fresh (<= 90 days). |
| PROD | RTO/RPO commitments stated; unresolved risk register attached; documented business acceptance of residual risk. |

## Traceability

| Requirement | Control | ADR | Register item |
| ----- | ----- | ----- | ----- |
| `NFR-REL-001`, `NFR-REL-003` | Reliability baseline | ADR-0009 | `RV-02`, `RV-11` |
| `FR-GOV-001` (HITL/audit persistence) | `CH-C03` | ADR-0007, ADR-0009 | `RV-07` |
| `NFR-COMP-007` (PHI failover default-deny) | `CH-C05` | ADR-0009 | `RV-02` |

## Change Control

Any change to recovery classes, targets, or the evidence schema bumps this document's
version per `.github/copilot-instructions.md` Â§9 and must stay consistent with ADR-0009.
