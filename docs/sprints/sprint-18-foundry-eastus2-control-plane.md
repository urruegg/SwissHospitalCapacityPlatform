# Sprint 18 — Foundry Control Plane + Agent Registration in eastus2

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | @urruegg |
| **Status** | Ready for execution |
| **Previous Version** | n/a (new sprint) |

> **Sprint theme.** Establish the Microsoft Foundry control plane in eastus2 — the only MCAP tenant region with OpenAI quota AND Foundry Agent Service support — deploy production-grade models, register all 8 platform agents, and verify end-to-end agent invocation.

---

## 1. Sprint goal

Unblock agent registration by deploying the Foundry control plane in eastus2, register all 8 platform agents with correct model assignments, and prove end-to-end agent invocation works from the existing westus2 agent-host.

**Success shape:**

- AI Services account in eastus2 with Foundry project provisioned and accessible.
- 3 models deployed (gpt-5, gpt-5-mini, o3) all GA GlobalStandard.
- 8 agents registered and responding to prompts via Foundry data-plane API.
- End-to-end test: agent-host → Foundry API → agent → tool call → response.
- ADR-0028 documenting the region decision.

---

## 2. Source baseline

1. [SIT Evidence Analysis (2026-07-17)](sit-evidence-2026-07-17.md) — resource inventory + region analysis
2. [Sprints 11–16 Roadmap Design](../superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md)
3. [Sprint 18 Design Spec](../superpowers/specs/2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md)
4. [Sprint 18 Implementation Plan](../superpowers/plans/2026-07-17-sprint-18-foundry-eastus2-control-plane-plan.md)
5. [ADR-0013: Temporary US Region Demo Scope](../adr/0013-temporary-us-region-demo-scope.md)
6. [AGENTS.md §1 Registry](../../AGENTS.md)

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| T1 | ADR-0028 | `docs/adr/0028-foundry-control-plane-eastus2.md` | Merged |
| T2 | AI Services account | `ai-ihzhhpf-sit-eastus2` in eastus2 | Provisioned |
| T3 | Foundry project | `ai-ihzhhpf-sit-eastus2-project` | Created + managed identity |
| T4 | Deploy gpt-5 | GlobalStandard 50K TPM | Succeeded |
| T5 | Deploy gpt-5-mini | GlobalStandard 100K TPM | Succeeded |
| T6 | Deploy o3 | GlobalStandard 30K TPM | Succeeded |
| T7 | Register 8 agents | All in Foundry project | Verified via API |
| T8 | RBAC | Agent-host identity → Cognitive Services User | Assigned |
| T9 | E2E tests | Health + smoke + tool + refusal | 8/8 pass |
| T10 | Evidence doc update | Foundry section in SIT evidence | Committed |
| T11 | AGENTS.md update | eastus2 endpoint refs | Merged |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | eastus2 for Foundry (not switzerlandnorth) | MCAP tenant has zero OpenAI quota in westus2; eastus2 has 88 GA models + 5.8M TPM + Agent Service GA. Demo scope per ADR-0013. |
| D2 | Cross-region topology (westus2 app ↔ eastus2 Foundry) | Temporary until Sprint 19 collocates everything. Acceptable for demo scope. |
| D3 | gpt-5 + gpt-5-mini + o3 model trio | Covers all agent tiers: complex reasoning (gpt-5), cost-efficient (mini), multi-step planning (o3). |

---

## 5. Definition of Done

- [ ] ADR-0028 merged
- [ ] AI Services + Foundry project provisioned in eastus2
- [ ] 3 models deployed (Succeeded state)
- [ ] 8 agents registered (verified via GET /assistants)
- [ ] RBAC assigned for agent-host identity
- [ ] E2E tests: 8/8 health + smoke pass; ≥4/8 tool invocation; 8/8 refusal
- [ ] Evidence document updated
- [ ] AGENTS.md updated
- [ ] All CI checks pass

---

## 6. References

- Design: [`2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md`](../superpowers/specs/2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md)
- Plan: [`2026-07-17-sprint-18-foundry-eastus2-control-plane-plan.md`](../superpowers/plans/2026-07-17-sprint-18-foundry-eastus2-control-plane-plan.md)
- Issue: See linked GitHub issue
