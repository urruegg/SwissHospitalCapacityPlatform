# Sprint 33 — Curavias BVA Agent — Plan 3: WS-D Opportunity capture

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 — Curavias BVA Agent |
| **Issue** | [#489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489) (tracker); [#521](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/521) (WS-D) |

> **For agentic workers:** REQUIRED SUB-SKILL — `superpowers:subagent-driven-development`
> (fresh subagent + spec review + quality review per task) with
> `superpowers:test-driven-development`. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Capture every value/onboarding ask as an **`Opportunity`** document in
a Cosmos DB system-of-record (frozen `bva-opportunity-v1` contract), project it
**one-way** to a `gold.bva_opportunity` analytics table, and surface an
**opportunity-pipeline** view in the Curavias Backstage app. Agents never
auto-advance `status` past `qualified` (write ceiling).

**Architecture (mirror existing patterns):**

- **Cosmos SoR** — mirror [`data-platform/scripts/csa/_cosmos.py`](../../../data-platform/scripts/csa/_cosmos.py):
  env-driven `DefaultAzureCredential`, container-per-aggregate, `upsert_item`.
  Container `opportunities`, partition key `/hospitalName`; deterministic id
  `opp-<slug(hospitalName)>-0001` so re-asks update the same record (append to
  `history`, never fork).
- **Projection** — pure flatten (mirror
  [`data-platform/bva/costbasis.py`](../../../data-platform/bva/costbasis.py) /
  Sprint 15 `bva_transforms.py`): Cosmos docs → sorted `gold.bva_opportunity`
  rows + pipeline metrics (count by status, weighted ROI); thin Fabric notebook
  I/O wrapper. One-way; Cosmos stays the SoR (design R4).
- **App** — mirror [`apps/hcc-app-fluent/src/data/evidence/evidence-service.ts`](../../../apps/hcc-app-fluent/src/data/evidence/evidence-service.ts):
  a committed fixture + a data service + a Backstage widget; Vitest test. No live
  dependency in CI.

**Frozen inputs (do NOT redefine):**

- [`data/synthetic/schema/bva-opportunity-v1.schema.json`](../../../data/synthetic/schema/bva-opportunity-v1.schema.json)
  and the `Opportunity` prose contract §3 of
  [`2026-07-28-sprint-33-bva-agent-contracts.md`](../specs/2026-07-28-sprint-33-bva-agent-contracts.md).
- The lifecycle `new → evaluating → qualified / disqualified → onboarding → won / lost`.
- WS-A `bva_baseline_kpi` (the ROI basis) and the WS-B `BvaSimulationResult` snapshot shape.

**Out of scope (this plan does NOT):**

- Execute live Cosmos writes or publish `gold.bva_opportunity` Direct Lake.
  Those are `deploy`-ceiling, **gated by `approved-to-apply`** (AGENTS.md §4),
  documented in the gated-load plan. The repo slice is fully authorable + tested.
- Edit `AGENTS.md`, `docs/PRD.md`, `docs/adr/`, `.github/copilot/mcp.json`,
  the frozen WS-G0 schemas, or the WS-A/WS-B code.

## Tasks

- [ ] **D1 — validator + synthetic dataset** — dependency-free `Opportunity`
  record validator vs the frozen schema (mirror
  `evals/bva-agent/tests/test_bva_schema_conformance.py`); a synthetic
  multi-status opportunities dataset JSON (shared by D3 + D5); tests. TDD.
- [ ] **D2 — Cosmos Opportunity SoR** — `data-platform/bva/opportunity_store.py`:
  env-driven upsert, idempotent by hospital lineage, `append_history`,
  never-advance-past-`qualified` guard. Pure record-building + guard
  unit-tested; Cosmos I/O mocked. TDD.
- [ ] **D3 — Cosmos → gold projection** — pure `opportunity_projection.py` →
  `gold.bva_opportunity` rows + pipeline metrics (count by status, weighted ROI);
  thin notebook wrapper; byte-stable tests. TDD.
- [ ] **D4 — schema + gated-load doc** — `docs/data-platform/bva-opportunity-gold-schema.md`
  (gold schema + pipeline metric catalog); update
  `docs/data-platform/bva-cost-gated-load-plan.md` with the Cosmos container +
  `approved-to-apply` step. Version headers.
- [ ] **D5 — Backstage pipeline view** — `apps/hcc-app-fluent` opportunity-pipeline
  widget + data service reading the committed fixture; Vitest test.
- [ ] **D6 — final review + PR** — full test run, doc gates, scope check, rebase
  on `main`, squash PR → #521/#489. Human merges.

## Definition of Done (WS-D repo slice)

- Opportunity validator green against the frozen schema + synthetic dataset.
- Cosmos store upsert is idempotent by hospital lineage and refuses to advance
  past `qualified`; guard unit-tested.
- Projection reconciles pipeline metrics deterministically; byte-stable tests pass.
- Backstage opportunity-pipeline view renders from the committed fixture; Vitest green.
- Gold schema + gated-load path documented; doc gates clean; versions bumped.
- Squash PR opened off latest `main`; **human-merged**; live Cosmos/Direct Lake
  apply only via `approved-to-apply`.
