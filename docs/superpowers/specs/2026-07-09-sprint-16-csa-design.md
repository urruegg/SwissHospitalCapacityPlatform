# Sprint 16 — CSA What-If Scenario Research and Catalogue — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.2.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüeegg |
| **Status** | Draft for review |
| **Previous Version** | 1.1.0 (Sprint 16 T9 execution close-out: 4 Cosmos containers, 8 seeded scenarios, tier classifier ADR-0024, `csa-agent` full body, and 3 MVP runs delivered) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/superpowers/ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md](../ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md) |
| **Runtime posture** | Application-hosted per [ADR-0008](../../adr/0008-agent-runtime-pattern-scope-and-selection.md); loaded by the Sprint 13 Container Apps agent-host; chat model = Microsoft Foundry |
| **Best-practice references** | [Azure Cosmos DB — AI agents](https://learn.microsoft.com/azure/cosmos-db/ai-agents); [Agent memories in Azure Cosmos DB for NoSQL](https://learn.microsoft.com/azure/cosmos-db/gen-ai/agentic-memories); [Fabric Mirroring — Azure Cosmos DB](https://learn.microsoft.com/fabric/mirroring/azure-cosmos-db); [Agent Memory Toolkit for Azure Cosmos DB (preview)](https://learn.microsoft.com/azure/cosmos-db/gen-ai/agent-memory-toolkit) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture and data flow](#3-architecture-and-data-flow)
4. [Persistence — Cosmos DB for NoSQL + Fabric Mirroring](#4-persistence--cosmos-db-for-nosql--fabric-mirroring)
5. [`csa-agent` — Prepare → Run → Evaluate → Recommend](#5-csa-agent--prepare--run--evaluate--recommend)
6. [Tier classifier (Swiss Lage doctrine)](#6-tier-classifier-swiss-lage-doctrine)
7. [Seeded scenarios (the captured eight)](#7-seeded-scenarios-the-captured-eight)
8. [App wizard (Sprint 13 surface)](#8-app-wizard-sprint-13-surface)
9. [Agent and skill mix](#9-agent-and-skill-mix)
10. [GitHub delegation](#10-github-delegation)
11. [Side-effect posture and approval gates](#11-side-effect-posture-and-approval-gates)
12. [Verification strategy](#12-verification-strategy)
13. [Risks and mitigations](#13-risks-and-mitigations)
14. [Dependencies](#14-dependencies)
15. [Definition of done](#15-definition-of-done)

---

## 1. Goal and desired end state

The CSA is a working what-if system:

- scenarios live in **Azure Cosmos DB for NoSQL** (agent memory + catalog per Microsoft best practice — [Cosmos for AI agents](https://learn.microsoft.com/azure/cosmos-db/ai-agents));
- replicated to **Fabric OneLake via Mirroring** for analytical query ([ref](https://learn.microsoft.com/fabric/mirroring/azure-cosmos-db));
- the dedicated `csa-agent` walks users through a **Prepare → Run → Evaluate → Recommend** wizard in the Sprint 13 app;
- 8 seeded scenarios from the [CSA idea §6](../ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md#6-scenario-catalogue-captured-eight--evidence-impact-tier-levers-simulator-parameters) run end-to-end against synthetic Gold data;
- each run produces a Markdown recommendation PR into `docs/csa/runs/`;
- the tier classifier is grounded in the Swiss Lage doctrine (Normallage / Besondere Lage / Ausserordentliche Lage) per [§3.2 of the anchor idea](../ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md#32-the-csa-tier-model-review-session-tiers--swiss-doctrine).

---

## 2. Scope

### 2.1 In-scope MVP

- **Cosmos DB for NoSQL** provisioned via Bicep (`infra/modules/cosmos/csa.bicep`) with four containers (see §4).
- **Fabric Mirroring** enabled from Cosmos to OneLake (`fabric-mirrored-csa` Fabric item).
- **Dedicated `csa-agent`** — **application-hosted** agent (per [ADR-0008](../../adr/0008-agent-runtime-pattern-scope-and-selection.md); loaded by the Sprint 13 Container Apps agent-host; dispatched to a Foundry chat model), body written now (scaffold shipped in Sprint 11).
- **Tier classifier** — rules layer grounded on the Swiss Lage doctrine.
- **Response-lever library** — served from Cosmos as a reference container.
- **App wizard** — new page in Sprint 13 app (`apps/hcc-app-fluent/src/workspaces/main/wizards/csa/`) rendering the four phases with the `csa-agent` in the Copilot Drawer.
- **8 seeded scenarios** — the captured eight from the anchor idea §6. Seeded via `data-platform/scripts/csa-seed-scenarios.py`.
- **Simulation notebook** — `data-platform/notebooks/csa-simulate.ipynb` runs on Fabric Spark reading synthetic Gold capacity data; writes `DC-SIM-RESULT` back to Fabric.

### 2.2 Out-of-scope / deferred

- Full 20+ discovered scenarios (roadmap Q-5).
- External-actor integration modelling (Rega, KSD/IES) beyond notification events.
- Multi-user shared runs (single-user runs in MVP).
- Automated re-scoring on capacity-data change.
- Real PHI in simulations (synthetic only, ADR-0006).

---

## 3. Architecture and data flow

```text
                    ┌──────────────────────────────────────────────┐
                    │           React app (Sprint 13)              │
                    │  ┌────────────────────────────────────────┐  │
                    │  │  CSA Wizard (Prepare→Run→Evaluate→Rec)│  │
                    │  │  Copilot Drawer: csa-agent            │  │
                    │  └────────────────────────────────────────┘  │
                    └──────────┬───────────────────────────────────┘
                               │
                               ▼
                    ┌────────────────────────────────────┐
                    │  Container Apps agent-host (S13)  │
                    │  loads csa-agent prompt manifest  │
                    │  dispatches to Foundry chat model │
                    │  MCP: cosmos, fabric              │
                    └──────┬──────┬──────────────────────┘
                           │      │
              Read/write   │      │  Trigger notebook
                           ▼      ▼
                ┌──────────────┐  ┌───────────────────────────┐
                │  Cosmos NoSQL│  │  Fabric Notebook          │
                │  scenarios   │  │  csa-simulate.ipynb       │
                │  agent-mem   │  │  Reads Gold capacity data │
                │  levers      │  │  Writes DC-SIM-RESULT     │
                │  runs        │  └──────────┬────────────────┘
                └──────┬───────┘             │
                       │ mirror              │
                       ▼                     ▼
                Fabric OneLake ◀──────────Gold Delta tables
                (Delta replica of Cosmos)
                       │
                       ▼
                Power BI / semantic model for scenario analytics
```

---

## 4. Persistence — Cosmos DB for NoSQL + Fabric Mirroring

Microsoft-recommended shape for agent memory + catalog. Four containers:

| Container | Partition key | Vector policy | Purpose |
| --- | --- | --- | --- |
| `scenarios` | `/scenarioId` | `DiskANN` on `descriptionEmbedding` | Catalog of what-if scenarios (schema per anchor idea §4.1) |
| `agent-memory` | `/threadId` | `DiskANN` on `contentEmbedding`, sharded by `/threadId` | Per-run agent memory — one document per turn (per Microsoft best practice) |
| `response-levers` | `/leverId` | `quantizedFlat` on `descriptionEmbedding` | Doctrine-aligned mitigation library |
| `simulation-runs` | `/runId` | (none) | Run metadata + result references |

**Vector index rationale** — DiskANN for scenarios and agent-memory (per [Cosmos vector search guidance](https://learn.microsoft.com/azure/cosmos-db/gen-ai/agentic-memories#configure-a-vector-index)): high throughput, low latency, cost-efficient at scale, supports dynamic updates. Sharded by `/threadId` for agent-memory to keep per-run search focused. `quantizedFlat` for response-levers because the library is small (< 100 items).

**Consistency level** — Session (default), which suits agent memory read-your-writes needs.

**Fabric Mirroring** — enabled at container level; Delta tables surface `scenarios`, `agent-memory`, `response-levers`, `simulation-runs` in the Fabric SQL analytics endpoint for BI join with Gold capacity data. No RU consumption for mirroring reads.

**Preview caveat.** Fabric Mirroring for external Azure Cosmos DB is currently in preview and not available in sovereign clouds. Demo scope is `westus2` per [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md), which accepts preview features. Fallback if mirroring is blocked at go-live: a manual Spark job copies Cosmos change-feed events into Fabric Bronze.

**Optional accelerator.** The [Agent Memory Toolkit for Azure Cosmos DB (preview)](https://learn.microsoft.com/azure/cosmos-db/gen-ai/agent-memory-toolkit) is a candidate scaffold — evaluate in the Sprint 16 kickoff brainstorm.

---

## 5. `csa-agent` — Prepare → Run → Evaluate → Recommend

**Application-hosted** agent per [ADR-0008](../../adr/0008-agent-runtime-pattern-scope-and-selection.md), loaded by the Sprint 13 Container Apps agent-host at runtime. Dispatches to a **Microsoft Foundry** chat model. MCP servers: `github-mcp`, `fabric-mcp`, `cosmos-mcp`. Ceiling: `write` (for scenarios / recommendations), `deploy` for simulation-run trigger (gated).

**Phase 1 — Prepare.** Agent interviews the user (via Copilot Drawer), retrieves similar scenarios from Cosmos via vector search, proposes parameters (magnitude, duration, cascade). User confirms.

**Phase 2 — Run.** Agent writes a `simulation-runs` document, triggers `csa-simulate.ipynb` via Fabric REST, returns a "run started" message. Async pattern — user gets a webhook / notification when result ready.

**Phase 3 — Evaluate.** Agent reads the simulation output from Fabric, classifies tier (§6), retrieves matching response levers from Cosmos.

**Phase 4 — Recommend.** Agent emits a Markdown recommendation, opens a draft PR into `docs/csa/runs/YYYY-MM-DD-<scenarioId>.md`. PR body includes tier, key impacts, response levers, KPI expectations, and doctrine citations.

**Refusal rules (in addition to shared).**

- Refuse to run a scenario the user does not have `HCC.CrisisManager`, `HCC.OperationsLead`, `HCC.PlatformAdmin`, or `HCC.SuperAdmin` role for.
- Refuse to include real-PHI data in any output.
- Refuse to auto-execute any response lever (advisory only).

---

## 6. Tier classifier (Swiss Lage doctrine)

Rules layer over ontology capacity states. Escalates a scenario to Tier 2 or Tier 3 when:

- **Tier 2 — Besondere Lage** — one+ resource dimension breaches threshold; internal reallocation required; single-site.
- **Tier 3 — Ausserordentliche Lage** — demand exceeds site capacity even after internal levers; special capability overwhelmed (burn ICU, ventilators, decontamination); multi-canton or severe-consequence per VKSD Art. 2.

Rules are version-pinned; every change requires an ADR reference. Encoded in `data-platform/scripts/csa-tier-classifier.py`.

---

## 7. Seeded scenarios (the captured eight)

Seeded via `data-platform/scripts/csa-seed-scenarios.py`. Each seeded scenario carries the anchor idea's schema fields (`trigger`, `shockVector`, `affectedResources`, `magnitude`, `onset`, `duration`, `cascade`, `scarceCapability`, `defaultTier`, `responseLevers`, `kpis`, `hospitalRelevance`).

| # | Scenario | Family | Default tier | MVP-required run |
| --- | --- | --- | --- | --- |
| 1 | Helipad elevator failure | F1 | 2 | — |
| 2 | Ward specialists at congress | F2 | 1–2 | — |
| 3 | Crans-Montana burns MCI | F3 | 3 | — |
| 4 | Cyberattack on hospital services | F4 | 2–3 | **✔ MVP** |
| 5 | Ventilator supply shortage | F5 | 2–3 | — |
| 6 | Pediatric virus surge (RSV) | F6 | 2 | **✔ MVP** |
| 7 | Terror attack + risk of second hit | F7 | 3 | — |
| 8 | Summer heatwave demand surge | F8 | 1–2 | **✔ MVP** (bed-pressure heatwave) |

MVP requires end-to-end runs for the three ticked scenarios (yielding merged recommendation PRs).

---

## 8. App wizard (Sprint 13 surface)

- New page `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/` behind a role gate (`HCC.CrisisManager`, `HCC.OperationsLead`, `HCC.PlatformAdmin`, `HCC.SuperAdmin`).
- Uses the whiteboard framework's card catalog for scenario cards; renders Prepare / Run / Evaluate / Recommend as sequential steps with progress indicator.
- Copilot Drawer stays open in the right rail, showing the `csa-agent` conversation for the current wizard step.
- Async run pattern — Run step returns immediately with a `runId`; user is notified when Evaluate is ready.

---

## 9. Agent and skill mix

| Component | Superpowers skills | Domain skills |
| --- | --- | --- |
| `csa-agent` body | `writing-plans`, `test-driven-development`, `verification-before-completion` | `spark-authoring`, `fabric-semantic-model-authoring` |
| Cosmos IaC | Same | Bicep best-practice |
| Fabric Mirroring setup | Same | `spark-authoring` |
| Notebook (`csa-simulate.ipynb`) | Same | `spark-authoring`, `spark-operations` |
| CSA wizard (React) | Same | (from Sprint 13 stack) |
| Seed + tier classifier scripts | Same | (none) |

---

## 10. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Issue template — CSA scenario | `.github/ISSUE_TEMPLATE/csa-scenario.yml` | New/updated scenario (round-trips to Cosmos via workflow) |
| Issue template — CSA run | `.github/ISSUE_TEMPLATE/csa-run.yml` | Requested simulation run |
| Workflow — scenario sync | `.github/workflows/csa-scenario-sync.yml` | On merge of `data/csa/scenarios/*.yaml` → upsert into Cosmos |
| Workflow — run follow-up | `.github/workflows/csa-run-followup.yml` | On `docs/csa/runs/*.md` PR merge → close the parent run issue |
| MCP additions | `.github/copilot/mcp.json` | `cosmos-mcp`, `fabric-mcp` (added in S14 if not already) |
| CODEOWNERS | `.github/CODEOWNERS` | `docs/csa/**`, `infra/modules/cosmos/**` → @urruegg |
| Labels | `sprint-16`, `csa`, `csa-scenario`, `csa-recommendation`, `cosmos-provision` | Applied by templates |

---

## 11. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| Cosmos DB provisioning | `deploy` | `approved-to-apply` + `cosmos-provision` label |
| Fabric Mirroring enable | `deploy` | `approved-to-apply` |
| Scenario upsert to Cosmos | `write` | Automated (workflow only after PR merge) |
| Simulation run trigger | `write` | User initiates in the wizard; agent runs; result review manual |
| Recommendation PR into `docs/csa/runs/` | `write` | Standard PR review |
| Cosmos data deletion | `delete` | Blocked; manual portal only during MVP |

---

## 12. Verification strategy

- **Cosmos IaC** — `az deployment ... what-if` clean before apply; RU budget documented.
- **Cosmos schema smoke** — unit tests for scenario upsert / vector search / hybrid search on all four containers.
- **Notebook golden test** — for the RSV surge scenario with fixed capacity input, the simulation returns Tier 2 with expected KPI values.
- **Agent golden-tasks** — one fixture per seeded scenario: Prepare produces expected parameter shape; Recommend produces a PR with tier + levers matching doctrine.
- **Mirroring smoke** — verify Delta table appears in OneLake within 15 min of first write to a mirrored container.
- **E2E** — `HCC.CrisisManager` starts the wizard, picks "Cyber attack", runs, receives recommendation PR in the repo.
- **RBAC test** — `HCC.GuestReadOnly` cannot open the wizard.

---

## 13. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Fabric Mirroring for external Cosmos is preview + not in sovereign clouds | Demo scope westus2 per ADR-0013 accepts preview; fallback = manual Spark job copying change-feed to Bronze |
| Cosmos RU costs from vector search under load | DiskANN + sharded index by `threadId`; monitor RU consumption; cap request concurrency |
| Notebook simulation runtime > wizard timeout | Async pattern: agent returns "run started, will notify"; user gets a webhook when result is ready |
| Scenario schema drift between YAML and Cosmos | `csa-scenario-sync.yml` validates against JSON schema before upsert; PR blocked if schema fails |
| Recommendation PRs pile up | Label `csa-recommendation` + a Projects lane; auto-close if not merged in 30 days |
| Tier classifier misclassifies (doctrine drift) | Rules layer version-pinned; every change requires an ADR reference |
| `HCC.GuestReadOnly` accidentally sees the wizard button | Role-gated route + component; RBAC E2E test |
| Cosmos deletion during MVP causes data loss | `delete` ceiling blocked; deletion requires portal + `delete-confirmed` label + explicit `approved-to-apply` |

---

## 14. Dependencies

**In**: Sprint 11 (`csa-agent` scaffold), Sprint 13 (app wizard surface + whiteboard card framework), Sprint 10 (Gold capacity data), Sprint 14 (ontology cards on the presenter whiteboard for cross-drilling).

**Out**: (none downstream — Sprint 16 is the finale of the roadmap).

---

## 15. Definition of done

- [ ] Cosmos DB provisioned via Bicep with the four containers.
- [ ] Fabric Mirroring live (or documented fallback in place).
- [ ] 8 seeded scenarios in Cosmos with vector search working.
- [ ] `csa-agent` completes Prepare → Run → Evaluate → Recommend for the 3 MVP-tagged scenarios end-to-end.
- [ ] App wizard rendered in Sprint 13 app with role gating verified.
- [ ] 3 recommendation PRs merged into `docs/csa/runs/`.
- [ ] Tier classifier verified against doctrine table §3.2.
- [ ] `csa-scenario-sync.yml` + `csa-run-followup.yml` workflows green.
- [ ] Sprint 16 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
