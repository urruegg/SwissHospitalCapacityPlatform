# Curavias Product Owner Agent (Sprint 28) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Each workstream is delegated to its own git worktree per [`docs/runbooks/sprint-28-worktree-delegation.md`](../../runbooks/sprint-28-worktree-delegation.md).

**Goal:** Build the Curavias Product Owner Agent end-to-end - four knowledge classes (A corpus, B live-proof, C cost, D ontology), the Foundry IQ Knowledge Layer foundation, the START/BACKSTAGE Copilot rail, and the runtime/eval/RAI - as 8 parallelizable workstreams.

**Architecture:** Foundry IQ Knowledge Layer (Azure AI Search + OneLake) beneath a Container Apps runtime in Switzerland North; the PO Agent registered in Foundry Agent Service as domain #1; an in-app Copilot rail reusing the MAIN-board `AgentPlane` pattern. See [`2026-07-25-sprint-28-product-owner-agent-design.md`](../specs/2026-07-25-sprint-28-product-owner-agent-design.md).

**Tech Stack:** Bicep (Azure AI Search, Foundry IQ, ADLS Gen2, Container Apps, Cosmos, Key Vault, Azure OpenAI); Python 3 stdlib (corpus refresh, live-proof, cost, ontology tools + `pytest`); TypeScript / React / Fluent v9 (Copilot rail); Markdown (agent pack, ADRs, PRD).

---

## Hard constraints (apply to every task)

- **Runtime `python`, not `python3`.** All commands use `python`.
- **Commit with hooks disabled if needed:** `git -c core.hooksPath=/dev/null commit -m "..."`.
- **Ingestion / refresh jobs run as Azure Container Apps, never GitHub workflows.**
- **Synthetic / no-PHI only** (ADR-0016).
- **Human always reviews + merges every PR. Never self-merge.** One small PR per slice, each linked to the Sprint 28 issue.
- **Trunk-based per ADR-0038:** short-lived branch off `main` per PR; branch names `sprint-28/<ws>-<slice>`.
- **Deploy/delete gated by `approved-to-apply`** on the PR/issue thread before any `az deployment` apply.
- **Doc edits** follow copilot-instructions Section 9 + the `document-authoring` skill; mojibake/lint gates enforced by CI.
- **Region = Switzerland North.** Preview accepted in PROD (design D3). No hard-coded subscription/tenant/resource ids.

## Dependency order between workstreams

```text
WS-G0 (governance + contracts) ── publishes GroundedChunk + tool contracts ──┐
WS-INF (infra Bicep, what-if only) ──────────────────────────────────────────┤
                                                                             ▼
WS-A (corpus)   WS-B (live-proof)   WS-C (cost)   WS-D (ontology)   WS-X (rail)   (parallel)
                                                                             │
                                                                             ▼
                                                        WS-RT (runtime + eval + RAI integrates classes)
```

G0 + INF first. A/B/C/D/X in parallel against the frozen contracts. RT integrates last.

## File structure

- `agents/product-owner-agent/{AGENT.md,manifest.yaml,golden-tasks.md}` - agent pack (WS-G0).
- `docs/adr/00NN-product-owner-agent-foundry-iq-domain.md` - ADR (WS-G0).
- `infra/modules/knowledge-layer/{ai-search,foundry-iq-knowledge-base,corpus-landing}/main.bicep` - infra (WS-INF).
- `infra/modules/experience-hosting/po-agent-runtime/main.bicep` - runtime + refresh job (WS-INF).
- `data-platform/scripts/po-agent/corpus/*` - Class A corpus refresh (WS-A).
- `data-platform/scripts/po-agent/{liveproof,cost,ontology}/*` - Class B/C/D tools (WS-B/C/D).
- `apps/hcc-app-fluent/src/shell/planes/ProductOwnerRail.*` - Copilot rail (WS-X).
- `data-platform/scripts/po-agent/runtime/*` + `evals/product-owner-agent/*` - orchestrator + eval (WS-RT).

---

## WS-G0 - Governance and agent pack (branch `sprint-28/ws-g0-governance`)

> Publishes the interface contracts the class workstreams build against. Merge first.

