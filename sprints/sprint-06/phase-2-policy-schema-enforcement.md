# Sprint 06 Phase 2 — Onboarding Policy and Schema Enforcement Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 2 implementation outcome and the **SIT gate evidence** for
onboarding policy and schema enforcement: minimum-sensitive-data onboarding
controls, specialty-metadata schema validation and controlled versioning, and
cross-tenant identity boundary checks tied to the synthesized SIT datasets. This
is the Phase 2 (#46) deliverable for
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
and advances register items `RV-06-03`, `RV-06-04`, and `RV-06-07` in
[`requires-validation-register.md`](requires-validation-register.md).

## What was implemented

1. Phase 2 onboarding-policy enforcement added to the synthesized-data gate
   [`data/synthetic/validate_datasets.py`](../../data/synthetic/validate_datasets.py),
   layered on top of the Phase 1 schema and minimization checks:
   - **Minimum-data purpose-tag policy** (`check_purpose_tags`) — every record
     `purposeTag` must be in the dataset-level `purposeTags` allowlist, and
     patient-lane records must carry `minimizationReviewed: true`
     (`NFR-COMP-011`, `CH-C01`; `RV-06-04`).
   - **Specialty-metadata quality and controlled versioning**
     (`check_specialty_metadata`) — capacity datasets pin
     `specialtyTaxonomyVersion` to the governed taxonomy version and keep each
     record's `specialty` consistent with its `specialtyTags`, with no duplicate
     tags (`NFR-DQ-005`; `RV-06-07`).
   - **Cross-tenant identity boundary** (`check_tenant_boundary`) —
     provider-scoped datasets pin the dataset and every record to the declared
     tenant; the shared lane must not declare a dataset-level tenant id, and no
     foreign-tenant record may leak into a tenant-scoped dataset
     (`NFR-SEC-005`, `CH-C02`; `RV-06-03`).
2. Traceability map updated to surface the Phase 2 controls
   ([`data/synthetic/traceability.json`](../../data/synthetic/traceability.json),
   version 1.1.0): `NFR-SEC-005`, `CH-C02`, and `RV-06-03`/`RV-06-04`/`RV-06-07`
   are now declared per dataset.
3. Unit tests for the three new checks plus a Phase 2 traceability-coverage
   assertion
   ([`data/synthetic/tests/test_validate_datasets.py`](../../data/synthetic/tests/test_validate_datasets.py)).
4. README controls list extended with the Phase 2 enforcement section
   ([`data/synthetic/README.md`](../../data/synthetic/README.md), version 1.1.0)
   and the CI gate comment updated for Phase 2 policy checks
   ([`.github/workflows/data-contracts.yml`](../../.github/workflows/data-contracts.yml)).

## SIT gate evidence

The committed evidence artifact for the Phase 2 SIT gate run is
[`evidence/2026-06-09-phase-2-sit-onboarding-policy.json`](evidence/2026-06-09-phase-2-sit-onboarding-policy.json),
produced by:

```bash
python3 data/synthetic/validate_datasets.py \
  --output sprints/sprint-06/evidence/2026-06-09-phase-2-sit-onboarding-policy.json
```

Result summary: `pass` — 26 of 26 checks passed, 0 critical failures, across the
four synthesized onboarding datasets. Control coverage now includes the Phase 2
controls `NFR-COMP-011`, `NFR-DQ-005`, `NFR-SEC-005`, `CH-C01`, `CH-C02`, and
register items `RV-06-03`, `RV-06-04`, `RV-06-07`. The same gate runs in CI in
[`.github/workflows/data-contracts.yml`](../../.github/workflows/data-contracts.yml)
and uploads the artifact under the `synthesized-data-evidence` name.

## Sprint 06 Phase Evidence

### Phase Context

- Phase issue: #46 (see sprints/sprint-06/phase-issue-map.md)
- Phase: 2
- Onboarding lane(s): both (patient-minimum and specialty-capacity)
- Provider scope: both (hirslanden and zollikerberg)

### FR Controls Impacted

- `FR-ONB-001`: Patient onboarding via minimum required metadata only — full
- `FR-ONB-002`: Hospital-capacity onboarding via specialty-tagged metadata — full
- `FR-ONB-003`: Provider-specific specialty profiles for capacity — full

### NFR Controls Impacted

- `NFR-COMP-011`: Minimum-data purpose-tag and minimization policy enforced as a
  SIT gate criterion — full
- `NFR-SEC-005`: Cross-tenant identity boundary enforced for onboarding datasets —
  full
- `NFR-DQ-005`: Specialty-metadata quality and controlled taxonomy versioning
  enforced — full

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C01` | Minimization, purpose tags, re-identification control on onboarding | SEC | [`evidence/2026-06-09-phase-2-sit-onboarding-policy.json`](evidence/2026-06-09-phase-2-sit-onboarding-policy.json) |
| `CH-C02` | Explicit, auditable cross-tenant identity boundary on onboarding datasets | SEC | [`evidence/2026-06-09-phase-2-sit-onboarding-policy.json`](evidence/2026-06-09-phase-2-sit-onboarding-policy.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-06-03 | advanced | in-validation |
| RV-06-04 | advanced | in-validation |
| RV-06-07 | advanced | in-validation |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: pass
- [x] `python3 -m unittest discover -s data/synthetic/tests -v` — outcome: pass
- [x] `python3 data/synthetic/validate_datasets.py` — outcome: pass
- [x] onboarding policy / schema gate (Phase 2+) — outcome: pass
- [ ] provider SIT dataset validation evidence (Phase 3) — outcome: n/a

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/data-contracts.yml` |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-2-sit-onboarding-policy.json`](evidence/2026-06-09-phase-2-sit-onboarding-policy.json) |
| PROD gate | yes | pending | Requires legal/compliance re-identification (`RV-06-04`) sign-off and version-header confirmation |
| Runtime gate | no | n/a | |

### Approvals (PROD promotion only)

> PROD promotion is **pending**: approvals below are required before the PROD
> gate may read `pass`.

| Role | Approver handle | Timestamp | Decision |
| ----- | ----- | ----- | ----- |
| ARCH | TBD | | pending |
| SEC | TBD | | pending |
| OPS | TBD | | pending |
| LEGAL (re-identification / cantonal) | TBD | | pending |

### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Formal re-identification risk acceptance (`RV-06-04`) still requires legal/security sign-off before PROD | high | SEC | Minimization + purpose-tag policy now enforced as a SIT gate criterion; formal acceptance remains a PROD gate item | 2026-09-07 | open |
| Tenant-boundary control validated against synthesized datasets only; provider SIT evidence (`RV-06-08`/`RV-06-09`) is captured in Phase 3 | medium | OPS | Cross-tenant check enforced now; provider SIT evidence scheduled in Phase 3 (#47) | 2026-09-07 | accepted |

### Definition of Done Confirmation

- [x] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [x] No unresolved high-severity register item for this phase left undocumented
- [x] MVP Phase 1 scope kept locked to OOA/DCA/BMCA (optional agents deferred to Phase 3)
- [x] Every edited doc has its Version header bumped (copilot-instructions §9)

## Change Control

Any change to this evidence record or the onboarding-policy gate behaviour bumps
this document's version per `.github/copilot-instructions.md` §9 and must stay
consistent with the Sprint 6 phase plan.
