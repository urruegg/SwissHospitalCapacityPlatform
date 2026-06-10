# CAF/WAF Alignment and Delta Closure Matrix

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | N/A |

## Purpose

Track the closure of the Azure CAF and Well-Architected Framework (WAF) deltas raised in
the CAF/WAF review against concrete Sprint 5 baseline artifacts. This matrix gives a
single, auditable view of which review findings are closed, advanced, or deferred, and to
which target phase. It supports Phase 1 task 1 of
[`docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`\](../sprints/sprint-05-caf-waf-mvp-sit-prod.md)
and the consolidated enforcement model in
[`docs/adr/0007-0011-hardening-delta-summary.md`](../adr/0007-0011-hardening-delta-summary.md).

Primary source:
[`docs/reviews/2026-06-09-ama-caf-waf-review session.md`](<../reviews/2026-06-09-ama-caf-waf-review session.md>).

## Status Legend

| Status | Meaning |
| ----- | ----- |
| `closed` | Delta addressed by a committed artifact in this sprint baseline. |
| `advanced` | Documentation baseline created; implementation evidence due in a later phase. |
| `deferred` | Explicitly deferred with owner and due phase per the register. |

## CAF Landing-Zone and Operating-Model Deltas

| CAF area | Review finding | Closure artifact | Target phase | Status |
| ----- | ----- | ----- | ----- | ----- |
| Landing-zone governance | MG hierarchy, policy assignment, RBAC scopes weaker than intent (Â§4.1, Â§7) | `RV-06` register item; landing-zone governance evidence doc | Phase 2 | `deferred` |
| Platform operating model | Strong Git-first ALM with approval gates (Â§4.1) | [`docs/ALM_PLAN.md`](../ALM_PLAN.md), [`docs/sprints/sprint-05/gate-sequence.md`\](../sprints/sprint-05/gate-sequence.md) | Phase 1 | `closed` |
| Security baseline at platform layer | Execution evidence partial for several controls (Â§4.1) | Policy-as-code gates (ADR-0010) | Phase 2 | `advanced` |
| Standardization and reusable patterns | Runtime reference pattern needs scope guard (Â§4.1) | [`runtime-pattern-decision-matrix.md`](runtime-pattern-decision-matrix.md) (ADR-0008) | Phase 1 | `closed` |

## WAF Pillar Deltas

| WAF pillar | Review finding | Closure artifact | Target phase | Status |
| ----- | ----- | ----- | ----- | ----- |
| Reliability | DR/failover and PHI runbook gating open (Â§4.2) | [`docs/operations/reliability-dr-profile.md`](../operations/reliability-dr-profile.md) (ADR-0009) | Phase 1 doc / Phase 3 evidence | `advanced` |
| Security | Some operational controls still open (Â§4.2) | Policy-as-code + DSR/incident runbooks (ADR-0010) | Phase 2 | `advanced` |
| Cost Optimization | No full cost control evidence loop (Â§4.2) | `RV-09` FinOps thresholds | Phase 3 | `deferred` |
| Operational Excellence | Incident/DSR/privacy operations partially open (Â§4.2) | DSR + incident runbooks (`RV-04`) | Phase 2 | `advanced` |
| Performance Efficiency | Sizing provisional, pending SIT validation (Â§4.2) | [`docs/AI.md`](../AI.md) sizing + SIT load validation | Phase 3 | `deferred` |

## Zero Trust Deltas

| Finding | Closure artifact | Target phase | Status |
| ----- | ----- | ----- | ----- |
| Full policy-enforcement telemetry proving control effectiveness in PROD (Â§4.3) | `RV-10` consolidated control-effectiveness report | Phase 4 | `deferred` |

## High-Priority Recommendation Closure (Review Â§9)

| Recommendation | Priority | Closure artifact | Target phase | Status |
| ----- | ----- | ----- | ----- | ----- |
| Canton-specific legal applicability annex (Â§9 High 1) | High | [`docs/compliance/cantonal-annex.md`](../compliance/cantonal-annex.md) (ADR-0011) | Phase 1 doc / Phase 2 evidence | `advanced` |
| Reliability target state RTO/RPO + DR runbooks (Â§9 High 2) | High | [`docs/operations/reliability-dr-profile.md`](../operations/reliability-dr-profile.md) (ADR-0009) | Phase 1 doc / Phase 3 evidence | `advanced` |
| Policy-as-code enforcement in CI (Â§9 High 3) | High | ADR-0010; `RV-03` | Phase 2 | `advanced` |
| Landing-zone governance evidence (Â§9 Medium 1) | Medium | `RV-06` | Phase 2 | `deferred` |
| ADR clarifying Foundry vs self-hosted scope (Â§9 Medium 2) | Medium | [`runtime-pattern-decision-matrix.md`](runtime-pattern-decision-matrix.md); ADR-0008 | Phase 1 | `closed` |
| Operations evidence automation for CH-C03/C05/C10 (Â§9 Medium 3) | Medium | ADR-0010; `RV-03`, `RV-10` | Phase 2 / Phase 4 | `advanced` |

## Quick-Win Closure (Review Â§9 Quick wins)

| Quick win | Closure artifact | Status |
| ----- | ----- | ----- |
| Explicit "requires validation" register | [`docs/sprints/sprint-05/requires-validation-register.md`\](../sprints/sprint-05/requires-validation-register.md) | `closed` |
| Control-owner column for open CH controls | This matrix + register Owner column; [`docs/COMPLIANCE.md`](../COMPLIANCE.md) | `closed` |
| DR test evidence placeholder in release checklist | [`docs/operations/reliability-dr-profile.md`](../operations/reliability-dr-profile.md) rehearsal schema; release checklist DR row | `closed` |

## Summary

| Status | Count |
| ----- | ----- |
| `closed` | 6 |
| `advanced` | 7 |
| `deferred` | 4 |

All high-priority findings are `closed` or `advanced` (with a documentation baseline and a
named target phase); no high-priority finding remains untracked. Deferred items each carry
an owner and due phase in
[`docs/sprints/sprint-05/requires-validation-register.md`\](../sprints/sprint-05/requires-validation-register.md),
satisfying the Phase 1 Definition of Done.

## Change Control

Any change to closure status or artifact links bumps this document's version per
`.github/copilot-instructions.md` Â§9 and must stay consistent with the requires-validation
register and the hardening delta summary.

