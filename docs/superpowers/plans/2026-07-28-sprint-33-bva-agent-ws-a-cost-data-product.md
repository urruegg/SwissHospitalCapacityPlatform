# Sprint 33 — Curavias BVA Agent — Plan 2: WS-A cost/BOM data product

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 — Curavias BVA Agent |
| **Issue** | [#489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489) (tracker); [#517](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/517) (WS-A) |

> **For agentic workers:** REQUIRED SUB-SKILL — use `superpowers:subagent-driven-development` (fresh subagent + spec review + quality review per task) with `superpowers:test-driven-development`. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build the **master-data-via-file** BVA cost data product: git-owned,
CI-gated CSVs under `data/master-data/bva/` → a pure, unit-tested transform that
produces the Gold `bva_*` cost tables and the `sm_bva` baseline measures, all
CHF-normalized per the frozen WS-G0 cost-basis contract. Every baseline aggregate
reconciles **exactly** to the `docs/BVA.md` ROM (one-time `1,300,000` CHF, annual
run `1,250,000` CHF, 3 hospitals) so the WS-B engine's provisional
`archetypes.py` constants can later be sourced from `sm_bva` without changing the
`bva.simulate` contract.

**Architecture:** Reuse the master-data pattern
([`data/master-data/README.md`](../../../data/master-data/README.md)): CSVs are
the golden source loaded **identically in SIT and PROD**; a dependency-free
validator gates PK/FK/no-PHI/CHF; the transform logic lives in a pure,
framework-agnostic module (mirroring
[`data-platform/notebooks/bva/bva_transforms.py`](../../../data-platform/notebooks/bva/bva_transforms.py))
so it is unit-testable with byte-stable fixtures, with the Fabric notebook a thin
I/O wrapper. This is a **new, additive** cost data product; it does not modify the
Sprint 15 BVA consumption/value-realization product (`gold.bva_fact_*`), and
`sm_bva` is a new semantic model name (no collision).

**Tech stack:** Python 3 stdlib only (+ `jsonschema` in tests where a schema is
asserted), `pytest`/`unittest`. Interpreter `python` (not `python3`). CSV +
Markdown.

**Out of scope (this plan does NOT):**

- Run live Fabric loads, publish the `sm_bva` Direct Lake semantic model, or wire
  ontology / Fabric IQ Data Agent grounding. Those are `deploy`-ceiling actions
  **gated by `approved-to-apply`** (AGENTS.md §4) and are captured as a separate
  gated follow-on (Task A5, plan-only here).
- Edit `AGENTS.md`, `docs/PRD.md`, `docs/adr/`, or `.github/copilot/mcp.json`
  (governance close-out already merged in #515).
- Modify the WS-B engine, the frozen WS-G0 schemas, or the Sprint 15 notebooks.

---

## Frozen inputs (do NOT redefine)

- Cost-basis contract §4 of
  [`2026-07-28-sprint-33-bva-agent-contracts.md`](../specs/2026-07-28-sprint-33-bva-agent-contracts.md):
  `teamCostChf = copilotCostChf + (humanElectiveHours * configuredRoleRateChf)`;
  USD→CHF only via the explicit `bva_fx_rate.csv` line; settling weeks
  `provisional`.
- ROM baseline from [`docs/BVA.md`](../../../docs/BVA.md) §"ROM Cost Model":
  one-time `1,300,000` CHF (5 elements), annual run `1,250,000` CHF (4 elements),
  3-year TCO `5,050,000`.
- WS-B baseline shape (`data-platform/bva/models.py::BvaBaseline`):
  `totalCostChf`, `oneTimeChf`, `annualRunChf`, `hospitals`, `asOf`, `sourceRef`.

## Source CSVs — `data/master-data/bva/` (Task A1)

| File | Grain / columns | Reconciles to |
| ---- | --------------- | ------------- |
| `bva_cost_element.csv` | `element_id,cost_type,element_name,amount_chf,driver_source` | **Authoritative ROM ledger** — 5 `one_time` + 4 `annual_run` rows summing to `1,300,000` / `1,250,000`; `driver_source` links each element to its drill-down CSV |
| `bva_bom.csv` | `resource_type,resource_group,env,resource_id` | BOM inventory (SIT+PROD parity) |
| `bva_azure_cost_weekly.csv` | `service_name,resource_group,resource_id,iso_week,cost_usd` | drill-down evidence for the `760,000`/yr Azure run element (USD, FX-converted) |
| `bva_copilot_usage_weekly.csv` | `iso_week,aiu,tokens_in,tokens_out,cost_usd` | Copilot component drill-down of team cost |
| `bva_team_effort.csv` | `role,iso_week,elective_hours,role_rate_chf` | human elective build effort (CHF) drill-down for the `640,000` build element |
| `bva_fx_rate.csv` | `period,usd_to_chf` | explicit FX line |
| `bva_hospital_profile.csv` | `tenant_id,hospital_name,beds,occupancy_target,archetype` | 3 hospitals; FK to `dim_tenant` |

**Reconciliation contract:** `bva_baseline_kpi` derives `oneTimeChf` /
`annualRunChf` **solely by summing `bva_cost_element.csv`** grouped by
`cost_type` (the single source of the ROM figures — exact, byte-stable). The
weekly/effort/FX CSVs are **supporting drill-down evidence** that feed
`bva_cost_fact` / `bva_effort_fact`; the transform asserts their FX-converted
roll-ups sit within the ±30% ROM band of the ledger element they support (a
soft consistency gate, not the baseline source). All values synthetic/anonymized,
no PHI (ADR-0013, ADR-0016). Hospital names ASCII.

## Gold outputs — pure transform (Task A2)

`data-platform/bva/costbasis.py` (pure, no I/O) exposes deterministic functions
producing:

- `bva_bom_dim` — one row per BOM resource.
- `bva_cost_fact` — CHF-normalized Azure + copilot cost by ISO week (FX applied).
- `bva_effort_fact` — CHF team effort by role/week.
- `bva_hospital_profile_dim` — the 3 hospitals with archetype drivers.
- `bva_baseline_kpi` — the reconciled baseline: `oneTimeChf`, `annualRunChf`,
  `totalCostChf`, `hospitals`, `costPerBedChf`, `costPerHospitalChf`,
  `costPerForecastRunChf`, each with `asOf` + `sourceRef` provenance.

`sm_bva` baseline **measures** (total cost CHF, one-time vs run split,
cost-per-bed, cost-per-hospital, cost-per-forecast-run) are documented as a
measure catalog in `docs/data-platform/bva-cost-gold-schema.md` (Task A4); the
values equal the `bva_baseline_kpi` aggregates.

---

## Tasks

- [ ] **A1 — master-data CSVs + validator** — create the 7 CSVs (incl. the
  `bva_cost_element.csv` ROM ledger); extend
  `data/master-data/validate_master_data.py` (add a `bva` domain check) for
  file presence, PK uniqueness, FK to `dim_tenant`, no-PHI, the CHF/FX
  contract, and the ledger-sums-to-ROM invariant; add a test under
  `data/master-data/tests/`. TDD: validator test first.
- [ ] **A2 — pure cost-basis transform + unit tests** — `data-platform/bva/costbasis.py`
  producing the 5 Gold tables + `bva_baseline_kpi`; byte-stable fixture tests
  under `data-platform/bva/tests/` asserting the reconciliation
  (one-time=1,300,000; run=1,250,000; hospitals=3) and CHF/FX correctness. TDD.
- [ ] **A3 — Fabric notebook wrapper (thin I/O, not run here)** — `data-platform/notebooks/bva/build_gold_bva_costbasis.py`
  reading `Files/master-data/bva/`, calling the pure transform, writing
  `gold.bva_*`; documented, no live run. Mirror the existing notebook I/O style.
- [ ] **A4 — measure catalog + schema doc** — `docs/data-platform/bva-cost-gold-schema.md`
  (gold tables + `sm_bva` measure definitions + Sprint-15 reconciliation note);
  update `data-platform/notebooks/bva/README.md`. Doc-authoring skill; version headers.
- [ ] **A5 — gated live-load plan (plan-only)** — document the `approved-to-apply`
  publish path (OneLake upload → medallion run → `sm_bva` Direct Lake publish →
  ontology/Data Agent grounding) + the `data-quality-agent` contract-check on
  `bva_*`; **no execution** in this PR. Record SIT+PROD parity method.
- [ ] **A6 — final review + PR** — full test run, doc gates, evidence-fixture
  regen if PRD/ADR touched (not expected), scope check, rebase on `main`, squash
  PR → tracker #489. Human merges.

## Definition of Done (WS-A repo slice)

- 7 CSVs present and green through the master-data validator + no-PHI gate;
  `bva_cost_element.csv` ledger sums to one-time `1,300,000` / run `1,250,000`.
- Pure transform reconciles to the ROM baseline exactly; byte-stable fixture
  tests pass.
- Gold schema + `sm_bva` measure catalog documented; Sprint-15 reconciliation
  noted; doc gates (mojibake + markdownlint) clean; doc versions bumped.
- Live Fabric publish + DQ contract-check documented as a gated follow-on (A5),
  not executed.
- Squash PR opened off latest `main`; **human-merged**; no infra apply beyond
  gated, `approved-to-apply` loads.
