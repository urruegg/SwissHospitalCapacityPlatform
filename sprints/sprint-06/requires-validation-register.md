# Sprint 06 Requires-Validation Register

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Track every Sprint 06 onboarding and specialty-capacity delta that **requires
validation** before promotion, with an owner role, target phase, and the evidence
needed to close it. This is the Phase 0 control artifact for Phase 0 task 2 of
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md),
covering the "New Sprint 6 Requirement Delta (to be baselined)" and the
"Provider Extension for Capacity Onboarding" scope of that sprint file.

## Source Findings

1. `sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md` (FR/NFR deltas, provider extension, phase plan)
2. `docs/reviews/2026-06-09-ama-cto-mentor-Review.md` (onboarding review baseline)
3. `docs/reviews/2026-06-09-ama-sd-review.md` (solution-design review baseline)

## Status Legend

| Status | Meaning |
| ----- | ----- |
| `open` | Not yet evidenced; validation work not started. |
| `in-validation` | Evidence collection or implementation in progress. |
| `validated` | Evidence captured and accepted at the relevant gate. |
| `deferred` | Explicitly deferred with owner, due phase, and risk rationale. |

## Owner Roles

Owner roles follow the same approval ownership baseline used across the platform:

1. **ARCH** — Architecture Owner
2. **SEC** — Security and Compliance Owner
3. **OPS** — Operations and Release Owner
4. **LEGAL** — Legal and Compliance Owner (cantonal / re-identification gate specific)

## Register

### Onboarding deltas (patient minimum-data lane)

| ID | Finding (Requires validation) | Source | Severity | FR / NFR | CH Control | Owner | Target Phase | Evidence Needed | Status |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| RV-06-01 | Patient onboarding minimum-metadata contract not yet baselined as an enforceable data contract | Sprint 6 §Scope, FR-ONB-001 | High | `FR-ONB-001`, `NFR-COMP-011` | `CH-C01` | SEC | Phase 1 | Patient-minimum onboarding contract schema in `docs/DATA.md` with purpose tags and minimized field set | open |
| RV-06-02 | Deterministic-service vs agentic-flow classification criterion for onboarding undocumented | Sprint 6 §Guiding Principles, FR-ONB-004 | Medium | `FR-ONB-004` | `CH-C10` | ARCH | Phase 1 | Documented classification criterion in `docs/SD.md`/`docs/ARCHITECTURE.md` applied to onboarding flows | open |
| RV-06-03 | Onboarding identity and cross-tenant boundaries not explicit or auditable | Sprint 6 §NFR, NFR-SEC-005 | High | `NFR-SEC-005` | `CH-C02` | SEC | Phase 2 | Cross-tenant/onboarding identity boundary check enforced in policy/CI with evidence artifact | open |
| RV-06-04 | Quasi-identifier re-identification risk through onboarding attributes not controlled | Sprint 6 §Risks, NFR-COMP-011 | High | `NFR-COMP-011` | `CH-C01`, `CH-C05` | SEC | Phase 2 | Minimization + re-identification risk rule in `docs/COMPLIANCE.md` and policy gate | open |
| RV-06-05 | Onboarding services degraded-mode and recovery behavior undefined | Sprint 6 §NFR, NFR-REL-005 | Medium | `NFR-REL-005` | `CH-C03` | OPS | Phase 3 | Degraded-mode behavior spec + SIT evidence of recovery controls for onboarding services | open |

### Specialty-capacity deltas (capacity onboarding lane + provider extension)

| ID | Finding (Requires validation) | Source | Severity | FR / NFR | CH Control | Owner | Target Phase | Evidence Needed | Status |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| RV-06-06 | Specialty-driven capacity onboarding contract and provider specialty profiles not baselined | Sprint 6 §Scope, FR-ONB-002, FR-ONB-003 | High | `FR-ONB-002`, `FR-ONB-003` | `CH-C01` | ARCH | Phase 1 | Specialty-capacity onboarding contract schema in `docs/DATA.md` with specialty tags and provider profile model | open |
| RV-06-07 | Specialty metadata quality checks and controlled versioning missing | Sprint 6 §NFR, NFR-DQ-005 | Medium | `NFR-DQ-005` | `CH-C03` | ARCH | Phase 2 | Specialty metadata quality checks + versioned taxonomy with schema gate in CI | open |
| RV-06-08 | Klinik Hirslanden specialty-weighted capacity onboarding signals not evidenced in SIT | Sprint 6 §Klinik Hirslanden incorporation | High | `FR-ONB-002`, `FR-ONB-003` | `CH-C01` | OPS | Phase 3 | Synthesized Hirslanden specialty-capacity dataset + SIT contract/schema validation evidence | open |
| RV-06-09 | Spital Zollikerberg specialty/care-mode and Hospital-at-Home onboarding signals not evidenced in SIT | Sprint 6 §Spital Zollikerberg incorporation | High | `FR-ONB-002`, `FR-ONB-003` | `CH-C01` | OPS | Phase 3 | Synthesized Zollikerberg specialty-capacity + HaH dataset with SIT validation; HaH fields optional and provider-scoped | open |
| RV-06-10 | IaC-first deployable bootstrap and synthesized-data validation for onboarding not reproducible | Sprint 6 §Data Platform Kickstart, NFR-MAINT-005 | High | `NFR-MAINT-005` | `CH-C03` | OPS | Phase 1 | IaC modules + synthesized onboarding datasets with CI contract/schema validation and FR/NFR/CH traceability mapping | open |

## FR / NFR / CH Traceability Anchors

The Sprint 06 requirement deltas map to controls as follows. This anchor table is
the traceability baseline that every phase PR must reference via
[`pr-evidence-checklist.md`](pr-evidence-checklist.md).

| Requirement | Description | CH Control | Register item(s) |
| ----- | ----- | ----- | ----- |
| `FR-ONB-001` | Onboard patients using a minimum required metadata set only | `CH-C01` | RV-06-01 |
| `FR-ONB-002` | Onboard hospital capacity using specialty-tagged metadata | `CH-C01` | RV-06-06, RV-06-08, RV-06-09 |
| `FR-ONB-003` | Support provider-specific specialty profiles for capacity planning | `CH-C01` | RV-06-06, RV-06-08, RV-06-09 |
| `FR-ONB-004` | Classify onboarding workflows as deterministic service vs agentic flow | `CH-C10` | RV-06-02 |
| `NFR-COMP-011` | Enforce minimum-sensitive-data controls and purpose tags | `CH-C01`, `CH-C05` | RV-06-01, RV-06-04 |
| `NFR-SEC-005` | Explicit, auditable onboarding identity and cross-tenant boundaries | `CH-C02` | RV-06-03 |
| `NFR-DQ-005` | Specialty metadata quality checks and controlled versioning | `CH-C03` | RV-06-07 |
| `NFR-REL-005` | Onboarding services available under defined degraded-mode behavior | `CH-C03` | RV-06-05 |
| `NFR-MAINT-005` | IaC-first deployable services with reproducible environment bootstrap | `CH-C03` | RV-06-10 |

## Closure Rules

1. An item may move to `validated` only when its **Evidence Needed** is attached
   to a PR and accepted at the gate named in **Target Phase** (see
   [`gate-sequence.md`](gate-sequence.md)).
2. An item may move to `deferred` only with an explicit owner, due phase, and
   risk rationale recorded in the PR that defers it.
3. High-severity `open` or `in-validation` items are PROD promotion blockers for
   their target phase, consistent with the consolidated enforcement gate model.
4. Any change to this register bumps the document version per
   `.github/copilot-instructions.md` §9.
