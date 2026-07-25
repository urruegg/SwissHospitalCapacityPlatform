# Sprint 27 - Curavias Product Owner Agent: full build (Design)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Approved (brainstorming) |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 27 - Curavias Product Owner Agent full build (tracked by the Sprint 27 GitHub issue) |
| **Issue** | [#377](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/377) |
| **Extends** | Idea pack [`Curavias-Product-Owner-Agent-Proposal.md`](../ideas/Curavias-Product-Owner-Agent-Proposal.md) (Draft v1.2) |
| **Depends on** | Foundry control plane (Sprint 18, eastus2 / [ADR-0032](../../adr/0032-foundry-control-plane-eastus2.md)); PROD Switzerland North greenfield ([ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md)); `da_hospital_capacity` demo artefact ([ADR-0034](../../adr/0034-fabric-iq-demo-scope-artefacts.md)) |
| **Mirrors** | Sprint 23 master-data landing pattern (`infra/modules/data-foundation/masterdata-landing/`); Sprint 22 medallion; Sprint 21 signal-provider plugin |

> **For agentic workers:** This is the approved design for Sprint 27. The
> implementation plan is produced separately via `superpowers:writing-plans`
> ([`2026-07-25-sprint-27-product-owner-agent.md`](../plans/2026-07-25-sprint-27-product-owner-agent.md))
> and delegated per-workstream to parallel Copilot CLI worktrees via
> [`docs/runbooks/sprint-27-worktree-delegation.md`](../../runbooks/sprint-27-worktree-delegation.md).
> The brainstorming HARD-GATE is satisfied: this design was approved
> (interactive brainstorm, 2026-07-25) before any production code.

---

## 1. Goal and context

Build the **Curavias Product Owner Agent (PO Agent)** end-to-end in one sprint:
the authoritative, source-grounded, advisory-only voice of the platform,
embedded in the Curavias App as a Copilot rail. The PO Agent is **domain #1** on
a shared **Foundry IQ Knowledge Layer** that later serves any other agent role.

This sprint delivers the **full build** requested by the product owner - MVP
**and** the three items the proposal had marked post-MVP (Partner/external tier,
Multilingual parity, Additional knowledge domains) are **all in-sprint**. It is
an intentionally large "art of the possible" sprint; the size risk is tracked in
[Section 12](#12-risks). Preview services are accepted in PROD per the product
owner's direction.

The design body (personas, use cases, four knowledge classes, RAI, risks) lives
in the approved proposal
([`Curavias-Product-Owner-Agent-Proposal.md`](../ideas/Curavias-Product-Owner-Agent-Proposal.md)).
This spec covers **what we build this sprint and how it decomposes for parallel
delegation**.

## 2. Locked decisions (brainstorm 2026-07-25)

| # | Decision | Rationale |
| - | -------- | --------- |
| D1 | **Full build in one sprint** (MVP + all three former post-MVP items) | Product-owner direction: "full build MVP + post-MVP this sprint". |
| D2 | **Foundry IQ Knowledge Layer is the retrieval foundation**; Azure AI Search is the GA substrate beneath it | Learn confirms Foundry IQ = managed enterprise knowledge layer over Azure AI Search + Azure OpenAI; it is the "art of the possible" surface. |
| D3 | **Preview accepted in PROD (Switzerland North)** | Product-owner direction: show the art of the possible. Only Preview pieces are Foundry IQ agentic-retrieval (portal / preview API) and Fabric IQ + Fabric Data Agent (Class D). |
| D4 | **Four knowledge-source classes**: A governed corpus (daily GitHub -> ADLS -> OneLake -> knowledge source), B live-proof, C BVA/TCO cost, D ontology query surface (`da_hospital_capacity`) | Matches the approved proposal Section 6; Learn validates the Foundry IQ / Fabric IQ / Work IQ split. |
| D5 | **In-app Copilot rail on START + BACKSTAGE**, reusing the MAIN-board pattern (`AgentPlane` / `useAgentInvoker`) | Product-owner direction; "Backstage" = the Curavias App surface, not a Spotify plugin. |
| D6 | **Register a new `agents/product-owner-agent/` pack AND use subagent-driven execution**; package each workstream for a **parallel Copilot CLI worktree** | Product-owner direction: both the agent pack and the parallel-worktree delegation package. |
| D7 | **8 workstreams, granularity unchanged**; the three former post-MVP items fold **into** the existing 8, not into new workstreams | Product-owner direction: "workstream granularity -> no". |
| D8 | **Apply/deploy gated by `approved-to-apply`** on the PR/issue thread; ingestion/refresh jobs run as **Azure Container Apps**, never GitHub workflows | Standing platform rules (AGENTS.md Section 4; ADR-0002). |

## 3. Region and Preview posture (verified 2026-07-25)

Target region: **Switzerland North** (PROD greenfield, ADR-0037). Verified
against the repo record ([`docs/region-availability.yaml`](../../region-availability.yaml),
live `az` 2026-07-21) and Microsoft Learn.

| Service (role) | Switzerland North | Note |
| -------------- | ----------------- | ---- |
| Foundry IQ knowledge layer (Classes A/B/C retrieval) | Available | Built on Azure AI Search agentic retrieval + Azure OpenAI; Foundry projects are in swn. Some agentic-retrieval features GA, some Preview (portal is preview-only). |
| Azure AI Search (Foundry IQ substrate) | GA | Hybrid vector + keyword; the knowledge-base host. |
| Azure OpenAI (gpt-5 / o3 GlobalStandard; gpt-4.1 / 4o regional) | GA | Generation + query planning. |
| Foundry Agent Service (agent registration) | GA | Registers the `product-owner` agent id. |
| Fabric IQ ontology + Fabric Data Agent (Class D) | Preview | Per-capacity gated (issue #270), F2+ capacity, residency caveat; `da_hospital_capacity` is the demo artefact. |
| ADLS Gen2 / OneLake, Container Apps, Cosmos DB, Logic Apps, Key Vault | GA | Corpus landing, runtime, audit store, secrets. |

**Net:** nothing blocks the full build in swn PROD. Preview pieces (Foundry IQ
agentic-retrieval preview API; Fabric IQ / Data Agent) are accepted per D3.

## 4. Scope

Everything below is **in-sprint**. The three items the proposal marked post-MVP
are tagged `[was post-MVP]` and folded into the workstream that owns them.

- **Foundation**: shared Foundry IQ Knowledge Layer + PO Agent registered as domain #1.
- **Class A** governed corpus, daily GitHub -> ADLS -> OneLake -> knowledge source, PHI-excluded, interviews (`docs/reviews/`) first-order.
- **Class B** live-proof read-only probes (Resource Graph, Fabric REST, Foundry Agent API) with reconcile-and-flag.
- **Class C** BVA/TCO cost data product (effective PROD Azure cost + GitHub Copilot token cost, reconciled to BVA / ADR-0025).
- **Class D** ontology query surface via `da_hospital_capacity` Fabric Data Agent.
- **Experience** Copilot rail on START + BACKSTAGE (MAIN-board pattern) + `[was post-MVP]` partner-scoped surface variant.
- **Runtime** orchestration (route A/B/C/D -> ground -> cite), grounded-answer contract, authz-aware retrieval, audit logging, per-persona golden-question eval, RAI guardrails, `[was post-MVP]` multilingual (DE/EN) answering, `[was post-MVP]` partner entitlement tier.
- **Additional knowledge domains** `[was post-MVP]`: Compliance, Data, Operations mounted on the same layer to prove multi-domain reuse.

**Out of scope (explicit):** any real PHI (ADR-0016 - synthetic only); replacing
the MAIN-board agents; changing the runtime decision in ADR-0002.

## 5. Architecture

The authoritative architecture is proposal Sections 6, 7, 11. Summary:

```text
Curavias App (React / Fluent v9)
  START + BACKSTAGE Copilot rail  (AgentPlane -> useAgentInvoker('product-owner'))
        | HTTPS
PO Agent runtime  (Azure Container Apps, Switzerland North)
  orchestrator: query -> route(A/B/C/D) -> ground -> answer -> cite
  guardrails: authz filter, advisory-only, injection defence, multilingual
        |                        |
  Foundry IQ Knowledge Layer     Azure OpenAI (swn)
   Class A  corpus knowledge source (OneLake)
   Class B  live-proof tool  (Resource Graph / Fabric REST / Foundry Agent API, read)
   Class C  cost tool        (Cost Management + Copilot token cost + BVA)
   Class D  ontology tool    (da_hospital_capacity Fabric Data Agent, read)
        |
  Governance and ops: Entra ID + Managed Identity + Key Vault; Azure Policy;
  Purview lineage; Cosmos audit store (question -> sources -> answer);
  Monitor / Log Analytics / App Insights
```

## 6. Workstreams (8)

Each workstream is a **git worktree + branch** built in parallel by a delegated
Copilot CLI agent. Foundation workstreams (G0, INF) publish the interface
contracts ([Section 7](#7-interface-contracts)) first so the class workstreams
build to contract concurrently. Every `deploy` action is gated by
`approved-to-apply`.

| WS | Owns | Includes `[was post-MVP]` | Depends on | Branch |
| -- | ---- | ------------------------- | ---------- | ------ |
| **G0** Governance and agent pack | ADR(s), `agents/product-owner-agent/` pack, AGENTS.md row, PRD FR/NFR + Section 7, MCP allow-list review, additional-domain registration pattern | Additional-domain registration contract | - | `sprint-27/ws-g0-governance` |
| **INF** Infra (Bicep) | Azure AI Search + Foundry IQ knowledge base, ADLS corpus landing + OneLake shortcut, Container Apps runtime + daily refresh job, Cosmos audit store, Key Vault, RBAC, Azure OpenAI deploy | Extra knowledge-source scaffolding for Compliance/Data/Ops domains | G0 contracts | `sprint-27/ws-inf-bicep` |
| **A** Class A corpus | daily GitHub -> ADLS -> OneLake -> knowledge source, chunk/tag, PHI gate, interviews first-order | source-language tagging (DE/EN); Compliance/Data/Ops corpora | INF | `sprint-27/ws-a-corpus` |
| **B** Class B live-proof | read-only probes + reconcile-and-flag; the 5 reference questions | - | G0 | `sprint-27/ws-b-liveproof` |
| **C** Class C cost | Cost Management (PROD) + Copilot token cost + BVA reconciliation | - | G0 | `sprint-27/ws-c-cost` |
| **D** Class D ontology | wire `da_hospital_capacity`; concept + gold-binding citations | - | G0 | `sprint-27/ws-d-ontology` |
| **X** Experience rail | START + BACKSTAGE Copilot rail; MAIN-board pattern | partner-scoped surface variant; UI DE/EN | G0 | `sprint-27/ws-x-rail` |
| **RT** Runtime + eval + RAI | orchestrator, grounded-answer contract, authz-aware retrieval, audit logging, per-persona golden-question harness, transparency banner, injection defence | multilingual DE/EN answering; partner entitlement tier | A/B/C/D contracts | `sprint-27/ws-rt-runtime` |

## 7. Interface contracts

Published by G0 before class workstreams start so A/B/C/D/X/RT integrate in
parallel. Each class is a **typed, read-only tool** the orchestrator calls at
answer time; each returns a **grounded chunk** the citation layer renders
uniformly.

```text
GroundedChunk {
  classId:      "A" | "B" | "C" | "D"
  text:         string            # the retrieved / computed content
  citation:     { sourceRef, anchor?, conceptRef?, goldBinding? }
  asOf:         ISO-8601          # freshness stamp
  liveness:     "live" | "snapshot"
  status:       "verified" | "partial" | "requires-validation"
  confidence:   0.0 .. 1.0
  language:     "de" | "en"       # source language of the chunk
}
```

- **Class A** `retrieveCorpus(query, roleScope, lang) -> GroundedChunk[]` - Foundry IQ knowledge-base retrieve over the OneLake corpus knowledge source; `liveness` always `live` (daily refresh), `citation.sourceRef` = doc path + commit.
- **Class B** `liveProof(question, subscriptionScope) -> GroundedChunk[]` - read-only Resource Graph / Fabric REST / Foundry Agent API; reconciled against `docs/bom.yaml` / `docs/region-availability.yaml` / `AGENTS.md`; degrades to `snapshot` on failure.
- **Class C** `costAnswer(question) -> GroundedChunk[]` - Cost Management + Copilot token cost + BVA baseline (ADR-0025); ranges-with-assumptions, `citation.sourceRef` = feed + as-of.
- **Class D** `ontologyQuery(question) -> GroundedChunk[]` - `da_hospital_capacity` Fabric Data Agent; `citation.conceptRef` + `citation.goldBinding` required.
- **Orchestrator** `answer(question, caller) -> { answer, chunks[], status, confidence, language }` - routes to one or more classes, enforces the grounded-answer contract (>= N chunks over threshold or transparent partial), applies authz filter by caller entitlement + domain, logs the full bundle to the audit store.

## 8. Data flow

1. **Corpus refresh (daily, Container Apps Job).** Snapshot governed docs from GitHub -> ADLS `landing/curavias-product-corpus/<source>/<yyyy-mm-dd>/` -> OneLake shortcut -> chunk/tag (classification, residency, status, version/commit, date, language) -> PHI-exclusion gate -> Foundry IQ knowledge source.
2. **Query time.** Rail on START/BACKSTAGE -> runtime orchestrator -> route to Class A/B/C/D tools -> ground -> Azure OpenAI synthesis (advisory-only prompt) -> answer card with status/confidence/citations -> audit store.
3. **Live-proof / cost / ontology** resolve as read-only tool calls at answer time, provenance-stamped, degrading to `snapshot` on failure.

## 9. Security and governance

- **Region**: all runtime + data in Switzerland North; Preview services accepted (D3). Class D (Fabric Data Agent) currently reads the westus2 `da_hospital_capacity` demo artefact (ADR-0034) with the residency caveat documented.
- **PHI**: none (ADR-0016). Class A PHI-exclusion gate is mandatory; corpus is documentation only.
- **Identity**: Entra ID for callers; Managed Identity for all service-to-service; no static secrets (Key Vault). Foundry Agent Service registration uses the platform WIF identity.
- **Authorisation-aware retrieval**: per-domain knowledge sources + caller-entitlement filter. The `[was post-MVP]` partner tier is a distinct entitlement class that never sees internal cost/security detail.
- **Audit**: every question -> retrieved chunks -> citations -> confidence -> caller identity logged to Cosmos (EAA-style). Target 100% audit coverage.
- **MCP allow-list**: WS-G0 reviews [`.github/copilot/mcp.json`](../../../.github/copilot/mcp.json). Class B reuses `azure-mcp` (read); Class D reuses `fabric-mcp`. If the runtime needs a new MCP server it is a CODEOWNERS-gated change with a golden task.
- **HITL**: the agent-pack side-effect ceiling is `write` (advisory answers + drafts only). Any `deploy` in WS-INF is gated by `approved-to-apply`.

## 10. Testing and evaluation

- **Golden-question harness** (per-persona: CEO/COO/CIO/CFO/CTO/CISO/CDO/CLO + Developer/Architect/PM/Partner): accuracy, citation coverage (>= 95%), grounded-refusal correctness, zero hallucination on CFO/CISO/CLO classes.
- **Class fixtures**: A (citation + freshness), B (the 5 reference questions + reconcile-and-flag + snapshot degradation), C (cost fidelity within BVA +/- 30%), D (concept + gold-binding citation present).
- **Agent-pack golden tasks**: `agents/product-owner-agent/golden-tasks.md` with >= 1 happy-path + >= 1 failure-mode fixture, `requirement:` front-matter linking FR/NFR IDs.
- **Multilingual**: DE and EN parity fixtures with source-language transparency.
- **Infra**: `az bicep build` clean + `what-if` additive on every `infra/**` change.
- **Docs**: `check_mojibake.py` + `markdownlint-cli2` on every doc change.

## 11. Requirements (added to PRD by WS-G0)

New requirement family `FR-POA-*` / `NFR-POA-*`. WS-G0 adds these rows to
[`docs/PRD.md`](../../PRD.md) and its Section 7 traceability matrix in the same
change; golden tasks reference them via the `requirement:` key.

| ID | Requirement (summary) |
| -- | --------------------- |
| `FR-POA-001` | The PO Agent shall answer product questions grounded only on the four knowledge classes, with mandatory citations. |
| `FR-POA-002` | The PO Agent shall be embedded as a Copilot rail on the Curavias App START and BACKSTAGE surfaces using the MAIN-board pattern. |
| `FR-POA-003` | The knowledge layer shall be a shared Foundry IQ Knowledge Layer registering the PO Agent as domain #1 and supporting additional domains. |
| `FR-POA-004` | The corpus shall refresh daily GitHub -> ADLS -> OneLake -> knowledge source, PHI-excluded, interviews first-order. |
| `FR-POA-005` | Class B live-proof shall answer the five reference questions read-only with reconcile-and-flag. |
| `FR-POA-006` | Class C shall reconcile effective PROD Azure cost + GitHub Copilot token cost to the BVA/TCO baseline. |
| `FR-POA-007` | Class D shall answer data questions via the ontology with concept + gold-binding citations. |
| `FR-POA-008` | The PO Agent shall answer in DE and EN with source-language transparency. |
| `FR-POA-009` | The PO Agent shall expose an entitlement-scoped partner tier that never sees internal cost/security detail. |
| `NFR-POA-001` | Citation coverage >= 95%; zero hallucination on CFO/CISO/CLO classes. |
| `NFR-POA-002` | 100% audit coverage (question -> sources -> answer -> caller). |
| `NFR-POA-003` | All runtime + data in Switzerland North; no PHI; Preview services accepted per D3. |
| `NFR-POA-004` | Advisory-only, human-in-the-loop; the agent never mutates a system. |

## 12. Risks

| # | Risk | Mitigation |
| - | ---- | ---------- |
| R1 | **Sprint size** - full build + 3 former-post-MVP items is very large | Strict workstream isolation + parallel worktrees; foundation contracts first; each WS independently mergeable; ruthless YAGNI inside each WS. |
| R2 | **Preview instability** (Foundry IQ agentic-retrieval preview API; Fabric IQ / Data Agent per-capacity gate #270) | Pin the Search REST API version; feature-flag Class D; degrade to `snapshot`; accepted per D3. |
| R3 | **Cross-domain leakage** on the shared layer | Per-domain knowledge sources + authz-aware retrieval + entitlement tests in CI. |
| R4 | **Cost-answer hallucination** (CFO) | Class C data-product grounding; ranges-with-assumptions; refuse extrapolation; golden fixtures. |
| R5 | **Class D residency** (westus2 demo artefact) | Documented caveat; production Swiss grounding follows Fabric IQ swn GA (ADR-0014). |
| R6 | **Parallel-worktree merge conflicts** | Interface contracts frozen in G0; workstreams own disjoint paths; integration in WS-RT last. |

## 13. Delegation model

Each workstream is delegated to a **fresh Copilot CLI agent in its own git
worktree** per
[`docs/runbooks/sprint-27-worktree-delegation.md`](../../runbooks/sprint-27-worktree-delegation.md).
Execution order: **G0 + INF first** (publish contracts + provision-plan), then
**A/B/C/D/X in parallel**, then **RT** integrates. Each worktree agent reads its
workstream section of the plan + this spec + the referenced repo patterns, then
implements task-by-task via `superpowers:subagent-driven-development`. Every
`deploy` waits for `approved-to-apply`.

## 14. Follow-ups

- Fabric IQ Switzerland North GA lift for Class D production grounding (ADR-0014).
- Foundry IQ agentic-retrieval GA API migration when the preview features graduate.
- Deeper cost modelling (per-provider / per-tier TCO forecast) beyond run-rate.
