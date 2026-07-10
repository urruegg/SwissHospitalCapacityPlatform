# Sprint 14 — Showcase Evidence Data Product (presenter whiteboard) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the showcase-evidence data product end-to-end per the design spec — from repo edits through the Fabric medallion into a presenter whiteboard in Backstage that renders BOM + ADR + PRD-requirement + GA-evidence + dependency-edge cards with provenance on every card.

**Architecture:** Sequential-ish with explicit parallelism. Reuses Sprint 13's whiteboard framework (`apps/hcc-app-fluent/src/whiteboard/`) — Sprint 14 adds a **new card registry** for the 5 evidence card types; the framework is not forked. Fabric medallion pattern from Sprint 10 (Bronze → Silver → Gold star schema). Direct Lake semantic model owned by Sprint 09 v2, extended with evidence tables. Design contract in [`docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../specs/2026-07-09-sprint-14-evidence-design.md).

**Tech Stack:** Python (evidence parsers — matches Sprint 10 Spark notebooks + Sprint 13 agent-host recommendation), YAML (BOM + region-availability catalogs), GitHub Actions workflow, Fabric notebooks (PySpark), Fabric semantic model (TMDL edits), React + TypeScript (5 whiteboard card types + Evidence Backstage tab), Playwright (E2E provenance).

---

## Prerequisites (verify before starting)

- [ ] On `main`, clean: `git switch main; git pull`.
- [ ] Sprint 14 design spec merged at v1.0.0.
- [ ] **Sprint 13 T3** (whiteboard framework in `apps/hcc-app-fluent/src/whiteboard/`) merged — blocks T5. Track via issue #161.
- [ ] **Sprint 13 T4** (Backstage router in `apps/hcc-app-fluent/src/workspaces/backstage/`) merged — blocks T6. Track via issue #161.
- [ ] **Sprint 10** medallion pattern (Bronze / Silver / Gold layout + naming) — reference for T3. `docs/superpowers/specs/2026-07-08-sprint-10-completion-strategy.md`.
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active** (needed for T3 pipeline + T4 semantic model publish).
- [ ] Fabric workspace `ws-ihzhhpf-sit-data` (id `f3af9733-9503-4e92-98f9-a901d96f1c87`) + lakehouse `lh_ihzhhpf_sit` (id `30594c20-46ba-40ea-91fa-4701b105e0b9`) reachable.
- [ ] `az` CLI authenticated to SIT tenant per ADR-0012.
- [ ] Python 3.11+ available (parser dev + notebook local test).
- [ ] `gh` CLI authenticated.
- [ ] Explicit go-ahead from @urruegg in the Sprint 14 kickoff issue thread.

---

## File Structure

Files created or modified across the seven tasks.

### T1 — Evidence parsers + publish workflow

- Create: `scripts/evidence/parsers/{prd_parser,adr_parser,bom_parser,region_availability_parser,infra_parser}.py`.
- Create: `scripts/evidence/parsers/__init__.py` — module init.
- Create: `scripts/evidence/publish.py` — orchestrator that runs all parsers and writes to `data/evidence/*.json`.
- Create: `scripts/evidence/pyproject.toml` — parser package definition + dev dependencies (`pytest`, `ruamel.yaml`, `pyyaml`, `jsonschema`).
- Create: `scripts/evidence/tests/fixtures/` — golden inputs (small PRD slice, sample ADR, sample BOM, sample region-availability).
- Create: `scripts/evidence/tests/{test_prd_parser,test_adr_parser,test_bom_parser,test_region_parser,test_infra_parser,test_publish_orchestrator}.py`.
- Create: `data/evidence/schema/{requirements,adrs,req_adr_map,bom,dependencies,region_availability,deployed_bom}.schema.json` — JSON Schema per output file.
- Create: `.github/workflows/evidence-publish.yml` — on push to `main` (paths filter), run parsers, commit outputs to `evidence-latest` branch.
- Create: `scripts/evidence/README.md`.
- Modify: `.github/CODEOWNERS` — add `/scripts/evidence/`, `/data/evidence/**` → @urruegg.

