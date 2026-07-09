# ADR-0020 — Sprint 11 agent model selection

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

## Context

Sprint 11 introduces seven (or eight with the onboarding stretch)
**application-hosted** agents (per
[ADR-0008](0008-agent-runtime-pattern-scope-and-selection.md)) that the Sprint 13
Container Apps agent-host will load at runtime and dispatch against a Microsoft
Foundry chat model. This ADR selects the **model deployment** — not the runtime —
and must honour the regulated-inference constraints already recorded in:

- [ADR-0003](0003-swiss-regional-inference-for-phi.md) — Swiss-regional inference for PHI.
- [ADR-0004](0004-block-global-and-data-zone-for-phi.md) — block global / data-zone deployments for PHI.
- [ADR-0006](0006-preview-features-non-production-rule.md) — preview features are non-production.
- [ADR-0013](0013-temporary-us-region-demo-scope.md) — temporary `westus2` demo scope (synthetic only).
- [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) — no PHI in the MVP demo scope.

The runtime posture (application-hosted vs Foundry Agent Service) is **out of
scope** for this ADR and remains governed by ADR-0008. Sprint 11 delivers
prompt manifests, tool contracts, golden tasks, and HITL declarations only — it
performs **no Foundry Agent Service deployment**.

## Decision

1. All Sprint 11 agents share a **single frontier chat-completion deployment**
   in the `westus2` demo Foundry project per ADR-0013 (demo scope only). The
   deployment name is referenced by each agent manifest as
   `modelDeploymentRef: sprint11-chat` — the concrete Azure deployment name is
   resolved at Sprint 13 agent-host configuration time and is **not** hard-coded
   in any prompt, manifest, or workflow.
2. This deployment is **synthetic-data-only**. Per ADR-0006 and ADR-0016 it is
   **non-production for regulated data** and must never process real PHI.
   Enforcement is layered: agent refusal rules (per-agent `AGENT.md`), the
   synthetic-only Sprint 10 Gold tables, and the `data-quality-agent` PHI gate.
3. Every Sprint 11 agent `AGENT.md` **references this ADR** in its Identity or
   Grounding section so that the model-selection decision is traceable from the
   agent to the constraint set above.
4. When the platform sunsets ADR-0013 and returns to Switzerland North, this ADR
   is **superseded** by a new ADR that pins Swiss-resident deployments per agent
   and lifts the synthetic-only restriction for regulated data.

## Consequences

- ✅ A single shared deployment reduces cost and operational complexity for the
  demo while keeping every agent traceable to one model decision.
- ✅ No model deployment happens in Sprint 11 — the manifest reference is inert
  until the Sprint 13 agent-host binds it, so no `approved-to-apply` gate fires
  in this sprint.
- ⚠ Agents must not accept real PHI in Sprint 11 — enforced by refusal rules and
  by the synthetic-only Gold layer.
- ⚠ Any new SKU or region for this deployment is a `deploy`-ceiling action and
  requires an `approved-to-apply` comment plus a superseding ADR per
  [AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete).
- 🔒 ADR-0006 is unchanged: this deployment remains non-production for regulated
  data for the lifetime of the ADR-0013 demo scope.
