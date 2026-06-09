# Cantonal Legal Applicability Annex

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | N/A |

## Purpose

Operationalize canton-specific legal applicability into an explicit, evidence-backed
control annex, so that federal baseline controls are not assumed to satisfy cantonal
public-sector production requirements. This annex is the Phase 1 deliverable for the
cantonal applicability gate defined in
[`docs/adr/0011-cantonal-legal-applicability-gate.md`](../adr/0011-cantonal-legal-applicability-gate.md)
and closes register item `RV-01` in
[`sprints/sprint-05/requires-validation-register.md`](../../sprints/sprint-05/requires-validation-register.md).

It addresses high-priority finding §9.1 and §8 of the CAF/WAF review
[baseline](<../reviews/2026-06-09-ama-caf-waf-review session.md#9-recommendations-and-next-steps>)
and the cantonal review baseline
`docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`.

## Scope

1. Applies to any workload promoted for a named canton ("cantonal workload").
2. Federal baseline controls (`CH-C01`..`CH-C10` in
   [`docs/COMPLIANCE.md`](../COMPLIANCE.md)) remain the foundation; this annex records
   the **delta** each canton adds or modifies.
3. This annex is governance documentation only. It creates no infrastructure and does
   not itself constitute legal sign-off; sign-off is recorded per the approval model
   below.

## Annex Entry Schema (mandatory)

Per ADR-0011 Target 1, every canton entry must include all of the following fields.
Entries missing any field are treated as `requires-validation` and are PROD-promotion
blockers for that canton scope.

| Field | Description |
| ----- | ----- |
| `cantonId` | ISO 3166-2:CH canton code (for example `ZH`, `BE`, `VD`). |
| `legalSource` | Authoritative cantonal legal/regulatory source reference (statute, ordinance, or official guidance). |
| `obligationSummary` | Short summary of the canton-specific obligation or deviation from the federal baseline. |
| `controlMappings` | Mapped federal control IDs (`CH-C01`..`CH-C10`) plus any canton-specific delta control. |
| `controlOwner` | Accountable owner role (`LEGAL`, `SEC`, `OPS`, or `ARCH`). |
| `evidenceArtifacts` | Evidence artifact link(s) demonstrating the control is satisfied. |
| `status` | One of `design-aligned`, `implemented`, `requires-validation` (per ADR-0011 §4). |
| `openValidationPoints` | Unresolved validation points with owner and due phase. |

### Status Legend

| Status | Meaning |
| ----- | ----- |
| `design-aligned` | Control is documented and intended, but implementation evidence is not yet captured. |
| `implemented` | Control is implemented and evidence artifact is attached. |
| `requires-validation` | Applicability or evidence is incomplete; treated as an open gap. |

## Approval Ownership

Per ADR-0011 Target 3, cantonal applicability sign-off requires all of:

1. **LEGAL** — Legal and Compliance Owner (cantonal legal applicability sign-off).
2. **SEC** — Security and Compliance Owner (data class, residency, control mapping).
3. **OPS** — Operations and Release Owner (production readiness and evidence completeness).

Sign-off is echoed with approver handle and timestamp in the promotion PR, consistent
with the PR evidence checklist
[`sprints/sprint-05/pr-evidence-checklist.md`](../../sprints/sprint-05/pr-evidence-checklist.md).

## Canton Register

The register below is the canonical applicability map. Sprint 5 seeds the register with
the first target-canton scope. Additional cantons are appended as rollout plans are
confirmed; each addition bumps this document's version per
`.github/copilot-instructions.md` §9.

> No canton entry is `implemented` until its evidence artifacts are attached and the
> approval ownership above is recorded. All seed entries are therefore
> `requires-validation` pending Phase 2 evidence automation and legal sign-off.

| `cantonId` | `legalSource` | `obligationSummary` | `controlMappings` | `controlOwner` | `evidenceArtifacts` | `status` | `openValidationPoints` |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| `ZH` | Cantonal health and data-protection legislation (canton of Zürich); confirm exact statute/ordinance reference during legal review | Canton-specific data-protection supervisory authority and health-data handling obligations layered on FADP/EPDG baseline | `CH-C01`, `CH-C03`, `CH-C05`, `CH-C07` | LEGAL | Pending (Phase 2 evidence pack) | `requires-validation` | Confirm statute citation; confirm whether cantonal authority adds breach-notification or residency deltas |
| `BE` | Cantonal health and data-protection legislation (canton of Bern); confirm exact statute/ordinance reference during legal review | Bilingual obligations and cantonal supervisory authority deltas over the federal baseline | `CH-C01`, `CH-C04`, `CH-C05`, `CH-C06` | LEGAL | Pending (Phase 2 evidence pack) | `requires-validation` | Confirm DSR routing to cantonal authority; confirm language-of-record obligations |
| `VD` | Cantonal health and data-protection legislation (canton of Vaud); confirm exact statute/ordinance reference during legal review | Romandie cantonal supervisory authority deltas and EPR participation specifics | `CH-C05`, `CH-C07`, `CH-C08` | LEGAL | Pending (Phase 2 evidence pack) | `requires-validation` | Confirm EPR/EPDG conformance boundary for cantonal reference community |

## Promotion Threshold

Per ADR-0011 Target 2, **zero unresolved high-severity legal applicability gaps** are
permitted for PROD promotion in the target canton scope. While any in-scope canton entry
is `requires-validation`, that canton's workload is limited to SIT/non-production
validation (ADR-0011 §3).

## Exceptions

Any exception to this gate follows the exception-management baseline in
[`docs/adr/0007-0011-hardening-delta-summary.md`](../adr/0007-0011-hardening-delta-summary.md#exception-management-baseline):
rationale, compensating controls, owner, explicit expiry (max 90 days for critical
governance exceptions), mitigation plan, and follow-up validation date. Expired
exceptions are hard PROD-promotion blockers.

## Revalidation Cadence

Per ADR-0011 Target 5:

1. Monthly applicability revalidation for active cantonal deployments.
2. Immediate reassessment on any cantonal legal or regulatory change.
3. Outcomes recorded as governance evidence and follow-up issues for any drift.

## Traceability

| Requirement | Control | ADR | Register item |
| ----- | ----- | ----- | ----- |
| `NFR-COMP-001`, `NFR-COMP-002` | `CH-C05`, `CH-C07` | ADR-0011 | `RV-01` |
| `NFR-COMP-005`, `NFR-COMP-010` | `CH-C01`, `CH-C03` | ADR-0011 | `RV-01` |

## Change Control

Any change to the schema, approval model, or canton register bumps this document's
version per `.github/copilot-instructions.md` §9 and must stay consistent with ADR-0011.
