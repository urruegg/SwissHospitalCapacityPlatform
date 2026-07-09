# Sprint 11 — Agents (Data + User-facing + Onboarding stretch) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.2.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüeegg |
| **Status** | Draft for review |
| **Previous Version** | 1.1.0 (rewrote all `agents-archive/<name>/` references to `agents/<name>/` after the 2.0.0 folder restructure) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/reviews/2026-06-09-ama-sd-review.md](../../reviews/2026-06-09-ama-sd-review.md) §2.4 Baseline Architecture; [docs/superpowers/ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md](../ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md) §4.1 |
| **Runtime posture** | Application-hosted agents dispatched from the Sprint 13 Container Apps agent-host to a Microsoft Foundry chat model, per [ADR-0008](../../adr/0008-agent-runtime-pattern-scope-and-selection.md) + [ADR-0007](../../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture and per-agent design](#3-architecture-and-per-agent-design)
4. [Agent and skill mix](#4-agent-and-skill-mix)
5. [GitHub delegation](#5-github-delegation)
6. [Side-effect posture and approval gates](#6-side-effect-posture-and-approval-gates)
7. [Verification strategy](#7-verification-strategy)
8. [Risks and mitigations](#8-risks-and-mitigations)
9. [Dependencies](#9-dependencies)
10. [Definition of done](#10-definition-of-done)

---

## 1. Goal and desired end state

Eight agents are addressable in the repo. Each has:

- an `agents/<name>/AGENT.md` prompt file with Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules;
- an `agents/<name>/golden-tasks.md` with at least one happy-path and one failure-mode fixture;
- a compatibility stub under `agents/<name>/`;
- a row in [AGENTS.md §1](../../../AGENTS.md#1-registry);
- for the six user-facing operational agents: a **prompt manifest + tool contract + HITL gate declaration** ready to be *loaded* by the Sprint 13 Container Apps agent-host and dispatched against a Foundry chat model.

Sprint 11 does **not** yet invoke agents from a real app UI — that is Sprint 13. Sprint 11 does **not** yet fill out the CSA body — that is Sprint 16.

### Runtime posture (per ADR-0008 + ADR-0007)

- **Control plane (agent orchestration, tool routing, HITL enforcement)** — application-hosted in **Azure Container Apps** (the agent-host built in Sprint 13). This is the ADR-0008 default; Foundry Agent Service is a permitted exception with a boundary contract, which Sprint 11 does not use.
- **Chat model** — **Microsoft Foundry** deployment (region + SKU pinned by the Sprint 11 model-selection ADR).
- **Cache (grounding + session state)** — **Azure Cache for Redis** (per ADR-0007 §1).
- **Persistence (conversation, audit, approval events)** — **Azure Cosmos DB** with the ADR-0007 §Implementation-Notes schema. This is separate from the Sprint 16 CSA scenario Cosmos.
- **HITL gates HITL-01..HITL-05** (per ADR-0007 §3) — mandatory before any side-effecting downstream action. Sprint 11 agents are all `write` ceiling (advisory), so they do not fire HITL gates themselves; they must declare which HITL gate governs the downstream action they recommend.

**What Sprint 11 delivers.** Prompt manifests + tool contracts + goldens + HITL declarations only — no Container Apps agent-host code (Sprint 13 builds that) and no Foundry Agent Service deployment (posture forbids it by default).

---

## 2. Scope

### 2.1 In-scope MVP

- **6 user-facing operational copilots** from the UX design §4.1: `bmca-agent` (bed management), `ooa-agent` (occupancy / 72-h forecast), `dca-agent` (discharge), `orsa-agent` (OR steering), `sba-agent` (staffing balance), `csa-agent` (scaffold only — Prepare/Run/Evaluate wired in Sprint 16).
- **1 data agent** — `data-quality-agent`: checks Bronze → Silver → Gold contracts, PHI/FK/schema gates. Leverages the `spark-operations` and `e2e-medallion-architecture` skills already installed in [`.github/skills/`](../../../.github/skills/).
- **Model selection ADR** — `docs/adr/00XX-sprint11-agent-model-selection.md` (number assigned at creation) decides which Foundry model per agent, grounded against [ADR-0003](../../adr/0003-swiss-regional-inference-for-phi.md), [ADR-0004](../../adr/0004-block-global-and-data-zone-for-phi.md), [ADR-0006](../../adr/0006-preview-features-non-production-rule.md), and [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md).
- **Grounding** — all agents ground on the ontology + synthetic Gold Delta tables produced in Sprint 10.
- **Golden-tasks** — 2 fixtures per agent, replayed via `.github/workflows/eval-goldens.yml`.

### 2.2 Out-of-scope / deferred

- App integration (Sprint 13's Copilot Drawer).
- Real PHI data (synthetic only per ADR-0006).
- CSA simulation engine, Cosmos DB provisioning, scenario catalog (Sprint 16).
- Adoption telemetry (Sprint 12/15 dependency).

### 2.3 Stretch — only if MVP lands early

- **`onboarding-agent`** — reads new sign-ins from the Entra audit log, drafts a welcome PR that files role-appropriate seed data. Ceiling: `write` on repo, `read` on `entra-mcp`.

---

## 3. Architecture and per-agent design

Each user-facing agent follows the same shape (single source of truth after the 2.0.0 folder restructure):

```text
agents/<name>/
├─ AGENT.md              # Identity + Scope + Tools + Refusal + Output + Confirmation
├─ manifest.yaml         # runtime manifest loaded by the Sprint 13 Container Apps agent-host
├─ golden-tasks.md       # ≥1 happy-path + ≥1 failure fixture
└─ (optional) prompts/   # Sub-prompts for phases if needed
```

### 3.1 Agent-by-agent scope summary

| Agent | Primary user | Primary output | Grounding | Notable refusal rules |
| --- | --- | --- | --- | --- |
| `bmca-agent` | Bed Manager | Bed placement recommendations, discharge candidates, pressure alerts | Bed state, occupancy, discharge readiness, ward capacity | No PHI in outputs; no direct bed reassignment |
| `ooa-agent` | ED Lead, Operations Lead | 72-h occupancy forecast, admission-pressure signals | Historical arrivals, seasonality, current census | Refuse forecasts for regions/hospitals outside assigned scope |
| `dca-agent` | Discharge Coordinator, Care-Transition | Ranked discharge candidates, blocker list, partner-handoff status | Bed state + LOS + care-transition readiness signals | No direct partner-org notification (advisory only) |
| `orsa-agent` | OR Coordinator | Idle-slot detection, slate reshuffle proposals, cancellation risk | OR slate, anaesthesia status, staff availability | No direct slate mutation |
| `sba-agent` | Staffing Coordinator | Staffing-gap heatmap, roster-vs-forecast deltas | Roster + shift plan + forecast | No direct roster edits |
| `csa-agent` (scaffold) | Crisis / Duty Manager | Scenario prep skeleton (Prepare phase stub) | Placeholder — filled in Sprint 16 | Refuse Run/Evaluate/Recommend until Sprint 16 (returns "not yet available") |
| `data-quality-agent` | Data engineer, Ontology Steward | Bronze/Silver/Gold contract-check reports, drift alerts | Delta table stats, ontology metadata | Refuse to mask PHI failures |
| `onboarding-agent` (stretch) | Platform Admin | Welcome PR into `data/onboarding/` with role-seeded persona layout | Entra audit log new-sign-in events | Refuse if UPN is not in the demo domain |

### 3.2 Common prompt sections (required)

Every `AGENT.md` includes these in this order:

1. **Identity** — name, owner, purpose (≤ 3 sentences).
2. **Scope** — which hospitals, roles, environments, and MCP servers are in-scope; explicit out-of-scope list.
3. **Tools** — every MCP tool the agent is allowed to call, with input/output shape and side-effect ceiling.
4. **Grounding sources** — Fabric tables, ontology entities, and any curated evidence files.
5. **Refusal rules** — shared refusals from [AGENTS.md §5](../../../AGENTS.md#5-refusal-rules-shared) plus per-agent additions.
6. **Output contract** — required shape of any comment, PR, or user-visible reply (redaction rules, citation requirements, tier/label expectations).
7. **Confirmation rules** — for any `deploy` or `delete` ceiling tool call, the `approved-to-apply` gate per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete).
8. **Golden-tasks path** — link to `golden-tasks.md`.

---

## 4. Agent and skill mix

| Agent | Superpowers skills used | Workspace domain skills used |
| --- | --- | --- |
| `bmca-agent`, `ooa-agent`, `dca-agent`, `orsa-agent`, `sba-agent` | `writing-plans`, `test-driven-development`, `verification-before-completion`, `subagent-driven-development` | `spark-authoring`, `fabric-semantic-model-authoring` |
| `csa-agent` (scaffold) | Same | Placeholder; full list in Sprint 16 |
| `data-quality-agent` | Same | `spark-operations`, `e2e-medallion-architecture` |
| `onboarding-agent` (stretch) | Same | (none — Microsoft Graph API direct) |

Follow [AGENTS.md skill-discovery rule of engagement](../../../AGENTS.md#skill-discovery--rule-of-engagement-v1140-2026-07-08) if a Sprint 11 subagent hits a domain gap.

---

## 5. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Issue template — agent build | `.github/ISSUE_TEMPLATE/agent-build.yml` | New agent build — one issue per agent |
| Issue template — sprint kickoff | `.github/ISSUE_TEMPLATE/sprint-kickoff.yml` | Sprint 11 kickoff |
| Workflow — eval goldens | `.github/workflows/eval-goldens.yml` | On PR to `agents/**` — replays fixtures against the Foundry chat-completion API (no Foundry Agent Service involved) |
| Labels | `sprint-11`, `agent-build`, `model-adr-required`, `superpowers-brainstorm`, `superpowers-plan`, `superpowers-execute` | Applied by templates |
| MCP allow-list | `.github/copilot/mcp.json` | Add `fabric-mcp` entry so the Sprint 13 agent-host can dispatch Fabric tool calls on behalf of the loaded agents |
| CODEOWNERS | `.github/CODEOWNERS` | `agents/**` → @urruegg |

**Delegation flow.** Kickoff issue opens → Copilot coding agent reads the roadmap + this design spec → uses `brainstorming` to confirm no gaps → invokes `writing-plans` to produce `plan.md` → invokes `subagent-driven-development` to build the 8 agents in parallel subagents (one per agent).

---

## 6. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| Prompt file changes (`agents/**`) | `write` | Standard PR review |
| Model deployment (if new SKU or region) | `deploy` | `approved-to-apply` + ADR |
| `onboarding-agent` reading Entra audit log | `read` | Consent gate — `AuditLog.Read.All` app permission granted once, revocable |
| Any deletion (agent, model, definition) | `delete` | Blocked in Sprint 11 |

> **Note.** No Foundry Agent Service deployments in Sprint 11 — per ADR-0008 the runtime is application-hosted. The Sprint 13 Container Apps agent-host loads the prompt manifests at runtime; Sprint 11 delivers the manifests, not the runtime.

---

## 7. Verification strategy

- **Golden-task replay** — every agent PR must include 2 golden fixtures; `eval-goldens.yml` must be green.
- **Refusal-rule test** — each agent has one fixture that prompts out-of-scope behaviour and expects a refusal that cites the specific refusal rule.
- **PHI/PII redaction test** — each agent has one fixture with synthetic PHI-shaped input; expected output redacts.
- **Cross-agent hygiene** — automated check that no agent's MCP scope leaks into another agent's tool list.
- **AGENTS.md consistency** — CI check that every agent under `agents/**` has a matching row in AGENTS.md §1 with matching ceiling.

---

## 8. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Foundry region drift (ADR-0013 westus2 demo scope) | ADR explicitly demo-only; model-selection ADR pins region per agent |
| Golden-task drift as prompts evolve | `eval-goldens.yml` runs on every push to `agents/**` |
| Cross-agent behaviour contamination | Each agent gets distinct MCP scope + role claim; hygiene check in CI |
| Onboarding-agent needing write to Entra | Kept read-only; welcome PRs are the only "write" (into the repo) |
| `csa-agent` scaffold used before Sprint 16 body | Scaffold explicitly returns "not yet available" for Run/Evaluate/Recommend phases |
| Model choice drifting from ADRs 0003/0004/0006 | Model-selection ADR referenced from every agent's `AGENT.md`; CI check that referenced ADR exists and is Accepted |

---

## 9. Dependencies

**In**: Sprint 10 synthetic Gold Delta tables; ontology semantic model; existing `AGENTS.md` registry.

**Out**: Sprint 12 (personas exist for testing agents against real identity), Sprint 13 (Copilot Drawer wires agents), Sprint 16 (`csa-agent` body).

---

## 10. Definition of done

- [ ] 8 agents (or 7 without stretch) have prompt file, golden-tasks, AGENTS.md row.
- [ ] Model-selection ADR merged and referenced by each agent.
- [ ] `eval-goldens.yml` workflow green.
- [ ] `agent-build.yml` and `sprint-kickoff.yml` issue templates in place.
- [ ] `fabric-mcp` entry added to `.github/copilot/mcp.json`.
- [ ] For each user-facing agent: prompt manifest + tool contract + HITL gate declaration ready for Sprint 13 runtime loading (no Foundry Agent Service deployment; agent-host runtime is Sprint 13 scope).
- [ ] Sprint 11 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
