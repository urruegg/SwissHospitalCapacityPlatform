# Sprint 6 Synthesized Onboarding Datasets (SIT)

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.1.0 (Phase 2 onboarding policy and schema enforcement gate) |

## Purpose

This pack holds the **non-production, synthesized** SIT datasets and their
contract schemas for the Sprint 6 minimum-data onboarding and specialty-driven
capacity onboarding lanes. It is the executable Phase 1 deliverable for
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../../sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
"Data Platform Kickstart" and closes/advances register item `RV-06-10` in
[`sprints/sprint-06/requires-validation-register.md`](../../sprints/sprint-06/requires-validation-register.md).

All records are fabricated. No real patient or provider data is present. The
patient lane carries only a minimized, pseudonymous field set; direct
identifiers are rejected by the validator.

## Contents

| Path | Purpose |
| ----- | ----- |
| `schema/patient-minimum-onboarding.schema.json` | `DC-ONB-PATIENT-v1` minimum-data patient onboarding contract |
| `schema/specialty-capacity-onboarding.schema.json` | `DC-ONB-CAPACITY-v1` specialty-driven capacity onboarding contract |
| `schema/provider-hirslanden-capacity.schema.json` | `DC-ONB-CAPACITY-HIRSLANDEN-v1` provider extension |
| `schema/provider-zollikerberg-capacity.schema.json` | `DC-ONB-CAPACITY-ZOLLIKERBERG-v1` provider extension (Hospital-at-Home optional) |
| `datasets/*.json` | Synthesized SIT datasets, one per contract |
| `traceability.json` | Dataset -> schema -> FR/NFR/CH and RV register mapping |
| `validate_datasets.py` | Dependency-free contract/schema + minimization validator |
| `tests/test_validate_datasets.py` | Unit tests for the validator |

## How to run

```bash
# Validate all datasets and print the evidence artifact
python3 data/synthetic/validate_datasets.py

# Write a dated SIT evidence artifact
python3 data/synthetic/validate_datasets.py \
  --output sprints/sprint-06/evidence/2026-06-09-phase-1-sit-synthesized-data.json

# Run the unit tests
python3 -m unittest discover -s data/synthetic/tests
```

The validator exits non-zero on any schema, minimization, capacity-invariant,
onboarding-policy (purpose-tag, specialty-metadata, tenant-boundary),
provider degraded-mode reliability, or traceability-coverage failure. CI runs it in
[`.github/workflows/data-contracts.yml`](../../.github/workflows/data-contracts.yml).

## Controls enforced

1. **Schema conformance** — every dataset validates against its declared
   contract (`additionalProperties: false`, enums, patterns, bounds, date
   format). Supports `FR-ONB-001`, `FR-ONB-002`, `FR-ONB-003`, `NFR-DQ-005`.
2. **Re-identification minimization** — onboarding records must not contain
   forbidden direct-identifier fields (name, birth date, AHV/SSN, address,
   contact, insurance/patient ids). Supports `NFR-COMP-011`, `CH-C01`.
3. **Capacity invariant** — `bedsAvailable` never exceeds `bedsTotal`.
4. **Specialty taxonomy versioning** — capacity datasets declare a
   `specialtyTaxonomyVersion` (`NFR-DQ-005`).
5. **FR/NFR/CH traceability coverage** — every dataset maps to at least one FR
   and one CH control (`NFR-MAINT-005`).

### Phase 2 onboarding policy and schema enforcement

These checks are layered on top of the Phase 1 schema gate (advancing register
items `RV-06-03`, `RV-06-04`, `RV-06-07`):

6. **Minimum-data purpose-tag policy** — every record `purposeTag` must be in the
   dataset-level `purposeTags` allowlist, and patient-lane records must carry
   `minimizationReviewed: true` (`NFR-COMP-011`, `CH-C01`).
7. **Specialty-metadata quality and controlled versioning** — capacity datasets
   pin `specialtyTaxonomyVersion` to the governed taxonomy version and keep each
   record's `specialty` consistent with its `specialtyTags`, with no duplicate
   tags (`NFR-DQ-005`).
8. **Cross-tenant identity boundary** — provider-scoped datasets pin the dataset
   and every record to the declared tenant; the shared lane must not declare a
   dataset-level tenant id. No foreign-tenant record may leak into a
   tenant-scoped dataset (`NFR-SEC-005`, `CH-C02`).

### Phase 3 provider SIT evidence and reliability enforcement

This check is layered on top of the Phase 1 and Phase 2 gates (advancing register
item `RV-06-05`, alongside provider SIT evidence for `RV-06-08`/`RV-06-09`):

9. **Degraded-mode and recovery contract** — provider-scoped onboarding datasets
   must declare a `degradedMode` block with a fallback read model, a positive and
   bounded (`<= 60` minute) data-staleness ceiling, an explicit manual-override
   capability, and a recovery-runbook reference (`NFR-REL-005`, `CH-C03`).

## Relationship to IaC

These datasets are the SIT fixtures for the data-platform bootstrap path
provisioned by [`infra/modules/data-platform/main.bicep`](../../infra/modules/data-platform/main.bicep),
which exposes a dedicated `onboarding` blob container for synthesized onboarding
data used by the OOA/DCA/BMCA MVP flows. See
[`docs/agents/sprint-06-mvp-agent-readiness.md`](../../docs/agents/sprint-06-mvp-agent-readiness.md)
for the agent-to-IaC component mapping.