### Task G0.1: ADR - PO Agent as Foundry IQ domain #1

**Files:** Create `docs/adr/00NN-product-owner-agent-foundry-iq-domain.md`

- [ ] **Step 1** - Write the ADR: context (proposal v1.2), decision (PO Agent = domain #1 on Foundry IQ Knowledge Layer; Azure AI Search substrate; Preview accepted in PROD per D3), consequences, links to ADR-0002/0014/0033/0034/0037. Status `Accepted`.
- [ ] **Step 2: Doc gates** - Run: `python scripts/lint/check_mojibake.py docs/adr/00NN-*.md; npx --yes markdownlint-cli2 "docs/adr/00NN-*.md"` - Expected: clean.
- [ ] **Step 3: Commit** - `git commit -am "docs(adr): PO Agent as Foundry IQ domain #1 (#<issue>)"`

**Acceptance gate:** ADR Accepted; doc gates green; cross-links resolve.

### Task G0.2: Freeze interface contracts

**Files:** Create `docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md`

- [ ] **Step 1** - Transcribe the `GroundedChunk` shape and the five tool signatures (design Section 7) as the frozen contract, with a JSON Schema for `GroundedChunk` under `data/synthetic/schema/grounded-chunk-v1.schema.json`.
- [ ] **Step 2** - Add one example `GroundedChunk` per class as fixtures under `evals/product-owner-agent/fixtures/`.
- [ ] **Step 3: Commit** - `git commit -am "docs(spec): freeze PO Agent class-tool contracts (#<issue>)"`

**Acceptance gate:** schema validates the example fixtures; contracts referenced by all class workstreams.

### Task G0.3: Agent pack

**Files:** Create `agents/product-owner-agent/{AGENT.md,manifest.yaml,golden-tasks.md}`; Modify `AGENTS.md`

- [ ] **Step 1** - Author `AGENT.md` with the fixed structure (Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules); side-effect ceiling `write` (advisory answers + drafts). Mirror `agents/knowledge-agent/AGENT.md` structure.
- [ ] **Step 2** - Author `manifest.yaml` (mirror `agents/knowledge-agent/manifest.yaml`): `runtime: copilot-coding-agent`; `mcpTools` = `github-mcp` (write), `azure-mcp` (read, Class B/C), `fabric-mcp` (read, Class D); `hitl.gates` empty (write ceiling); `goldenTasksRef`.
- [ ] **Step 3** - Author `golden-tasks.md`: >= 1 happy-path + >= 1 failure-mode, `requirement: FR-POA-001` front-matter.
- [ ] **Step 4** - Add the registry row to `AGENTS.md` Section 1 + bump its version header.
- [ ] **Step 5: Doc gates** - Run: `python scripts/lint/check_mojibake.py agents/product-owner-agent/*.md AGENTS.md; npx --yes markdownlint-cli2 "agents/product-owner-agent/*.md" "AGENTS.md"` - Expected: clean.
- [ ] **Step 6: Commit** - `git commit -am "feat(agents): register product-owner-agent pack (#<issue>)"`

**Acceptance gate:** pack complete; AGENTS.md row present + version bumped; doc gates green.

### Task G0.4: PRD requirements + MCP allow-list review

**Files:** Modify `docs/PRD.md`; review `.github/copilot/mcp.json`

- [ ] **Step 1** - Add `FR-POA-001..009` + `NFR-POA-001..004` (design Section 11) to `docs/PRD.md` and its Section 7 traceability matrix; bump PRD version (MINOR).
- [ ] **Step 2** - Confirm `.github/copilot/mcp.json` already lists `github-mcp` / `azure-mcp` / `fabric-mcp`; if the runtime needs a new server, open a separate CODEOWNERS-gated PR (do not add here).
- [ ] **Step 3: Doc gates + Commit** - gates green; `git commit -am "docs(prd): add FR/NFR-POA requirements (#<issue>)"`.

**Acceptance gate:** PRD rows + matrix consistent; no unreviewed MCP additions.

---

## WS-INF - Infra Bicep (branch `sprint-28/ws-inf-bicep`)

> `az bicep build` + `what-if` only. No apply in a PR merge; apply is `approved-to-apply` gated.

### Task INF.1: Knowledge-layer module (AI Search + Foundry IQ knowledge base)

**Files:** Create `infra/modules/knowledge-layer/ai-search/main.bicep`, `infra/modules/knowledge-layer/foundry-iq-knowledge-base/main.bicep`; Modify `infra/main.bicep`, `infra/environments/{sit,prod}.bicepparam`

- [ ] **Step 1** - Azure AI Search (swn, hybrid vector+keyword tier), managed identity, diagnostic settings -> Log Analytics (prod). Name `srch-ihzhhpf-<env>`; tag `env`/`owner`/`costCenter`/`workload`.
- [ ] **Step 2** - Foundry IQ knowledge base wiring (pin the Search REST API version; document the preview-vs-GA split per design R2). Where a resource type is not Bicep-provisionable, add a REST runbook `.md` beside the module (mirror `masterdata-landing/onelake-shortcut.md`).
- [ ] **Step 3: Build** - Run: `az bicep build --file infra/main.bicep` - Expected: clean.
- [ ] **Step 4: what-if (SIT)** - Run: `az deployment group what-if -g <rg-sit> -f infra/main.bicep -p infra/environments/sit.bicepparam` - Expected: additive only; paste summary into PR; do not apply.
- [ ] **Step 5: Commit** - `git commit -am "feat(infra): knowledge-layer AI Search + Foundry IQ knowledge base (#<issue>)"`

**Acceptance gate:** builds clean; `what-if` additive; API version pinned; no hard-coded ids.

### Task INF.2: Corpus landing + runtime + refresh job

**Files:** Create `infra/modules/knowledge-layer/corpus-landing/main.bicep`, `infra/modules/experience-hosting/po-agent-runtime/main.bicep`; Modify `infra/main.bicep` + params

- [ ] **Step 1** - ADLS Gen2 corpus landing (`isHnsEnabled`, `landing/curavias-product-corpus/`) mirroring `masterdata-landing`; OneLake shortcut runbook `.md`.
- [ ] **Step 2** - Container Apps runtime app + a **scheduled Container Apps Job** for the daily corpus refresh (manual+cron trigger); Cosmos audit store; Key Vault; Azure OpenAI deployment (swn); RBAC (managed-identity least privilege: Search index, Storage Blob Data, Cosmos Data Contributor).
- [ ] **Step 3: Build + what-if (SIT)** - additive only; paste; do not apply.
- [ ] **Step 4: Commit** - `git commit -am "feat(infra): PO Agent runtime + corpus landing + refresh job (#<issue>)"`

**Acceptance gate:** builds; `what-if` additive; refresh job is Container Apps (not a GitHub workflow); tags applied.

---

## WS-A - Class A corpus (branch `sprint-28/ws-a-corpus`)

**Files:** Create `data-platform/scripts/po-agent/corpus/{snapshot.py,chunk_tag.py,phi_gate.py,publish.py,tests/}`

- [ ] **Step 1: Failing test** - `tests/test_phi_gate.py`: assert any chunk tagged `classification: phi` is dropped before publish.
- [ ] **Step 2: Run test** - Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_phi_gate.py -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `snapshot.py` (GitHub docs tree -> ADLS landing folder), `chunk_tag.py` (heading/ADR/contract boundaries; tags classification/residency/status/version/commit/date/**language**), `phi_gate.py`, `publish.py` (-> Foundry IQ knowledge source). **Interviews (`docs/reviews/`) are first-order** (own tag), plus Compliance/Data/Ops corpora subsets for the additional domains.
- [ ] **Step 4: Run tests** - Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/ -v` - Expected: PASS (PHI gate, chunk-boundary, language-tag, interview-first-order).
- [ ] **Step 5: Commit** - `git commit -am "feat(po-agent): Class A corpus refresh pipeline (#<issue>)"`

**Acceptance gate:** PHI gate proven; language tags present; interviews first-order; `GroundedChunk` conformance test green.

---

## WS-B - Class B live-proof (branch `sprint-28/ws-b-liveproof`)

**Files:** Create `data-platform/scripts/po-agent/liveproof/{probes.py,reconcile.py,tests/}`

- [ ] **Step 1: Failing test** - `tests/test_reconcile.py`: given a mocked Resource Graph result whose SKU differs from `docs/bom.yaml`, assert `reconcile()` returns both values flagged `drift`.
- [ ] **Step 2: Run test** - Run: `python -m pytest data-platform/scripts/po-agent/liveproof/tests/test_reconcile.py -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `probes.py` (read-only Resource Graph, Fabric REST, Foundry Agent API for the 5 reference questions), `reconcile.py` (compare to `bom.yaml`/`region-availability.yaml`/`AGENTS.md`; degrade to `snapshot` on failure). All calls read-only; mock live services in tests.
- [ ] **Step 4: Run tests** - Run: `python -m pytest data-platform/scripts/po-agent/liveproof/tests/ -v` - Expected: PASS (5 reference questions + drift-flag + snapshot degradation).
- [ ] **Step 5: Commit** - `git commit -am "feat(po-agent): Class B live-proof probes (#<issue>)"`

**Acceptance gate:** 5 reference questions covered; reconcile-and-flag proven; strictly read-only; snapshot degradation tested.

---

## WS-C - Class C cost (branch `sprint-28/ws-c-cost`)

**Files:** Create `data-platform/scripts/po-agent/cost/{azure_cost.py,copilot_cost.py,reconcile_bva.py,tests/}`

- [ ] **Step 1: Failing test** - `tests/test_reconcile_bva.py`: given a mocked run-rate, assert the answer is presented as a range within the BVA +/- 30% band with an as-of stamp and refuses extrapolation beyond the feed window.
- [ ] **Step 2: Run test** - Run: `python -m pytest data-platform/scripts/po-agent/cost/tests/test_reconcile_bva.py -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `azure_cost.py` (Cost Management PROD, read), `copilot_cost.py` (GitHub Copilot token/usage cost feed), `reconcile_bva.py` (against `docs/BVA.md` + ADR-0025 `bva_kpi.py`). Ranges-with-assumptions only.
- [ ] **Step 4: Run tests** - Run: `python -m pytest data-platform/scripts/po-agent/cost/tests/ -v` - Expected: PASS.
- [ ] **Step 5: Commit** - `git commit -am "feat(po-agent): Class C cost data product (#<issue>)"`

**Acceptance gate:** cost answers are ranges within BVA band with as-of; extrapolation refused; feeds read-only.

---

## WS-D - Class D ontology (branch `sprint-28/ws-d-ontology`)

**Files:** Create `data-platform/scripts/po-agent/ontology/{data_agent.py,tests/}`

- [ ] **Step 1: Failing test** - `tests/test_data_agent.py`: assert every `ontologyQuery()` result carries `citation.conceptRef` + `citation.goldBinding`.
- [ ] **Step 2: Run test** - Run: `python -m pytest data-platform/scripts/po-agent/ontology/tests/test_data_agent.py -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `data_agent.py` wrapping the `da_hospital_capacity` Fabric Data Agent (read-only), returning `GroundedChunk` with concept + gold-binding citation; feature-flag for the Preview per-capacity gate (#270); mock the Data Agent in tests.
- [ ] **Step 4: Run tests** - Run: `python -m pytest data-platform/scripts/po-agent/ontology/tests/ -v` - Expected: PASS.
- [ ] **Step 5: Commit** - `git commit -am "feat(po-agent): Class D ontology query surface (#<issue>)"`

**Acceptance gate:** concept + gold-binding citation enforced; read-only; Preview feature-flagged.

---

## WS-X - Experience rail (branch `sprint-28/ws-x-rail`)

**Files:** Create `apps/hcc-app-fluent/src/shell/planes/ProductOwnerRail.tsx` (+ test); Modify START + BACKSTAGE surface hosts

- [ ] **Step 1: Failing test** - Jest test: the rail renders docked full-height on START and BACKSTAGE, opens on a proactive default card, and never renders empty.
- [ ] **Step 2: Run test** - Run: `npm --prefix apps/hcc-app-fluent test -- ProductOwnerRail` - Expected: FAIL.
- [ ] **Step 3: Implement** - `ProductOwnerRail.tsx` reusing the MAIN-board `AgentPlane` -> `useAgentInvoker('product-owner')` + `ConversationView`; proactive default; insight-click -> pre-formed question; answer card with status chip / confidence / citations; **partner-scoped surface variant** and **DE/EN UI language** toggle. Mount on START + BACKSTAGE.
- [ ] **Step 4: Run tests** - Run: `npm --prefix apps/hcc-app-fluent test -- ProductOwnerRail` - Expected: PASS.
- [ ] **Step 5: Commit** - `git commit -am "feat(app): PO Agent Copilot rail on START + BACKSTAGE (#<issue>)"`

**Acceptance gate:** rail parity with MAIN-board pattern; partner variant + DE/EN present; tests green.

---

## WS-RT - Runtime + eval + RAI (branch `sprint-28/ws-rt-runtime`)

> Integrates the class tools. Depends on A/B/C/D contracts.

### Task RT.1: Orchestrator + grounded-answer contract

**Files:** Create `data-platform/scripts/po-agent/runtime/{orchestrator.py,authz.py,audit.py,tests/}`

- [ ] **Step 1: Failing test** - `tests/test_grounded_contract.py`: assert `answer()` degrades to a transparent partial when fewer than N chunks clear the threshold, and never emits an uncited claim.
- [ ] **Step 2: Run test** - Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_grounded_contract.py -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `orchestrator.py` (route A/B/C/D -> ground -> synthesise -> cite; **multilingual DE/EN**), `authz.py` (per-domain + caller-entitlement filter incl. **partner tier**), `audit.py` (log question -> chunks -> citations -> confidence -> caller to Cosmos).
- [ ] **Step 4: Run tests** - Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/ -v` - Expected: PASS.
- [ ] **Step 5: Commit** - `git commit -am "feat(po-agent): runtime orchestrator + grounded-answer contract (#<issue>)"`

**Acceptance gate:** grounded-answer contract proven; authz + partner tier enforced; audit bundle complete; DE/EN routing.

### Task RT.2: Per-persona golden-question harness + RAI

**Files:** Create `evals/product-owner-agent/{golden_questions.yaml,run_evals.py,tests/}`

- [ ] **Step 1: Failing test** - assert the harness fails a run with any uncited claim on a CFO/CISO/CLO question (zero-hallucination gate) and computes citation coverage.
- [ ] **Step 2: Run test** - Run: `python -m pytest evals/product-owner-agent/tests/ -v` - Expected: FAIL.
- [ ] **Step 3: Implement** - `golden_questions.yaml` (per-persona incl. Partner, DE + EN), `run_evals.py` (accuracy, citation coverage >= 95%, grounded-refusal correctness, zero-hallucination gate); transparency banner + injection-defence assertions.
- [ ] **Step 4: Run tests** - Run: `python -m pytest evals/product-owner-agent/tests/ -v` - Expected: PASS.
- [ ] **Step 5: Commit** - `git commit -am "test(po-agent): per-persona golden-question harness + RAI gates (#<issue>)"`

**Acceptance gate:** harness enforces >= 95% citation coverage + zero CFO/CISO/CLO hallucination; DE/EN + Partner personas covered.

---

## Self-review checklist (run before handoff)

- **Spec coverage:** every design Section 4 scope item and every `FR-POA-*` maps to a task above.
- **Contract consistency:** the `GroundedChunk` shape + five tool signatures are identical across G0.2 and WS-A/B/C/D/RT.
- **No placeholders:** replace `#<issue>` (this is issue [#377](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/377)) and `00NN` (the ADR number, assigned in WS-G0) with the real values at execution time.
- **Region/PHI:** every infra task targets swn; no PHI anywhere.

## Execution handoff

**Two execution options:**

1. **Parallel Copilot CLI worktrees (chosen)** - one worktree per workstream per [`docs/runbooks/sprint-28-worktree-delegation.md`](../../runbooks/sprint-28-worktree-delegation.md); G0 + INF first, then A/B/C/D/X in parallel, then RT.
2. **Subagent-Driven (in-session)** - `superpowers:subagent-driven-development`, fresh subagent per task with spec + quality review gates.