### T2 — Seed catalogs (BOM + region-availability)

- Create: `docs/bom.yaml` — 25 BOM items per design spec §2.1 (from anchor idea §6).
- Create: `docs/region-availability.yaml` — GA / Preview / Not-available facts per resource × region with `verifiedBy` + `asOf`.
- Create: `docs/adr-requirement-map.yaml` — 10 ADR-requirement seed rows per design spec §2.1 (from anchor idea §8.1). May instead live inside ADR front-matter; T2 kickoff picks the shape.
- Create: `docs/bom.schema.md` — human-readable BOM contract doc. Cross-reference with the JSON schema from T1.
- Create: `.github/ISSUE_TEMPLATE/bom-item.yml` — issue template for adding/updating BOM entries.
- Create: `.github/ISSUE_TEMPLATE/ga-evidence-refresh.yml` — issue template for refreshing GA facts.
- Modify: `.github/CODEOWNERS` — add `/docs/bom.yaml`, `/docs/region-availability.yaml`, `/docs/adr-requirement-map.yaml` → @urruegg.
- Create: labels via `gh label create` — `evidence`, `bom`, `ga-refresh`, `readiness-rules`.

### T3 — Fabric medallion pipeline (Bronze → Silver → Gold + readiness scoring)

- Create: `data-platform/notebooks/evidence/{ingest_bronze,build_silver,build_gold_facts,build_gold_dims,score_readiness}.py` — five notebooks per medallion layer.
- Create: `data-platform/scripts/evidence/deploy-pipeline.ps1` OR `deploy-pipeline.py` — orchestrator that publishes all 5 notebooks + wires the Fabric pipeline schedule.
- Create: `data-platform/notebooks/evidence/README.md` — pipeline overview, invariants.
- Create: `data-platform/notebooks/evidence/tests/` — small pytest suite for pure scoring functions.
- Create: `docs/adr/00XX-readiness-scoring-rules.md` — codifies the T-SHOW / T-PROD rules from design spec §6 as an ADR.
- Create: `docs/data-platform/evidence-gold-schema.md` — Gold star schema doc.

### T4 — Direct Lake semantic model + measures

- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/` — extend the existing PBIP model with:
  - Evidence dimensions (`Dim_Resource`, `Dim_Region`, `Dim_Track`, `Dim_MaturityStatus`, `Dim_Requirement`, `Dim_ADR`, `Dim_Environment`, `Dim_Date`).
  - Evidence facts (`Fact_AvailabilityEvidence`, `Fact_BOMDeployment`, `Fact_ReadinessSnapshot`).
  - Bridge tables (`Bridge_Resource_Dependency`, `Bridge_Requirement_Resource`, `Bridge_Requirement_ADR`).
  - Measures: `Readiness % (T-SHOW)`, `Readiness % (T-PROD)`, `GA-Parity Gap`, `BOM count`, `Blocked requirements count`.
- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/definition/relationships.tmdl` — add relationships per star schema.
- Create OR modify: RLS role definitions if evidence-side RLS is required (design spec §4 shows presenter roles — check whether Guest role needs a scoped view).
- Create: `data-platform/reports/capacity-dashboard.SemanticModel/README-evidence.md` — evidence-side authoring notes.
- Create: `data-platform/reports/tests/evidence-measure-tests.md` — DAX test queries.

### T5 — Presenter whiteboard 5-card catalog (reuses Sprint 13 framework)

- Create: `apps/hcc-app-fluent/src/cards/evidence/{BomCard,AdrCard,PrdRequirementCard,GaEvidenceCard,DependencyEdge}.tsx` — 5 new card types.
- Modify: `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` — register 5 evidence card types.
- Create: `apps/hcc-app-fluent/src/data/evidence/{useBomList,useAdrList,useRequirementList,useGaEvidence,useDependencies}.ts` — SWR/React Query hooks that call the Fabric semantic model (via the same DAX-over-XMLA pattern the operational whiteboard uses).
- Create: `apps/hcc-app-fluent/tests/unit/cards/evidence/*.test.tsx` — one per card type. Every card MUST render provenance (`sourceUrl` + `asOf`); missing provenance MUST fail the render.

