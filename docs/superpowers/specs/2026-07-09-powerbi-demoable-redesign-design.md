# Power BI Demoable Redesign — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |
| **Anchor artefact** | [data-platform/reports/capacity-dashboard.pbip](../../../data-platform/reports/capacity-dashboard.pbip) |
| **Brandkit** | [docs/brandkit/Helvion-Brand-Guide.md](../../brandkit/Helvion-Brand-Guide.md) |
| **Skill used** | [.github/skills/powerbi-report-authoring/SKILL.md](../../../.github/skills/powerbi-report-authoring/SKILL.md) |
| **Sprint 09 predecessor spec** | [docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md](2026-07-02-sprint-09-v2-refinement-design.md) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Target framing (T2 + M1 + H3)](#2-target-framing-t2--m1--h3)
3. [Persona catalog](#3-persona-catalog)
4. [Page architecture](#4-page-architecture)
5. [Component boundaries](#5-component-boundaries)
6. [Semantic model additions](#6-semantic-model-additions)
7. [RLS strategy (H3 hybrid)](#7-rls-strategy-h3-hybrid)
8. [Helvion theme mapping](#8-helvion-theme-mapping)
9. [Milestones M1–M6](#9-milestones-m1m6)
10. [Verification and demo script](#10-verification-and-demo-script)
11. [Risks and mitigations](#11-risks-and-mitigations)
12. [Definition of done](#12-definition-of-done)

---

## 1. Goal and desired end state

A single Power BI report (**capacity-dashboard v2**) that stands up as a T2 persona-anchored operational demo with C-level storytelling depth. When a **Bed Manager**, **OR Coordinator**, or **Ops Lead** persona opens the report:

- they land on their own page;
- headline KPIs are branded in **Helvion** ([docs/brandkit/Helvion-Brand-Guide.md](../../brandkit/Helvion-Brand-Guide.md));
- they can drill through and hover through the *why* without navigating a menu;
- hospital scope binds via H3 hybrid (hard RLS in PROD, soft slicer in SIT with an RLS-proof pill showing effective identity + selected hospital);
- every KPI shows its grounding chain (`FR-<id> • ADR-<nnnn> • hcp:<Entity>`);
- a hidden perf-benchmark page proves the hero scenario (cold load < 4s, warm interaction < 500ms).

---

## 2. Target framing (T2 + M1 + H3)

Locked in the 2026-07-09 brainstorm session:

| Dimension | Choice | Rationale |
| --- | --- | --- |
| Audience | **T2 — Persona-anchored operational demo** | Bed Manager + OR Coordinator live in the room |
| Delivery | **M1 — Live in Power BI (Desktop / Service)** | No external overlay; the report itself is the demo |
| Hospital scope | **H3 — Hybrid (hard PROD, soft SIT)** | Preserves both stories: RLS audit-ready + demo-time slicer flip |
| Scope size | **Approach C — Full narrative rebuild** | Includes small-multiples, field parameters, smart-narrative, grounding cards, perf-benchmark |
| Execution surface | **GitHub Copilot cloud coding agent** | Same delegation pattern as Sprint 11 kickoff issue #146 |
| Plan scope | **All 6 milestones in one plan** | Matches roadmap-then-plan pattern |

---

## 3. Persona catalog

Three primary personas. All others (Discharge Coordinator, ED Lead, Staffing Coordinator, Crisis Manager) are served via drill-throughs *within* these three views, not as separate landing pages.

| # | Persona | App role (Sprint 12) | Landing page | Primary questions answered |
| --- | --- | --- | --- | --- |
| 1 | **Bed Manager** | `HCC.BedManager` | `page-bed-manager` | Where is pressure now? Who can be discharged? What is the 72-h forecast? |
| 2 | **OR Coordinator** | `HCC.ORCoordinator` | `page-or-coordinator` | Which theatres are idle? What is cancellation risk? What is turnover trending? |
| 3 | **Ops Lead** (HCC / Operations Lead) | `HCC.OperationsLead` | `page-ops-lead` | Cross-cutting: capacity + OR + flow + escalation tier in one glance |

Demo-only identities anchor the landing page:

| Identity | Path through the report |
| --- | --- |
| `demo.guest` (`HCC.GuestReadOnly`) | Landing → aggregated-only view; cannot drill into any hospital-specific persona page |
| `sophie.meier` (`HCC.DemoOperator`) | Landing → any persona tile → soft slicer visible everywhere |
| `super.admin` (`HCC.SuperAdmin`) | Same as DemoOperator, plus perf-benchmark hidden page reachable via URL |

---

## 4. Page architecture

Six visible pages plus five hidden helper pages (tooltip + drill-through targets).

```
Visible pages (in navigation order):
  page-landing            (new)  — Helvion hero + 3 persona tiles + demo-mode banner + as-of pill
  page-bed-manager        (was page1-capacity)  — refined + discharge-candidate tile
  page-or-coordinator     (was page2-or)  — built out from empty skeleton
  page-ops-lead           (new)  — cross-cutting cockpit
  page-grounding          (new)  — first-class visual for PRD/ADR/ontology grounding
  page-perf-benchmark     (new, hidden from menu)  — hero-scenario cold/warm timings

Hidden helper pages (not in navigation, only reachable via bindings):
  tooltip-kpi-delta       — reused across every KPI card
  tooltip-contributor     — "why did it move" — top 5 contributors
  drill-ward              — from any bed-related visual
  drill-theatre           — from any OR visual
  drill-discharge         — from Discharge tile
```

### 4.1 Page-by-page content

**`page-landing`** — hero image (Helvion symbol), 3 persona tiles (Bed Manager / OR Coordinator / Ops Lead), "As of {timestamp}" pill, environment banner (`SIT — Synthetic data` in SIT), Guest sees a fourth aggregated-only tile.

**`page-bed-manager`** — 4 KPI cards (Occupancy %, Beds Free, ED Arrivals/hr, Forecast Peak 72h), Hospital + Specialty + Time slicers, 12-month capacity vs. required line chart, Month × Weekday RAG heatmap, Discharge Candidates tile (top 5 by readiness), Data-Quality badge (⚠ Inferred for USZ), smart-narrative visual, grounding-cards strip.

**`page-or-coordinator`** — 6 KPI wall (First-case-on-time %, Short-notice-cancellation %, Turnover, Idle-slot, Over-run, OR Utilization %), OR case Gantt timeline, Cancellation-reason donut, Block-reason bar, Anaesthesia consultation funnel, smart-narrative visual, grounding-cards strip.

**`page-ops-lead`** — Cross-cutting headline row (Capacity headline + OR headline + Flow bottleneck cards), small-multiples strip (3×1 hospital tiles for capacity vs. required), Escalation-tier classifier card (green/amber/red — will be `csa-agent`-fed post Sprint 16), smart-narrative visual composing the cross-cutting story, grounding-cards strip.

**`page-grounding`** — Requirement-to-visual lineage: a matrix of `FR-<id>` × `ADR-<nnnn>` × `hcp:<Entity>` × `Measure` × `Visual on page X`. Reusable as an audit artefact.

**`page-perf-benchmark`** (hidden) — Two cards showing cold-load ms and warm-interaction ms for the hero scenario (Bed Manager loading page-bed-manager with USZ selected). Cell values from `[Benchmark — Cold]` and `[Benchmark — Warm]` measures. Reference thresholds annotated on-page (cold < 4000ms, warm < 500ms).

---

## 5. Component boundaries

### 5.1 Theme layer

New `data-platform/reports/capacity-dashboard.Report/themes/helvion.json` derived from the Brandkit colour palette (§8 below). Loaded via `report.json`'s `themeCollection`, replacing the default `CY26SU05`. Design tokens (colour, typography, radius, shadow) documented in a parallel `helvion-token-mapping.md` so Sprint 13 can reuse them in Fluent.

### 5.2 Visual layer

**KPI card contract.** Every KPI card uses the same visual pattern: icon left, big number, delta chip below (green/red arrow + %), sparkline bottom. Reused visualContainer template.

**Chart tooltip contract.** Every chart has a **contributor tooltip** binding to `tooltip-contributor` that shows the top 5 contributors to the current value (by hospital, ward, or specialty depending on visual context).

**Smart-narrative visual.** One per persona page. Fed by the `[Narrative — <Persona>]` measure that composes 1–2 sentences from delta measures.

### 5.3 Field parameters

Two parameter tables for measure-swap (Approach C):

- `param_capacity_measure` — Occupancy % ⇄ Beds Free ⇄ Forecast Peak 72h ⇄ Actual vs Forecast delta.
- `param_or_measure` — First-case-on-time % ⇄ Turnover ⇄ Idle-slot minutes ⇄ Utilization %.

Rendered as a horizontal slicer above the main chart on each persona page. Direct Lake compatibility must be verified in M5 kickoff — if a fallback is required, the parameter table becomes an Import-mode calculated table.

### 5.4 Small-multiples

On `page-ops-lead`, the capacity chart renders as a **3×1 small-multiples strip** (USZ / LUKS / Zollikerberg). Makes the cross-hospital story readable at a glance. Uses the "small multiples" feature on cartesian visuals.

### 5.5 RLS-proof pill

Every visible page top-right. Bound to a DAX measure `[Effective Viewing Label]` that reads `USERPRINCIPALNAME()`, joins to `dim_persona`, and returns a string like `Viewing: USZ • Bed Manager`. In SIT under the soft-slicer path, the pill shows `Viewing: USZ (SIT demo override) • Demo Operator`.

### 5.6 Grounding cards

Strip on every persona page: three cards showing `FR-<id>`, `ADR-<nnnn>`, `hcp:<Entity>` chips. Click → jumps to `page-grounding` with a bookmarked filter selection.

---

## 6. Semantic model additions

Direct Lake mode preserved. Additions go under [data-platform/reports/capacity-dashboard.SemanticModel/definition/](../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/) via TMDL — matches current authoring pattern.

### 6.1 New tables

Add under `tables/`:

- `dim_persona.tmdl` — mirrors the Sprint 12 persona catalog (UPN → app role → default hospital). Read-only, seeded initially from a small `data/synthetic/personas.csv`; Sprint 12 later replaces the source with a Fabric mirror of Entra.
- `param_capacity_measure.tmdl` — field parameter table with 4 measure references (`[Occupancy %]`, `[Beds Free]`, `[Forecast Peak 72h]`, `[Actual vs Forecast]`).
- `param_or_measure.tmdl` — field parameter table with 4 measure references (`[First-Case On-Time %]`, `[Turnover]`, `[Idle-Slot Minutes]`, `[OR Utilization %]`).

### 6.2 New measures (add to appropriate table TMDL files)

**Identity family** (in `dim_persona.tmdl`):
- `[Effective Identity UPN]` — `USERPRINCIPALNAME()`.
- `[Effective Hospital]` — hospital claim from `dim_persona`, overridden by SIT slicer if `[Effective Role Label]` = "Demo Operator" or "Super Admin".
- `[Effective Role Label]` — for the RLS-proof pill.
- `[Effective Viewing Label]` — composed string for the pill.

**Delta family** (in `fact_capacity_baseline.tmdl` and `or_case.tmdl`):
- `[Occupancy % Δ yesterday]`, `[Occupancy % Δ WoW]`, `[Occupancy % Δ MoM]`.
- `[OR Utilization Δ yesterday]`, `[OR Utilization Δ WoW]`, `[OR Utilization Δ MoM]`.
- `[ED Arrivals Δ yesterday]`, `[ED Arrivals Δ WoW]`, `[ED Arrivals Δ MoM]`.
- `[First-Case On-Time Δ yesterday]`, etc.

**Contributor family** (table-returning DAX for `tooltip-contributor`):
- `[Top 5 wards by Δ Occupancy]`.
- `[Top 5 specialties by ED arrivals]`.
- `[Top 5 theatres by Δ Utilization]`.

**Smart-narrative feeders**:
- `[Narrative — Bed Manager]` — string measure composed from delta measures.
- `[Narrative — OR Coordinator]` — string measure.
- `[Narrative — Ops Lead]` — string measure composing the cross-cutting story.

**Perf-benchmark** (used only on `page-perf-benchmark`):
- `[Benchmark — Cold]` — records execution ms.
- `[Benchmark — Warm]` — records execution ms.

### 6.3 New RLS roles (`roles/`)

Existing roles (`BedOps`, `ORPlanner`, `Analyst`, `SemanticOwner`) keep their hard hospital predicates. Add:

- `SITDemoOperator` — no hospital predicate; assignable only to `HCC.DemoOperator` and `HCC.SuperAdmin` in SIT.
- `GuestAggregated` — `hospital = 'Aggregated'` only; assignable to `HCC.GuestReadOnly` in both environments.

---

## 7. RLS strategy (H3 hybrid)

| Env | Identity | Effective RLS role | Slicer visible |
| --- | --- | --- | --- |
| SIT | `HCC.BedManager` @ USZ | `BedOps` (hard: hospital = USZ) | No |
| SIT | `HCC.ORCoordinator` @ LUKS | `ORPlanner` (hard: hospital = LUKS) | No |
| SIT | `HCC.OperationsLead` @ USZ | `Analyst` (hard: hospital in [USZ, LUKS, Zollikerberg]) | No |
| SIT | `HCC.DemoOperator` @ All | `SITDemoOperator` (soft: no filter) | **Yes** |
| SIT | `HCC.SuperAdmin` | `SITDemoOperator` (soft) | **Yes** |
| SIT | `HCC.GuestReadOnly` | `GuestAggregated` (hard: Aggregated only) | No |
| PROD | any | Corresponding hard role only | No (Guest is only Aggregated; others are hospital-scoped) |

Enforced entirely in the semantic model — the report references the same RLS roles in both environments. The app-registration-role → RLS-role mapping happens in the Power BI workspace assignment (Sprint 12 + M1 kickoff overlap).

**RLS-proof pill wording:**
- Hard RLS: `Viewing: USZ • Bed Manager` (from `dim_persona`)
- Soft slicer: `Viewing: USZ (SIT demo override) • Demo Operator`
- Guest: `Viewing: Aggregated • Read-only Guest`

---

## 8. Helvion theme mapping

Brand tokens from [docs/brandkit/Helvion-Brand-Guide.md](../../brandkit/Helvion-Brand-Guide.md) mapped to Power BI theme JSON schema.

| Helvion token | Value | Power BI theme key |
| --- | --- | --- |
| Helvion Red | `#E30613` | `dataColors[0]`, negative KPI (over-threshold accent) |
| Helvion Blue | `#365B7D` | `dataColors[1]`, chart accent, KPI headline |
| Ink | `#2E4C68` | `foreground`, text primary |
| Slate | `#6B7A88` | `secondaryTextColor`, chart axis, subdued text |
| White | `#FFFFFF` | `background`, page + card backgrounds |
| Rainbow gradient (warm→cool) | `#FF9A2E → #FF5A4E → #F0398F → #9A4FF0 → #3E7BF6 → #23C57E` | `dataColors[2..7]` for categorical charts (donut, bar) |
| Segoe UI Bold | wordmark | `textClasses.title.fontFace`, KPI-headline font |
| Segoe UI Semibold uppercase | descriptor | `textClasses.header.fontFace`, subhead |
| Segoe UI Regular/Medium | body | `textClasses.label.fontFace`, chart labels |

Parallel token-mapping doc written at `data-platform/reports/capacity-dashboard.Report/themes/helvion-token-mapping.md` — Sprint 13 reuses it to derive Fluent theme tokens.

---

## 9. Milestones M1–M6

Each milestone is one PR. Sequential-ish (M3 depends on M1; M4 depends on M3) but M2 and M6 can go in parallel with M3.

| # | Milestone | Deliverable | Depends on |
| --- | --- | --- | --- |
| M1 | **Theme + RLS foundation** | `themes/helvion.json`; `dim_persona` table; identity measures; new `SITDemoOperator` + `GuestAggregated` roles. Theme applied to existing 2 pages. | (none) |
| M2 | **Page-2 build-out** | OR Coordinator page's 6 KPIs, Gantt, donut, bar, anaesthesia funnel — populate empty visualContainers. | M1 (theme) |
| M3 | **Landing + Ops Lead + persona split** | `page-landing`, `page-ops-lead`, rename P1 → bed-manager, RLS-pill on every page, navigation buttons. | M1 |
| M4 | **Drill-throughs + custom tooltips** | 3 drill-through pages (ward, theatre, discharge) + 2 tooltip pages (kpi-delta, contributor) + wiring on all headline KPIs. | M3 |
| M5 | **Field parameters + small-multiples + smart-narrative** | `param_capacity_measure` + `param_or_measure` tables, small-multiples strip on Ops Lead, smart-narrative visual per persona page. | M3 |
| M6 | **Grounding + perf-benchmark** | `page-grounding` full matrix, grounding-card strip on every page, hidden `page-perf-benchmark` with cold/warm timings. | M2 + M4 + M5 |

Each milestone PR follows the [PR Output Contract](../../../.github/copilot-instructions.md) with the sections: What/Why/Requirements-implemented/Test-evidence/Agent-impact/API/Infra/Security/Lane/Compliance.

---

## 10. Verification and demo script

### 10.1 3-minute demo script (the design's acceptance criterion)

1. **[0:00–0:20]** Open the report as `demo.guest` → land on `page-landing` → see aggregated banner + Helvion brand + as-of timestamp.
2. **[0:20–0:50]** Click Bed Manager tile → `page-bed-manager` opens, Hospital slicer defaults to USZ (SIT demo override). RLS-proof pill reads `Viewing: USZ (SIT demo override) • Demo Operator`.
3. **[0:50–1:10]** Hover an Occupancy KPI → `tooltip-kpi-delta` shows Δ vs yesterday, WoW, MoM, forecast contribution.
4. **[1:10–1:40]** Click Occupancy % → drill through to `drill-ward`. See ward-level breakdown. Right-click → back.
5. **[1:40–2:10]** Switch to OR Coordinator tile → OR page. Field parameter swap: Utilization → Turnover → Idle-slot.
6. **[2:10–2:40]** Click Ops Lead tile → cross-cutting page with small-multiples per hospital + smart-narrative reads e.g. "OR is at 82% but bed capacity is trailing due to Zollikerberg discharge delay."
7. **[2:40–3:00]** Click a grounding card → `page-grounding` opens showing the FR / ADR / ontology entity chain.

### 10.2 Per-milestone verification (before merge)

Runs via the [`powerbi-report-authoring` skill](../../../.github/skills/powerbi-report-authoring/SKILL.md):

- **PBIR validation:** `powerbi-report-author validate data-platform/reports/capacity-dashboard.Report` — must return clean.
- **Desktop reload + screenshot:** `powerbi-desktop reload` + screenshot of each changed page — human visual review.
- **Theme regression:** snapshot diff of theme-rendered pages against the previous milestone's snapshot; drift only where deliberate.
- **RLS test matrix:** 6 identities × expected pill wording. Automated via a small Python test that reads the DAX result set.
- **Drill-through roundtrip:** for each drill-through, forward + back preserves filters.
- **Direct Lake perf hero:** cold load < 4000ms; warm interaction < 500ms.
- **Field parameter swap:** each parameter table's members render without visual formatting loss.
- **Smart-narrative substance:** each narrative measure returns ≥ 40 characters of substantive text (not filler).

---

## 11. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Direct Lake vs. Import mode limits some visuals (e.g., field parameters may require calculated tables) | Test each parameter in M5 kickoff; document Import-fallback path if hit |
| Helvion brand tokens don't map cleanly to Power BI theme JSON schema | Build translation table `helvion-token-mapping.md` as part of M1 |
| Drill-through breaks RLS scope | Test with each persona; drill target inherits calling page's filters |
| Sprint 10 Gold tables lack columns needed for delta or contributor measures | M1 kickoff pre-check: run `data-platform/scripts/check_gold_columns.py`; fail early if a required column is missing |
| Perf-benchmark exposes real regression | Land M6 last, after content is stable; benchmark becomes the demo-day green light |
| PBIP files hand-authored vs. machine-authored drift (visualContainers folder-hashes) | Use `powerbi-report-author` CLI from the skill, not raw JSON hacking |
| `dim_persona` seeded from CSV before Sprint 12 mirrors Entra | Explicit note in `dim_persona.tmdl` that CSV is the temporary source; swap to Fabric mirror is a Sprint 12 dependency |
| Soft slicer bypasses RLS story during demos with a non-DemoOperator audience | Environment banner in top-right of every page (`SIT — Synthetic data`) makes the demo-override posture unmissable |

---

## 12. Definition of done

- [ ] All six milestones M1–M6 landed as merged PRs.
- [ ] Helvion theme applied to every page; visual-regression snapshots clean.
- [ ] Landing page + 3 persona pages + grounding page all rendered with content (no empty visualContainers).
- [ ] All headline KPIs wired to `tooltip-kpi-delta`, contributor charts wired to `tooltip-contributor`.
- [ ] All 3 drill-through pages roundtrip correctly.
- [ ] RLS-proof pill returns expected values across 6 test identities.
- [ ] Field parameters swap without formatting loss.
- [ ] Smart-narrative measures return substantive text for the 3 personas.
- [ ] Grounding-card strip on every visible page; `page-grounding` matrix populated.
- [ ] Perf-benchmark hero scenario cold < 4000ms, warm < 500ms.
- [ ] `powerbi-report-author validate` returns clean.
- [ ] `data-platform/reports/capacity-dashboard.Report/README.md` updated to reflect the v2 structure.
- [ ] Retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
