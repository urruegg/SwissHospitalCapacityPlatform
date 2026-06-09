# Sprint 6 Optional Agent Wave Readiness (DFA / IWA / DQSA / CSA / EAA)

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.0.0 (initial optional-wave gate decision) |

## Purpose

Stage the **deferred optional agent wave** for Sprint 6 — Demand Forecasting
Agent (DFA), Integration Workflow Agent (IWA), Data Quality and Semantics Agent
(DQSA), Compliance and Safety Agent (CSA), and Explainability and Audit Agent
(EAA) — and record the **explicit gate decision** on whether to onboard them in
Phase 3. This is the optional-wave deliverable for Phase 3 (#47) of
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../../sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
"Optional agents (deferred to Phase 3)", and is non-blocking for the MVP Phase 1
scope locked to OOA/DCA/BMCA in
[`sprint-06-mvp-agent-readiness.md`](sprint-06-mvp-agent-readiness.md).

## Scope

The optional agents remain **deferred backlog** and are realized as Markdown
governance artifacts only, consistent with ADR-0002 (agents and controls are
realized as Markdown). This note introduces no optional-agent implementation
work; it records readiness signals and the gate decision that authorizes — or
defers — onboarding.

## Optional Agent Backlog

| Agent | Primary responsibility | Classification (FR-ONB-004) | Onboarding contracts consumed |
| ----- | ----- | ----- | ----- |
| DFA | Demand forecasting for bed/specialty capacity | Agentic (advisory, HITL-gated) | `DC-ONB-CAPACITY-v1` (+ provider extensions) |
| IWA | Integration workflow orchestration across onboarding sources | Service-leaning (deterministic integration, agentic adapters) | `DC-ONB-CAPACITY-v1`, provider extensions |
| DQSA | Data quality and semantic consistency checks on onboarding metadata | Service (deterministic checks) | all onboarding contracts |
| CSA | Compliance and safety guardrail enforcement | Agentic (advisory, HITL-gated) | `DC-ONB-PATIENT-v1`, `DC-ONB-CAPACITY-v1` |
| EAA | Explainability and audit-trail generation | Service (deterministic audit) | all onboarding contracts |

All advisory agents are **advisory-only and human-in-the-loop**; no autonomous
closed-loop clinical actuation (`NFR-AI-001`).

## Gate Inputs

The optional-wave decision reads the Sprint 6 phase gate states defined in
[`../../sprints/sprint-06/gate-sequence.md`](../../sprints/sprint-06/gate-sequence.md)
and the register in
[`../../sprints/sprint-06/requires-validation-register.md`](../../sprints/sprint-06/requires-validation-register.md).

| Gate input | State | Evidence |
| ----- | ----- | ----- |
| Phase 1 SIT gate | pass | [`../../sprints/sprint-06/evidence/2026-06-09-phase-1-sit-synthesized-data.json`](../../sprints/sprint-06/evidence/2026-06-09-phase-1-sit-synthesized-data.json) |
| Phase 2 SIT gate | pass | [`../../sprints/sprint-06/evidence/2026-06-09-phase-2-sit-onboarding-policy.json`](../../sprints/sprint-06/evidence/2026-06-09-phase-2-sit-onboarding-policy.json) |
| Phase 3 SIT gate (provider + degraded-mode) | pass | [`../../sprints/sprint-06/evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](../../sprints/sprint-06/evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json) |
| Phase 1 PROD gate | pending | Owner approvals + version-header confirmation outstanding |
| Phase 2 PROD gate | pending | Legal/compliance re-identification acceptance (`RV-06-04`) outstanding |
| High-severity register blockers | open | `RV-06-04` (re-identification acceptance) remains a PROD blocker |

## Gate Decision

**Decision: DEFER the optional agent wave (DFA / IWA / DQSA / CSA / EAA).**

The Phase 1, Phase 2, and Phase 3 **SIT** gates are green, so the optional wave
is **staged and ready** at the SIT level. However, onboarding the optional wave
would expand scope beyond the Sprint 6 MVP lock and would still be blocked from
any PROD promotion while upstream approvals and register blockers remain open.
Two conditions are not yet met:

1. Phase 1 and Phase 2 **PROD** gates remain `pending` (owner approvals not
   collected).
2. High-severity register item `RV-06-04` (formal re-identification risk
   acceptance) remains `open`, which is a PROD promotion blocker for any change
   in scope.

Because the optional wave is explicitly **non-blocking** for the sprint and the
PROD gates are not green, the wave is **deferred** rather than onboarded in this
phase. This keeps MVP Phase 1 scope locked to OOA/DCA/BMCA and avoids
introducing optional-agent implementation work before its activation criteria
are met.

## Activation Criteria (when DEFER may flip to ONBOARD)

The optional wave may be onboarded in a subsequent increment only when **all**
of the following hold:

1. Phase 1 and Phase 2 PROD gates read `pass` with recorded owner approvals.
2. `RV-06-04` re-identification risk acceptance is `validated` with legal/security
   sign-off.
3. The Phase 3 provider SIT evidence
   ([`../../sprints/sprint-06/evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json`](../../sprints/sprint-06/evidence/2026-06-09-phase-3-sit-provider-degraded-mode.json))
   remains `pass` with zero critical failures.
4. Each onboarded agent ships its own readiness baseline (scope, contracts,
   HITL gates) mirroring [`sprint-06-mvp-agent-readiness.md`](sprint-06-mvp-agent-readiness.md).

## Change Control

Any change to the optional-agent backlog or the gate decision bumps this
document's version per `.github/copilot-instructions.md` §9 and must stay
consistent with the Sprint 6 phase plan and gate sequence.