### T6 — Backstage Evidence tab wiring + E2E provenance test

- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageRouter.tsx` — add `/backstage/evidence` route.
- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/EvidenceTab.tsx` — hosts the presenter whiteboard using the framework + evidence card registry.
- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/preset-layouts.ts` — 1–2 preset presenter layouts ("CH North × T-SHOW", "GA-parity view").
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/Sidebar.tsx` — add "Evidence" nav entry.
- Create: `apps/hcc-app-fluent/tests/e2e/backstage-evidence.spec.ts` — Playwright: sign in as `demo.guest` → nav to Evidence tab → assert ≥25 BOM cards + ≥10 ADR cards + ≥1 PRD-req card + dependency edges + every card has `sourceUrl` + `asOf`.
- Create: `apps/hcc-app-fluent/tests/e2e/backstage-evidence-provenance.spec.ts` — provenance-check regression per design spec §10.

### T7 — Retro + checkpoint matrix

- Update: `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 14 row.
- Update: `docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md` — mark DoD items complete; bump MINOR.
- Close: Sprint 14 kickoff issue with retro comment.

### Cross-cutting

- Modify: `AGENTS.md` — if T3 introduces a new agent (e.g., `evidence-publisher`), add a registry row. Expected: no new agents in Sprint 14; T3 is workflow-only.

---

## Common per-task workflow (referenced by T1–T7)

Every task PR follows this skeleton.

- [ ] **Sub-step A: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-14/T<N>-<slug>
```

- [ ] **Sub-step B: Read the design spec section for this task**

Open [`docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../specs/2026-07-09-sprint-14-evidence-design.md) and the referenced anchor idea `docs/superpowers/ideas/SwissHospitalPlatformShowcaseEvidence.md` for the § most relevant to the task.

- [ ] **Sub-step C: TDD — write the failing test first**

Every code change starts with a failing unit test, Playwright spec, or notebook assertion. For Fabric pipeline changes, use small local pytest suites for pure functions + a lakehouse smoke run for the full path.

- [ ] **Sub-step D: Implement minimal code to pass the test**

Prefer smaller files with one clear responsibility.

- [ ] **Sub-step E: Run the full task-level test suite**

```powershell
# Parsers
cd scripts/evidence; pytest tests/; cd ../..

# Notebooks (pure functions)
cd data-platform/notebooks/evidence; pytest tests/; cd ../../..

# App (Sprint 13 workflows still apply)
cd apps/hcc-app-fluent; npm test; npm run test:e2e; cd ../..
```

- [ ] **Sub-step F: For `deploy`-ceiling steps — post `what-if` + wait for `approved-to-apply`**

Applies to T3 (Fabric pipeline publish) and T4 (semantic model publish). Post the deployment-summary as a PR comment; @urruegg posts `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete); only then does the apply run.

- [ ] **Sub-step G: Commit + push + open PR**

```powershell
git add scripts/ data/ data-platform/ apps/ docs/ .github/
git commit -m "feat(evidence): T<N> <slug> — <headline>"
git push -u origin sprint-14/T<N>-<slug>
gh pr create --base main --head sprint-14/T<N>-<slug> --title "feat(evidence): T<N> <slug>" --body-file <path> --label sprint-14 --label superpowers-execute
```

PR body follows [copilot-instructions.md §6](../../../.github/copilot-instructions.md) Output Contract.

- [ ] **Sub-step H: Wait for review + merge**

Merge unblocks the dependent tasks.

---

## Task 1 — T1: Evidence parsers + publish workflow

