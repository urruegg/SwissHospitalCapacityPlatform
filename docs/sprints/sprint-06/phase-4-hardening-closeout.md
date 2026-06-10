# Sprint 06 Phase 4 — Hardening and Sprint Closure Package

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Record the Phase 4 outcome and the **Sprint 6 closeout recommendation** for the
onboarding-control and specialty-capacity workstream. This fills the Sprint 6
closeout artifact gap for Phase 4 (#48) and consolidates the hardening checks,
deterministic classification coverage, residual risks, and next-step decision.

## What was implemented

1. Added an explicit Phase 4 closeout record and evidence artifact so Sprint 6
   closure is backed by committed material rather than an empty merged PR.
2. Reconciled the Sprint 6 gate-sequencing model so later phases may collect SIT
   evidence while upstream PROD approvals remain pending, while keeping PROD
   promotion blocked until prerequisite approvals and register blockers clear.
3. Reviewed deterministic-service vs agentic-flow coverage for Sprint 6
   onboarding paths across:
   - [`docs/SD.md`](../../SD.md)
   - [`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md)
   - [`docs/agents/sprint-06-mvp-agent-readiness.md`](../../agents/sprint-06-mvp-agent-readiness.md)
   - [`docs/agents/sprint-06-optional-agent-wave-readiness.md`](../../agents/sprint-06-optional-agent-wave-readiness.md)
4. Consolidated the onboarding control-path checks used in Sprint 6:
   - synthesized-data validator unit tests under
     [`data/synthetic/tests/test_validate_datasets.py`](../../data/synthetic/tests/test_validate_datasets.py)
   - end-to-end synthesized-data gate run via
     [`data/synthetic/validate_datasets.py`](../../data/synthetic/validate_datasets.py)
5. Captured a closeout recommendation: Sprint 6 is **SIT-complete** but remains
   **PROD-pending** until owner approvals and `RV-06-04` are cleared.

## Phase 4 closeout evidence

The committed closeout evidence artifact is
[`evidence/2026-06-09-phase-4-hardening-closeout.json`](evidence/2026-06-09-phase-4-hardening-closeout.json).

The artifact consolidates:

1. Deterministic-classification coverage for `FR-ONB-004`
2. Control-path checks executed for Sprint 6 onboarding artifacts
3. Residual risks and owners carried forward from Phases 1 to 3
4. The closeout recommendation for Sprint 6

## Sprint 06 Phase Evidence

### Phase Context

- Phase issue: #48 (see docs/sprints/sprint-06/phase-issue-map.md)
- Phase: 4
- Onboarding lane(s): both (patient-minimum and specialty-capacity)
- Provider scope: both (hirslanden and zollikerberg)

### FR Controls Impacted

- `FR-ONB-004`: Deterministic-service vs agentic-flow classification documented and consolidated for Sprint 6 closure — full

### NFR Controls Impacted

- `NFR-MAINT-005`: Sprint evidence pack is complete and reviewable — full
- `NFR-COMP-011`: Outstanding PROD blocker remains explicitly carried as a closeout risk — full

### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C03` | End-to-end traceability and explicit closure evidence for Sprint 6 | OPS | [`evidence/2026-06-09-phase-4-hardening-closeout.json`](evidence/2026-06-09-phase-4-hardening-closeout.json) |
| `CH-C10` | Deterministic vs agentic classification consolidated and scope lock preserved | ARCH | [`evidence/2026-06-09-phase-4-hardening-closeout.json`](evidence/2026-06-09-phase-4-hardening-closeout.json) |

### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-06-02 | consolidated for closeout review | in-validation |
| RV-06-04 | carried forward as explicit PROD blocker | in-validation |

### Commands / Checks Executed

- [x] `npx --yes markdownlint-cli2 "docs/sprints/sprint-06/**/*.md" "docs/agents/sprint-06-*.md" "#node_modules"` — outcome: pass
- [x] `python -m unittest discover -s data/synthetic/tests -v` — outcome: pass
- [x] `python data/synthetic/validate_datasets.py` — outcome: pass

### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | pass | `.github/workflows/data-contracts.yml` + markdown lint |
| SIT gate | yes | pass | [`evidence/2026-06-09-phase-4-hardening-closeout.json`](evidence/2026-06-09-phase-4-hardening-closeout.json) |
| PROD gate | yes | pending | Requires upstream owner approvals and closure of `RV-06-04` |
| Runtime gate | no | n/a | |

### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Formal re-identification risk acceptance (`RV-06-04`) still requires legal/security sign-off before any PROD promotion | high | SEC | Keep Sprint 6 at SIT-complete / PROD-pending until approval is recorded | 2026-09-07 | open |
| Phase 1 to Phase 3 owner approvals are still required to flip PROD gates to pass | medium | ARCH | Collect ARCH / SEC / OPS / LEGAL approvals against existing phase evidence | 2026-09-07 | open |
| Optional agent wave (DFA/IWA/DQSA/CSA/EAA) remains deferred until MVP Phase 1 promotion blockers are cleared | low | ARCH | Preserve scope lock to OOA/DCA/BMCA and re-open optional-wave activation only after blockers close | 2026-09-07 | accepted |

### Closeout Recommendation

Sprint 6 is **ready to close at the SIT evidence level**. The sprint now has a
complete governance and evidence pack across Phases 0 to 4, and the missing
closeout artifact gap is resolved. However, Sprint 6 should remain
**PROD-pending** until:

1. Phase 1 and Phase 2 owner approvals are recorded
2. `RV-06-04` is accepted by legal/security
3. The remaining PROD gate statuses are updated to reflect those approvals

### Definition of Done Confirmation

- [x] Phase 4 closeout artifact committed and indexed
- [x] Deterministic-classification coverage consolidated for Sprint 6
- [x] Onboarding control-path checks linked and re-run for closeout
- [x] Residual risks and owners consolidated into one closeout package
- [x] Sprint 6 closure recommendation recorded with explicit PROD blockers

## Change Control

Any change to this closeout package or its recommendation bumps this document's
version per `.github/copilot-instructions.md` §9 and must stay consistent with
the Sprint 6 phase plan.

