# Sprint 06 Phase 1 — IaC Data Platform Kickoff and MVP Agents Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 1 implementation outcome and the **SIT gate evidence** for the
IaC-first data-platform kickoff, synthesized SIT onboarding datasets, and MVP
agent readiness (OOA/DCA/BMCA). This is the Phase 1 (#45) deliverable for
[`docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
and advances register items `RV-06-01`, `RV-06-02`, `RV-06-06`, and `RV-06-10`
in [`requires-validation-register.md`](requires-validation-register.md).

## What was implemented

1. Synthesized, non-production SIT onboarding datasets and JSON Schema contracts
   under [`data/synthetic/`](../../data/synthetic/README.md):
   - `DC-ONB-PATIENT-v1` (patient minimum-data lane),
   - `DC-ONB-CAPACITY-v1` (specialty-capacity lane),
   - `DC-ONB-CAPACITY-HIRSLANDEN-v1` and `DC-ONB-CAPACITY-ZOLLIKERBERG-v1`
     (provider extensions, Hospital-at-Home optional and provider-scoped).
2. A dependency-free contract/schema validator
   (`data/synthetic/validate_datasets.py`) enforcing schema conformance,
   re-identification minimization, the capacity invariant, specialty taxonomy
   versioning, and FR/NFR/CH traceability coverage, plus unit tests.
3. A CI gate (`.github/workflows/data-contracts.yml`) running the validator and
   uploading the synthesized-data evidence artifact.
4. IaC data-platform bootstrap wiring: a dedicated `onboarding` blob container in
   [`infra/modules/data-platform/main.bicep`](../../infra/modules/data-platform/main.bicep)
   with an `onboardingContainerName` output, regenerated into `infra/main.json`.
5. Baseline document deltas: `docs/PRD.md` (1.3.0), `docs/SD.md` (1.3.0),
   `docs/ARCHITECTURE.md` (0.12.0), `docs/DATA.md` (0.4.0),
   `docs/COMPLIANCE.md` (0.5.0).
6. MVP agent readiness baseline for OOA/DCA/BMCA with explicit IaC component
   mapping: [`docs/agents/sprint-06-mvp-agent-readiness.md`](../../agents/sprint-06-mvp-agent-readiness.md).

## SIT gate evidence

The committed evidence artifact for the Phase 1 SIT gate run is
[`evidence/2026-06-09-phase-1-sit-synthesized-data.json`](evidence/2026-06-09-phase-1-sit-synthesized-data.json),
produced by:

```bash
python3 data/synthetic/validate_datasets.py \
  --output docs/sprints/sprint-06/evidence/2026-06-09-phase-1-sit-synthesized-data.json
```

Result summary: `pass` — 15 of 15 checks passed, 0 critical failures, across the
four synthesized onboarding datasets. The same gate runs in CI in
`.github/workflows/data-contracts.yml` and uploads the artifact under the
`synthesized-data-evidence` name.

## Sprint 06 Phase Evidence

### Phase Context

- Phase issue: #45 (see docs/sprints/sprint-06/phase-issue-map.md)
- Phase: 1
- Onboarding lane(s): both (patient-minimum and specialty-capacity)
- Provider scope: both (hirslanden and zollikerberg)

### FR Controls Impacted

- `FR-ONB-001`: Patient onboarding via minimum required metadata only — full
- `FR-ONB-002`: Hospital-capacity onboarding via specialty-tagged metadata — full
- `FR-ONB-003`: Provider-specific specialty profiles for capacity — full
- `FR-ONB-004`: Deterministic-service vs agentic-flow classification documented — full

### NFR Controls Impacted

- `NFR-COMP-011`: Minimum-sensitive-data controls and purpose tags enforced — full
- `NFR-DQ-005`: Specialty metadata quality checks and controlled versioning — full
- `NFR-MAINT-005`: IaC-first deployable bootstrap with reproducible validation — full
- `NFR-REL-005`: Onboarding degraded-mode behavior documented — partial (Phase 3 SIT proof)

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C01` | Minimization, purpose tags, re-identification control on onboarding | SEC | [`evidence/2026-06-09-phase-1-sit-synthesized-data.json`](evidence/2026-06-09-phase-1-sit-synthesized-data.json) |
| `CH-C05` | Swiss residency tag on onboarding datasets | LEGAL | [`data/synthetic/traceability.json`](../../data/synthetic/traceability.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-06-01 | advanced | in-validation |
| RV-06-02 | advanced | in-validation |
| RV-06-06 | advanced | in-validation |
| RV-06-10 | advanced | in-validation |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: pass
- [x] `python3 -m unittest discover -s data/synthetic/tests -v` — outcome: pass
- [x] `python3 data/synthetic/validate_datasets.py` — outcome: pass
- [x] `bicep build infra/main.bicep` — outcome: pass
- [ ] onboarding policy / schema gate (Phase 2+) — outcome: n/a
- [ ] provider SIT dataset validation evidence (Phase 3) — outcome: n/a

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/data-contracts.yml` |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-1-sit-synthesized-data.json`](evidence/2026-06-09-phase-1-sit-synthesized-data.json) |
| PROD gate | yes | pending | Requires owner approvals and version-header confirmation |
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
| Datasets are synthesized; provider SIT evidence (`RV-06-08`/`RV-06-09`) is captured in Phase 3 | medium | OPS | Provider extension schemas validated now; SIT provider evidence scheduled in Phase 3 (#47) | 2026-09-07 | accepted |
| Formal re-identification risk acceptance (`RV-06-04`) pending legal/security sign-off | high | SEC | Enforced minimization baseline in validator; formal acceptance is a Phase 2 gate item | 2026-09-07 | open |

### Definition of Done Confirmation

- [x] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [x] No unresolved high-severity register item for this phase left undocumented
- [x] MVP Phase 1 scope kept locked to OOA/DCA/BMCA (optional agents deferred to Phase 3)
- [x] Every edited doc has its Version header bumped (copilot-instructions §9)

## Change Control

Any change to this evidence record or the synthesized-data gate behaviour bumps
this document's version per `.github/copilot-instructions.md` §9 and must stay
consistent with the Sprint 6 phase plan.