**Branch:** `sprint-14/T1-parsers-publish`  
**Depends on:** (none — can start immediately)

### Step 1.1 — Scaffold parser package + JSON Schemas

- [ ] **Step 1.1.1: Branch + init.**

```powershell
git switch main; git pull; git switch -c sprint-14/T1-parsers-publish
mkdir scripts/evidence, data/evidence/schema
cd scripts/evidence
# create pyproject.toml with pytest, ruamel.yaml, pyyaml, jsonschema
```

- [ ] **Step 1.1.2: Write JSON Schema for each output** (7 schemas: `requirements`, `adrs`, `req_adr_map`, `bom`, `dependencies`, `region_availability`, `deployed_bom`).

- [ ] **Step 1.1.3: Write failing tests** in `scripts/evidence/tests/` — each parser test reads a golden fixture from `tests/fixtures/` and asserts:
  - Parser output validates against the JSON Schema.
  - Byte-stable output for stable input (no map ordering flakes — sort keys before JSON dump).
  - Provenance fields (`sourcePath`, `sourceCommit`, `asOf`, `sourceUrl` where applicable) present on every record.

### Step 1.2 — Implement parsers one at a time (TDD loop)

- [ ] **Step 1.2.1: `prd_parser.py`** — extracts every `FR-*` / `NFR-*` from `docs/PRD.md` §7 traceability matrix + narrative sections. Output row shape: `{id, family, title, mvp, sourcePath, sourceLine, sourceCommit}`.
- [ ] **Step 1.2.2: `adr_parser.py`** — extracts every ADR from `docs/adr/*.md`. Front-matter parsing for `Status`, cross-links for `Supersedes` / `Superseded by`. Output: `{id, title, status, decisionSummary, sourcePath, sourceCommit}` + separate `req_adr_map.json` for governed requirements (from ADR front-matter or a dedicated map file per T2 decision).
- [ ] **Step 1.2.3: `bom_parser.py`** — reads `docs/bom.yaml` (T2 seeds this) and emits `bom.json` + `dependencies.json`. Validates against `bom.schema.json`.
- [ ] **Step 1.2.4: `region_availability_parser.py`** — reads `docs/region-availability.yaml` and emits `region_availability.json`. Requires `verifiedBy` + `asOf` on every fact.
- [ ] **Step 1.2.5: `infra_parser.py`** — walks `infra/**` and produces a lightweight `infra_snapshot.json` mapping resource IDs → module paths (for later cross-checking against `deployed_bom.json`). Full ARG-based deployed BOM is out-of-scope per design spec §2.2; leave a stub.
- [ ] **Step 1.2.6: `publish.py` orchestrator** — invokes all parsers, writes to `data/evidence/*.json` in the working tree.

### Step 1.3 — Publish workflow

- [ ] **Step 1.3.1: Create `.github/workflows/evidence-publish.yml`** — triggers:
  - `push` to `main` on paths: `docs/PRD.md`, `docs/adr/**`, `docs/bom.yaml`, `docs/region-availability.yaml`, `docs/adr-requirement-map.yaml`, `infra/**`, `scripts/evidence/**`.
  - `workflow_dispatch` for manual runs.
- [ ] **Step 1.3.2: Workflow steps** — checkout, setup Python, install parser package, run `python -m scripts.evidence.publish`, commit to `evidence-latest` branch (force-push allowed — this branch is intentionally rewound per push).
- [ ] **Step 1.3.3: Explicitly do NOT** merge evidence JSON into `main` (design spec §11 risks — bloat).

### Step 1.4 — PR

- [ ] Commit, push, open PR (Sub-step G). Label `sprint-14`, `evidence`, `superpowers-execute`, `documentation`.

**DoD:**
- [ ] All parser unit tests green.
- [ ] `evidence-publish.yml` runs successfully on the PR (uses `workflow_dispatch`) and pushes to `evidence-latest`.
- [ ] `data/evidence/*.json` output validates against every JSON Schema.
- [ ] Every record has provenance.

