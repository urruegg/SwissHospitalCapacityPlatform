# DR Rehearsal and SIT Restore-Proof Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

Operationalize the reliability/DR baseline by running a repeatable SIT disaster-recovery
rehearsal and capturing restore-proof evidence against the recovery classes and targets in
[`docs/operations/reliability-dr-profile.md`](../operations/reliability-dr-profile.md)
(ADR-0009).

## Scope

### In scope
- SIT DR rehearsal (technical drill or tabletop) for `R1`, `R2`, and `R3` recovery classes.
- Restore-proof capture for in-scope stateful dependencies (Cosmos DB, Redis, Key Vault,
  Service Bus).
- Recording rehearsal and restore evidence in the canonical schemas under
  `docs/sprints/sprint-05/evidence/`.

### Out of scope
- PHI cross-region failover activation (remains default-deny per ADR-0009 Â§3 unless a
  compliance-approved exception is completed).
- PROD execution; this runbook validates SIT and feeds the PROD readiness recommendation.
- Provisioning infrastructure; this runbook is governance documentation only.

## Prerequisites

Mandatory prerequisites:
1. Reliability/DR profile is current and recovery classes are assigned.
2. A non-production (SIT) target with isolated restore destinations is available.
3. `OPS` owns execution; `SEC` is available for the Key Vault restore step.

Repository prerequisites already in place:
1. [`docs/operations/reliability-dr-profile.md`](../operations/reliability-dr-profile.md) â€” recovery classes, targets, evidence schema.
2. [`docs/OPERATIONS.md`](../OPERATIONS.md) â€” DR test evidence checkpoints.
3. [`docs/TEST.md`](../TEST.md) â€” DR rehearsal evidence schema checkpoint.

## Security and Compliance Guardrails

1. No PHI may be restored to a cross-region destination; keep restores in-region.
2. No PHI may be reintroduced via reporting/derived (`R3`) recovery paths.
3. Restore destinations must be isolated from production data planes.
4. Any deviation that cannot be remediated in-drill is recorded as a residual risk with an
   owner and expiry, not silently waived.

## Operational Procedure

### Step 1: Confirm targets and scope

Confirm the recovery class under test and its RTO/RPO target from the reliability/DR
profile, and list the systems in scope.

Expected outcome:
1. Recovery class, target RTO/RPO, and in-scope systems recorded for each scenario.

### Step 2: Execute the rehearsal per recovery class

Run the failover/restore drill for each scenario (`R1`, `R2`, `R3`). Measure actual RTO and
RPO from declared incident start to validated recovery.

Expected outcome:
1. Measured `actualRtoRpo` recorded against `targetRtoRpo` for each scenario.
2. `passFailResult` set to `pass` only when actual values meet the target.

### Step 3: Capture restore proof for stateful dependencies

For each in-scope stateful dependency, perform the documented restore method (point-in-time
restore, rebuild-from-source, soft-delete recovery, dead-letter replay) and validate
integrity.

Expected outcome:
1. A restore-proof entry per dependency with method, result, and integrity check.
2. Each proof is fresh (<= 90 days) relative to the PROD-promotion decision.

### Step 4: Record evidence

Write the rehearsal evidence and restore-proof artifacts using the canonical schemas.

Expected outcome:
1. Rehearsal evidence in `docs/sprints/sprint-05/evidence/<date>-phase-3-sit-dr-rehearsal.json`.
2. Restore proof in `docs/sprints/sprint-05/evidence/<date>-phase-3-sit-restore-proof.json`.
3. The Rehearsal Evidence Register in the reliability/DR profile updated.

## Handoff to Next Process

After this runbook is complete, proceed with:
- Phase 3 evidence record ([`docs/sprints/sprint-05/phase-3-reliability-dr.md`\](../sprints/sprint-05/phase-3-reliability-dr.md)) with SIT pass/fail and PROD readiness recommendation.
- Requires-validation register closure for `RV-02`, `RV-07`, `RV-11`.

## Troubleshooting

If a scenario misses its target (RTO or RPO):
1. Record `passFailResult` as `fail` and capture the gap.
2. Raise a residual risk with owner role and time-bound expiry.
3. Schedule a retest date and do not mark the related register item `validated`.

If a restore proof fails integrity validation:
1. Treat the dependency as having no fresh restore proof (PROD blocker).
2. Re-run the restore after remediation and re-capture evidence.

## Evidence Checklist

Before closing this runbook execution:
- [ ] At least one SIT DR rehearsal documented for `R1`, `R2`, and `R3`.
- [ ] Restore proof captured for every in-scope stateful dependency (<= 90 days).
- [ ] Rehearsal and restore-proof evidence artifacts committed.
- [ ] Residual risks recorded with owner and expiry where targets were missed or assumptions bounded.

## Linked Documentation

- [docs/operations/reliability-dr-profile.md](../operations/reliability-dr-profile.md) â€” recovery classes, targets, evidence schema (ADR-0009)
- [docs/OPERATIONS.md](../OPERATIONS.md) â€” DR test evidence checkpoints
- [docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md](../adr/0009-reliability-and-dr-baseline-for-sit-prod.md) â€” reliability/DR baseline decision
