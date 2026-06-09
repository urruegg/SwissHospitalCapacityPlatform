# Sprint 06 Phase 3 — Provider SIT Evidence and Optional Agent Wave

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 3 outcome and the **SIT gate evidence** for provider onboarding:
the Klinik Hirslanden and Spital Zollikerberg specialty-capacity onboarding
metadata contracts, the onboarding degraded-mode and recovery reliability
controls, and the explicit optional-agent-wave gate decision. This is the
Phase 3 (#47) deliverable for
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
and advances register items `RV-06-05`, `RV-06-08`, and `RV-06-09` in
[`requires-validation-register.md`](requires-validation-register.md).

## What was implemented

1. Provider degraded-mode / recovery reliability enforcement added to the
   synthesized-data gate
   [`data/synthetic/validate_datasets.py`](../../data/synthetic/validate_datasets.py)
   (`check_degraded_mode`), layered on top of the Phase 1 schema and Phase 2
   policy checks:
   - **Degraded-mode and recovery contract** — provider-scoped onboarding
     datasets must declare a `degradedMode` block with a fallback read model, a
     positive and bounded (`<= 60` minute) data-staleness ceiling, an explicit
     manual-override capability, and a recovery-runbook reference
     (`NFR-REL-005`, `CH-C03`; `RV-06-05`).
2. Provider onboarding metadata contracts extended with the `degradedMode`
   block in both the schemas and synthesized SIT datasets:
   - [`data/synthetic/schema/provider-hirslanden-capacity.schema.json`](../../data/synthetic/schema/provider-hirslanden-capacity.schema.json)
     and [`data/synthetic/datasets/provider-hirslanden-capacity.json`](../../data/synthetic/datasets/provider-hirslanden-capacity.json)
     (Hirslanden specialty-weighted capacity; `RV-06-08`).
   - [`data/synthetic/schema/provider-zollikerberg-capacity.schema.json`](../../data/synthetic/schema/provider-zollikerberg-capacity.schema.json)
     and [`data/synthetic/datasets/provider-zollikerberg-capacity.json`](../../data/synthetic/datasets/provider-zollikerberg-capacity.json)
     (Zollikerberg specialty / care-mode + optional Hospital-at-Home; `RV-06-09`).
3. Traceability map updated to surface the Phase 3 controls
   ([`data/synthetic/traceability.json`](../../data/synthetic/traceability.json),
   version 1.2.0): `NFR-REL-005`, `CH-C03`, and `RV-06-05` are now declared on
   both provider datasets.
4. Unit tests for the new degraded-mode check plus a Phase 3 traceability-coverage
   assertion
   ([`data/synthetic/tests/test_validate_datasets.py`](../../data/synthetic/tests/test_validate_datasets.py)).
5. README controls list extended with the Phase 3 enforcement section
   ([`data/synthetic/README.md`](../../data/synthetic/README.md), version 1.2.0)
   and the CI gate comment updated for the Phase 3 provider reliability check
   ([`.github/workflows/data-contracts.yml`](../../.github/workflows/data-contracts.yml)).
6. Optional-agent-wave readiness note with the explicit gate decision
   ([`docs/agents/sprint-06-optional-agent-wave-readiness.md`](../../docs/agents/sprint-06-optional-agent-wave-readiness.md)).

## SIT gate evidence

The committed evidence artifact for the Phase 3 SIT gate run is
[`evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json),
produced by:

```bash
python3 data/synthetic/validate_datasets.py \
  --output sprints/sprint-06/evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json
```

Result summary: `pass` — 28 of 28 checks passed, 0 critical failures, across the
four synthesized onboarding datasets (including the two provider datasets).
Control coverage now includes the Phase 3 controls `NFR-REL-005` and `CH-C03`,
and register items `RV-06-05`, `RV-06-08`, `RV-06-09`. The same gate runs in CI
in [`.github/workflows/data-contracts.yml`](../../.github/workflows/data-contracts.yml)
and uploads the artifact under the `synthesized-data-evidence` name.

## Optional agent wave decision

The optional agent wave (DFA / IWA / DQSA / CSA / EAA) is **deferred**, not
onboarded. The Phase 1, Phase 2, and Phase 3 SIT gates are green, but the
Phase 1 and Phase 2 PROD gates remain `pending` and the high-severity
re-identification acceptance (`RV-06-04`) remains `open` — both PROD promotion
blockers under [`gate-sequence.md`](gate-sequence.md). The full decision, gate
inputs, and activation criteria are recorded in
[`docs/agents/sprint-06-optional-agent-wave-readiness.md`](../../docs/agents/sprint-06-optional-agent-wave-readiness.md).
MVP Phase 1 scope stays locked to OOA/DCA/BMCA.

## Sprint 06 Phase Evidence

### Phase Context

- Phase issue: #47 (see sprints/sprint-06/phase-issue-map.md)
- Phase: 3
- Onboarding lane(s): specialty-capacity
- Provider scope: both (hirslanden and zollikerberg)

### FR Controls Impacted

- `FR-ONB-002`: Hospital-capacity onboarding via specialty-tagged metadata — full
- `FR-ONB-003`: Provider-specific specialty profiles for capacity — full

### NFR Controls Impacted

- `NFR-REL-005`: Onboarding services available under defined degraded-mode
  behavior, enforced as a provider SIT gate criterion — full
- `NFR-DQ-005`: Specialty-metadata quality and controlled taxonomy versioning for
  provider datasets — full

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C03` | Degraded-mode and recovery behavior for onboarding services | OPS | [`evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json) |
| `CH-C01` | Minimization and re-identification control on provider onboarding | SEC | [`evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-06-05 | advanced | in-validation |
| RV-06-08 | advanced | in-validation |
| RV-06-09 | advanced | in-validation |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: pass
- [x] `python3 -m unittest discover -s data/synthetic/tests -v` — outcome: pass
- [x] `python3 data/synthetic/validate_datasets.py` — outcome: pass
- [x] onboarding policy / schema gate (Phase 2+) — outcome: pass
- [x] provider SIT dataset validation evidence (Phase 3) — outcome: pass

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/data-contracts.yml` |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json) |
| PROD gate | yes | pending | Requires business acceptance of provider residual risk and upstream Phase 1/2 PROD approvals |
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
| Provider datasets are synthesized; production provider feeds may diverge from the SIT degraded-mode assumptions | medium | OPS | Degraded-mode contract enforced as a SIT gate criterion; production parity validated before PROD promotion | 2026-09-07 | accepted |
| Optional agent wave (DFA/IWA/DQSA/CSA/EAA) deferred pending Phase 1/2 PROD gates and `RV-06-04` acceptance | low | ARCH | Wave staged with explicit activation criteria in the optional-agent-wave readiness note; non-blocking for MVP scope | 2026-09-07 | accepted |
| Formal re-identification risk acceptance (`RV-06-04`) still requires legal/security sign-off before PROD | high | SEC | Minimization enforced at SIT; formal acceptance remains a PROD gate item | 2026-09-07 | open |

### Definition of Done Confirmation

- [x] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [x] No unresolved high-severity register item for this phase left undocumented
- [x] MVP Phase 1 scope kept locked to OOA/DCA/BMCA (optional agents deferred to Phase 3)
- [x] Every edited doc has its Version header bumped (copilot-instructions §9)

## Change Control

Any change to this evidence record or the provider degraded-mode gate behaviour
bumps this document's version per `.github/copilot-instructions.md` §9 and must
stay consistent with the Sprint 6 phase plan.