---

## Task 2 — T2: Seed catalogs (BOM + region-availability + ADR map)

**Branch:** `sprint-14/T2-seed-catalogs`  
**Depends on:** T1 merged (parsers must validate the shapes).

Follow the [Common per-task workflow](#common-per-task-workflow-referenced-by-t1t7). Task-specific specifics:

- Draft `docs/bom.yaml` with the 25 BOM items from the anchor idea §6 seed catalog. Each item: `id`, `name`, `type`, `category`, `sku`, `sovereigntyClass` (regional / global), `dependencies[]`, `realizesRequirements[]`, `governingAdrs[]`, `sourcePath`, `notes`.
- Draft `docs/region-availability.yaml` with GA / Preview / Not-available facts for each of the 25 BOM items × { Switzerland North, West Europe }. Every fact carries `verifiedBy` (human handle or "Microsoft Learn URL") + `asOf`.
- Draft `docs/adr-requirement-map.yaml` — 10 seed rows from anchor idea §8.1 mapping `{adr, requirements[], resources[]}`. **T2 kickoff decides:** live in `adr-requirement-map.yaml` (one file) OR in ADR front-matter (`Governs: [FR-XY-001, FR-XY-002]`). Recommend the standalone file for now — less merge friction.
- Create issue templates `bom-item.yml` and `ga-evidence-refresh.yml`.
- Create labels `evidence`, `bom`, `ga-refresh`, `readiness-rules`.
- Add CODEOWNERS entries.

**Tests:**
- Run the T1 parsers against the new seed files — expect clean pass.
- CI evidence-publish workflow re-runs on the seed-catalog PR and produces a first real `data/evidence/*.json` snapshot on the `evidence-latest` branch.

**DoD:**
- [ ] `docs/bom.yaml` has 25 BOM items validating against the schema.
- [ ] `docs/region-availability.yaml` has facts for every BOM × {CH North, West Europe} with `verifiedBy` + `asOf`.
- [ ] `docs/adr-requirement-map.yaml` has 10 mapping rows.
- [ ] Issue templates + labels + CODEOWNERS entries live on `main`.
- [ ] Evidence-publish workflow runs cleanly on this PR.

---

## Task 3 — T3: Fabric medallion pipeline

**Branch:** `sprint-14/T3-fabric-medallion`  
**Depends on:** T2 merged (needs real evidence JSON on the `evidence-latest` branch).

### Step 3.1 — Bronze notebook

- [ ] **Step 3.1.1: Write `ingest_bronze.py`** — reads all files from the `evidence-latest` branch (or OneLake shortcut into it) and lands raw JSON into `Bronze.evidence_raw_*` tables. Naming convention matches Sprint 10 medallion. Per-load audit columns: `_ingest_utc`, `_source_commit`.
- [ ] **Step 3.1.2: Notebook test** — small pytest that runs the transformation on a sample fixture and asserts row count + column shape.

### Step 3.2 — Silver notebooks

- [ ] **Step 3.2.1: Write `build_silver.py`** — typed Silver tables: `Silver.requirements`, `Silver.adrs`, `Silver.req_adr_map`, `Silver.bom`, `Silver.dependencies`, `Silver.region_availability`. Provenance columns preserved.
- [ ] **Step 3.2.2: Notebook test** — assertions on data types, non-null contracts, and provenance-column presence.

### Step 3.3 — Gold star schema

- [ ] **Step 3.3.1: Write `build_gold_dims.py`** — populates all dimensions per design spec §3 (list expanded from anchor idea §5.1).
- [ ] **Step 3.3.2: Write `build_gold_facts.py`** — populates the 3 facts + 3 bridge tables per design spec §3 (list expanded from anchor idea §5.2).
- [ ] **Step 3.3.3: Naming: snake_case + gold-schema prefix** matches Sprint 10 convention (per PR #153 reconciliation). E.g., `gold.dim_resource`, `gold.fact_readiness_snapshot`.

### Step 3.4 — Readiness scoring

- [ ] **Step 3.4.1: Codify T-SHOW / T-PROD rules as ADR** at `docs/adr/00XX-readiness-scoring-rules.md` (Accepted). Reference design spec §6.
- [ ] **Step 3.4.2: Write `score_readiness.py`** — pure functions for the T-SHOW and T-PROD rules; regression fixture in `data-platform/notebooks/evidence/tests/fixtures/readiness_golden/` with byte-stable output assertion.
- [ ] **Step 3.4.3: Materialise `gold.fact_readiness_snapshot`** with one row per (`resource_id`, `region_id`, `track_id`, `date_id`).

### Step 3.5 — Pipeline orchestration + deploy

- [ ] **Step 3.5.1: Write `data-platform/scripts/evidence/deploy-pipeline.py`** — publishes all 5 notebooks to `ws-ihzhhpf-sit-data` and wires them into a Fabric pipeline scheduled daily (schedule matches Sprint 10 pattern).
- [ ] **Step 3.5.2: Dry-run via `what-if`-equivalent** — the script has a `--plan` mode that prints planned changes without executing.
- [ ] **Step 3.5.3: Post plan as PR comment; wait for `approved-to-apply`; apply.**

**DoD:**
- [ ] All 5 notebooks live in `data-platform/notebooks/evidence/` with pytest passing.
- [ ] Readiness-rules ADR merged.
- [ ] Fabric pipeline published to SIT and one successful end-to-end run completes.
- [ ] Gold tables populated for CH North × T-SHOW slice at minimum.
- [ ] Readiness golden fixture regression test green.

---

## Task 4 — T4: Direct Lake semantic model + measures

**Branch:** `sprint-14/T4-semantic-model`  
**Depends on:** T3 merged (Gold tables must exist).

Follow the [Common per-task workflow](#common-per-task-workflow-referenced-by-t1t7). Task-specific specifics:

- Extend the existing PBIP semantic model (`data-platform/reports/capacity-dashboard.SemanticModel/`) with evidence dimensions, facts, bridges, and relationships per design spec §3.
- Add measures: `Readiness % (T-SHOW)`, `Readiness % (T-PROD)`, `GA-Parity Gap`, `BOM count`, `Blocked requirements count`.
- Decide (task kickoff) whether evidence-side RLS is needed for the `Guest` presenter role (design spec §4 hints yes). If yes, add RLS role and matching filter DAX; if no, document why in the PR.
- Publish semantic model to `ws-ihzhhpf-sit-data`. Uses the `powerbi-optimization` + `fabric-semantic-model-authoring` skills.

**Deploy gate:** semantic model publish is `deploy`-ceiling. `approved-to-apply` required.

**Tests:**
- DAX test queries in `evidence-measure-tests.md` executed via the semantic-model MCP or via a Fabric REST call — each measure returns expected value on a fixed input.
- Direct Lake fallback test — measure works even if the lakehouse is under refresh.

**DoD:**
- [ ] Semantic model has evidence dims + facts + bridges + relationships wired.
- [ ] All 5 measures return expected values on golden inputs.
- [ ] Model published to SIT.
- [ ] RLS decision documented (implemented or explicitly deferred).

---

## Task 5 — T5: Presenter whiteboard 5-card catalog

**Branch:** `sprint-14/T5-evidence-cards`  
**Depends on:** T4 merged (measures for card content). **Sprint 13 T3 merged** (whiteboard framework exists).

- Add 5 card types under `apps/hcc-app-fluent/src/cards/evidence/`:
  - `BomCard.tsx` — resource name + type + region availability chip + dependency count. Drill-in panel shows dependencies + realising requirements + governing ADRs.
  - `AdrCard.tsx` — ADR id + title + status + one-line decision. Drill-in: full decision + governed requirements + affected BOM.
  - `PrdRequirementCard.tsx` — req id + family + title + MVP flag + readiness chips per track/region. Drill-in: governing ADR(s) + realising BOM item(s) + score.
  - `GaEvidenceCard.tsx` — resource × region chip (GA / Preview / Not available) + `asOf`. Drill-in: `sourceUrl` + `verifiedBy` + history.
  - `DependencyEdge.tsx` — directed edge with type (`requires`, `hosts`, `grounds`, `binds`, `governs`).
- Register the 5 card types in the Sprint 13 whiteboard `CardRegistry` — extension not fork.
- **Provenance is contract:** every card MUST render `sourceUrl` + `asOf`. Card render MUST fail (visible error state, not silent) if either is missing. Unit tests enforce.
- Data hooks under `apps/hcc-app-fluent/src/data/evidence/` — same DAX-over-XMLA pattern the operational whiteboard uses (or Direct Lake REST — depends on Sprint 13 T6's chosen pattern).
- Reuse: Helvion theme tokens from Sprint 13 T1.

**Tests:**
- Unit tests per card — happy path + missing-provenance failure path.
- Storybook or equivalent visual regression (optional; nice-to-have).

**DoD:**
- [ ] All 5 card types + edge render with provenance.
- [ ] Cards registered in `CardRegistry.tsx`.
- [ ] Unit tests green including the missing-provenance failure path.

---

## Task 6 — T6: Backstage Evidence tab wiring + E2E

**Branch:** `sprint-14/T6-backstage-evidence-tab`  
**Depends on:** T5 merged. **Sprint 13 T4 merged** (Backstage router exists).

- Add `/backstage/evidence` route in `BackstageRouter.tsx`.
- Create `EvidenceTab.tsx` — composes the whiteboard framework with the evidence card registry.
- Add 1–2 preset presenter layouts (`preset-layouts.ts`): "CH North × T-SHOW", "GA-parity view".
- Add "Evidence" nav entry in the Backstage sidebar (visible to `HCC.Presenter`, `HCC.PlatformAdmin`, `HCC.OntologySteward`, `HCC.Auditor`, `HCC.GuestReadOnly`).
- Playwright E2E test: sign in as `demo.guest` → nav Evidence → assert layout renders ≥25 BOM + ≥10 ADR + ≥1 PRD-req cards with dependency edges. Assert every rendered card has `sourceUrl` + `asOf`.
- Playwright provenance regression: assert that a mocked card with missing provenance renders the error state (unit-level assurance repeated at E2E level).

**DoD:**
- [ ] Evidence tab visible in Backstage for the intended roles.
- [ ] Preset layout loads and renders the whole card catalog.
- [ ] E2E provenance regression green.

---

## Task 7 — T7: Retro + checkpoint matrix

**Branch:** `sprint-14/T7-retro`  
**Depends on:** T6 merged.

- Update `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 14 row.
- Update `docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md` — mark DoD complete + bump MINOR.
- Close Sprint 14 kickoff issue with retro comment.

**DoD:**
- [ ] Checkpoint matrix entry landed.
- [ ] Design spec DoD checked off.
- [ ] Kickoff issue closed.

---

## Definition of Sprint 14 done (mirrors design spec §13)

- [ ] `evidence-publish.yml` runs on push and produces `data/evidence/*.json` on `evidence-latest` branch.
- [ ] Fabric medallion pipeline populated end-to-end from ≥1 publish cycle.
- [ ] Semantic model returns `readiness score per BOM item × region × track` for Switzerland North × T-SHOW.
- [ ] Backstage → Evidence tab renders the presenter whiteboard with ≥25 BOM cards + ≥10 ADR cards + ≥1 PRD-requirement card + dependency edges.
- [ ] Provenance visible on every card (`sourceUrl`, `asOf`); missing provenance fails render.
- [ ] Golden readiness-rule regression test green.
- [ ] Sprint 14 retro entry in [`docs/sprints/superpowers-checkpoint-matrix.md`](../../sprints/superpowers-checkpoint-matrix.md).

---

## Parallelism map (for the cloud coding agent's subagent scheduling)

```text
T1 (parsers + workflow) ──▶ T2 (seed catalogs) ──▶ T3 (Fabric medallion) ──▶ T4 (semantic model) ──▶ T5 (cards) ──▶ T6 (Backstage tab) ──▶ T7 (retro)
                                                                                     
Sprint 13 T3 (whiteboard framework) ────────────────────────────────────────┘         
Sprint 13 T4 (Backstage router) ─────────────────────────────────────────────────────────────┘
```

Sprint 14 is **largely sequential** (each layer depends on the one before). The two Sprint 13 dependencies fan in at T5 / T6 respectively.

**Fast-start options:**
- T1 can start immediately (no Sprint 14 deps; no Sprint 13 deps).
- T2 can start in parallel with T1's final PR polish once the schemas are settled — but T2's final CI green requires T1 merged. Recommend serial.
- T5 can start speculatively against mocked measure outputs once Sprint 13 T3 lands, but real T5 completion needs T4.

**Sprint 13 dependencies flagged (per task):**
- T5 blocks on Sprint 13 T3 (whiteboard framework in `apps/hcc-app-fluent/src/whiteboard/`).
- T6 blocks on Sprint 13 T4 (Backstage router in `apps/hcc-app-fluent/src/workspaces/backstage/`).

If Sprint 13 stalls on T3 / T4, the fallback per design spec §11 is: ship T1–T4 pipeline + data model first; ship T5–T6 whiteboard in a follow-up mini-sprint.

---

## Self-Review

**1. Spec coverage.** Every Sprint 14 design-spec §13 DoD bullet maps to a task:
- `evidence-publish.yml` + `data/evidence/*.json` → T1 + T2.
- Fabric medallion → T3.
- Semantic model readiness measure → T4.
- Backstage Evidence tab with 25 BOM + 10 ADR + 1 PRD card + edges → T5 + T6.
- Provenance on every card → enforced in T5 unit tests and T6 E2E.
- Golden readiness-rule test → T3.
- Retro entry → T7.

**2. Placeholder scan.** No `TBD` / `TODO`. Deliberate parametrics: `<N>`, `<slug>`, ADR number `00XX` (assigned at ADR creation). Two decisions deferred to task kickoffs with explicit exit criteria (T2 ADR-req map file vs front-matter; T4 evidence-side RLS yes/no).

**3. Type consistency.** Paths: `scripts/evidence/`, `data/evidence/`, `data-platform/notebooks/evidence/`, `data-platform/reports/capacity-dashboard.SemanticModel/`, `apps/hcc-app-fluent/src/cards/evidence/`, `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/`. Branch prefix `sprint-14/T<N>-<slug>`.

**4. Approval gates.** T3 (Fabric pipeline publish) + T4 (semantic model publish) each carry one `approved-to-apply` gate. Total Sprint 14 SIT gates: **~2**.

**5. Dependencies clean.** Sequential T1 → T2 → T3 → T4 → T5 → T6 → T7. Two external fan-ins from Sprint 13 (T3 → T5, T4 → T6). No cycles. Fallback documented if Sprint 13 stalls.

**6. Provenance is a contract.** Enforced at three layers: parser tests (T1), card unit tests (T5), Backstage E2E (T6). Any drift breaks the pipeline visibly.

---

## Execution Handoff

Plan complete and will be saved to `docs/superpowers/plans/2026-07-09-sprint-14-evidence-plan.md`. Two execution options:

1. **GitHub Copilot cloud coding agent (recommended)** — matches Sprint 11 / 12 / 13 pattern. Assign the accompanying kickoff issue to Copilot in the GitHub UI. The cloud agent authors T1–T7 as separate PRs, respecting the largely-sequential dependency chain.
2. **Inline execution here** — the chat session executes one task at a time.

**Which approach?** — my recommendation is the cloud agent again (proven three times: PR #149, #152, #156 + Sprint 13 in flight).
