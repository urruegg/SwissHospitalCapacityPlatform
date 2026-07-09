# Sprint 15 — BVA Evidence Data Product (synthetic seed) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/superpowers/ideas/Swiss-Hospital-Capacity-Live-Business-Value-Assessment-(BVA)-Dashboard.md](../ideas/Swiss-Hospital-Capacity-Live-Business-Value-Assessment-(BVA)-Dashboard.md) |
| **ROM baseline** | [docs/BVA.md](../../BVA.md) v1.0.1 |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture and data flow](#3-architecture-and-data-flow)
4. [Synthetic data design (FOCUS-shaped)](#4-synthetic-data-design-focus-shaped)
5. [Extended star schema](#5-extended-star-schema)
6. [C-suite views and KPIs](#6-c-suite-views-and-kpis)
7. [BVA cards on the presenter whiteboard](#7-bva-cards-on-the-presenter-whiteboard)
8. [Row-level security](#8-row-level-security)
9. [Stretch — `bva-agent`](#9-stretch--bva-agent)
10. [Agent and skill mix](#10-agent-and-skill-mix)
11. [GitHub delegation](#11-github-delegation)
12. [Side-effect posture and approval gates](#12-side-effect-posture-and-approval-gates)
13. [Verification strategy](#13-verification-strategy)
14. [Risks and mitigations](#14-risks-and-mitigations)
15. [Dependencies](#15-dependencies)
16. [Definition of done](#16-definition-of-done)

---

## 1. Goal and desired end state

The live BVA data product is operating on **synthetic** Azure-consumption data that mirrors the FOCUS export shape. Five C-suite views (CEO, CFO, CIO, COO, CTO) each render as cards on the Sprint 14 presenter whiteboard (Backstage → Evidence tab picks up a new "BVA" filter), plus a standalone Power BI app for board distribution. All plan-vs-actual KPIs are computable from the synthetic seed.

**Why synthetic only.** User selected Option A (synthetic seed) — decouples Sprint 15 from any Azure Cost Management / FOCUS export setup delays. Data model is FOCUS-shaped so a future PR can swap the source with one config change.

---

## 2. Scope

### 2.1 In-scope MVP

- Synthetic FOCUS-shaped dataset generator under `data-platform/scripts/bva-synth-focus.py` — emits daily-partitioned Parquet with columns matching FOCUS spec.
- Extended BVA star schema (§5) — `Fact_AzureConsumption`, `Fact_Cost`, `Fact_Budget`, `Fact_ValueRealization`, dims for `Service`, `Meter`, `Resource`, `Environment`, `Hospital`, `Capability`, `Persona`, `Date`.
- Adoption telemetry from Sprint 12 joined to `Fact_ValueRealization` — proves the "adoption %" KPI.
- Semantic model + DAX for 20+ headline KPIs (ROI, TCO, payback, cost per copilot turn, adoption %, run-rate variance).
- Row-level security by exec role + hospital.
- Three C-suite card types on the presenter whiteboard: **Headline KPI card**, **Plan-vs-Actual card**, **Trend card**.
- Board-summary shared page + role-aware landing (RLS routing).

### 2.2 Out-of-scope / deferred

- Real FOCUS export from Azure Cost Management (roadmap Q-4).
- ADLS Gen2 raw storage tier setup.
- Automated monthly PDF/email subscription (manual Power BI subscription in the demo).
- Non-Azure vendor cost (kept as plan-only line items).

### 2.3 Stretch — only if MVP lands early

- **`bva-agent`** — monthly narrative summary (Foundry agent) that drafts a Markdown board pack into `docs/board-packs/YYYY-MM/`.

---

## 3. Architecture and data flow

```
Sprint 12 adoption telemetry ──▶  Bronze/adoption/*.json  ┐
Sprint 15 synthetic FOCUS gen ──▶  Bronze/consumption/*.parquet │
                                                                ▼
                                    Fabric Medallion (BVA lakehouse)
                                                                ▼
                                    Semantic model (Direct Lake)
                                                                ▼
                                    ┌──────────┴──────────┐
                                    ▼                     ▼
                            Power BI app                Presenter whiteboard
                            (board distribution)         (BVA card catalog on
                                                          Sprint 14 whiteboard)
```

**Refresh cadence.** Nightly via `.github/workflows/bva-sim-refresh.yml`. The workflow (a) regenerates 90 days of synthetic data with reproducible seed, (b) uploads Parquet to Bronze, (c) triggers Fabric pipeline.

---

## 4. Synthetic data design (FOCUS-shaped)

**Timeframe.** 90 days ending "yesterday" (rolls forward on refresh).

**Services.** Mirror the Sprint 14 BOM: Fabric, Cosmos, Container Apps, Storage, Key Vault, Monitor, Foundry, App Insights, Log Analytics, Service Bus, Cache for Redis.

**Hospitals.** USZ / LUKS / Zollikerberg / Aggregated (tag on each resource).

**Environments.** dev / sit / prod (tag on each resource).

**Capabilities.** BMCA / OOA / DCA / ORSA / SBA / CSA (per-agent cost attribution via resource tag).

**Calibration.** Numbers targeted to hit the ROM baseline (~CHF 760k/yr Azure consumption per [BVA.md](../../BVA.md) v1.0.1) with ±15% noise so plan-vs-actual variance is realistic and visible.

**FOCUS columns emitted.**

`ChargeType`, `ServiceCategory`, `ServiceName`, `ResourceId`, `ResourceName`, `ResourceType`, `Region`, `MeterName`, `MeterCategory`, `MeterSubCategory`, `BillingPeriod`, `ChargePeriodStart`, `ChargePeriodEnd`, `BilledCost`, `EffectiveCost`, `ListCost`, `Quantity`, `UnitPrice`, `PricingUnit`, `Currency` (fixed CHF).

**Custom columns added (tag-derived).** `x_env`, `x_hospital`, `x_capability`.

---

## 5. Extended star schema

**Facts.**

| Fact | Grain | Notable measures |
| --- | --- | --- |
| `Fact_AzureConsumption` | resource × meter × day | `EffectiveCost`, `Quantity` |
| `Fact_Cost` | non-Azure line × month | one-time + run cost (plan-only in MVP) |
| `Fact_Budget` | budget line × month × env | plan cost |
| `Fact_ValueRealization` | capability × month × hospital | benefit realized, adoption count, decision cycles |

**Dimensions.** `Dim_Service`, `Dim_Meter`, `Dim_Resource`, `Dim_Environment`, `Dim_Hospital`, `Dim_Capability`, `Dim_Persona`, `Dim_Date`, `Dim_ExecRole`.

---

## 6. C-suite views and KPIs

Follows the anchor idea §4.1.

| Persona | Headline KPI | Supporting KPIs |
| --- | --- | --- |
| **CEO** | 3-yr net value realized (CHF) + benefit-realization % | ROI %, strategic adoption %, patient/bed-day impact, quality trend |
| **CFO** | Actual TCO vs. budget + payback tracking | ROI %, net annual benefit, run-cost variance %, cost-to-value ratio, Azure spend YTD vs. plan |
| **CIO** | Azure run-rate vs. budget + cost-optimization realized | spend by service/env, reliability (SLO), active users/adoption, cost avoidance |
| **COO** | Avoidable bed-day blocking (down) | time-to-bed-assignment, delayed discharges, forecast error, manual touches/discharge, OR utilization |
| **CTO** | Cost per copilot turn (trend down) | cost per decision cycle, cost per capability/agent, inference efficiency, model quality & P95 latency, burst headroom |

Each KPI is a DAX measure with a target, cadence tag, and RLS profile.

---

## 7. BVA cards on the presenter whiteboard

Sprint 14 whiteboard gains a "BVA" filter/tab. Three new card types:

| Card | Content | Drill-in |
| --- | --- | --- |
| **Headline KPI** | One big number vs. target vs. plan + variance chip | Underlying DAX + drill-through to Power BI page |
| **Plan-vs-Actual** | Small multiples with plan, actual, and variance band | Full Power BI page |
| **Trend** | Sparkline + N-month sparkline | Full Power BI page |

Reuse contract with Sprint 14: the whiteboard framework in `apps/hcc-app-fluent/src/whiteboard/` is untouched; Sprint 15 registers three new card types in the card registry.

---

## 8. Row-level security

- **Exec role** — CEO / CFO / CIO / COO / CTO see only their landing page as default; Board-summary is shared.
- **Hospital context** — every fact filtered by user's `hospital` claim; `Aggregated` bypasses filter.
- **Env** — every fact filtered by `env` claim from Sprint 12.
- `HCC.SuperAdmin` — bypasses all RLS filters (still audited).
- `HCC.GuestReadOnly` — sees `Aggregated` hospital only; sees a fixed "Board-summary" landing.

Enforced in the Fabric semantic model via DAX RLS roles.

---

## 9. Stretch — `bva-agent`

Only if MVP lands early. Foundry agent that:

- runs on the first business day of each month;
- reads the previous month's KPIs from the semantic model;
- drafts a Markdown board pack into `docs/board-packs/YYYY-MM/board-pack.md`;
- opens a draft PR for CFO review;
- refuses to include commentary that materially exceeds the KPI numbers (grounding-only rule).

MCP servers: `github-mcp`, `fabric-mcp`. Ceiling: `write`. Model selection follows Sprint 11 ADR.

---

## 10. Agent and skill mix

| Component | Superpowers skills | Domain skills |
| --- | --- | --- |
| Synthetic data generator | `writing-plans`, `test-driven-development` | (none) |
| Medallion + semantic model | Same + `subagent-driven-development` | `spark-authoring`, `fabric-semantic-model-authoring`, `powerbi-optimization` |
| C-suite Power BI pages | Same | `powerbi-report-authoring`, `powerbi-optimization` |
| BVA cards (React components) | Same | (from Sprint 13 decision stack) |
| Stretch `bva-agent` | Same | Foundry agent authoring |

---

## 11. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Workflow — BVA sim refresh | `.github/workflows/bva-sim-refresh.yml` | Nightly synth-refresh |
| Issue template — BVA KPI | `.github/ISSUE_TEMPLATE/bva-kpi.yml` | New/changed DAX measure |
| Issue template — BVA report page | `.github/ISSUE_TEMPLATE/bva-report-page.yml` | Report page work |
| Labels | `sprint-15`, `bva`, `focus-sim`, `dax`, `rls` | Applied by templates |
| CODEOWNERS | `.github/CODEOWNERS` | `data-platform/scripts/bva-synth-focus.py` and BVA semantic model paths → @urruegg |

---

## 12. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| Synthetic data refresh (workflow) | `write` | Automated on schedule |
| Semantic model publish | `deploy` | `approved-to-apply` |
| RLS role assignments in Power BI workspace | `deploy` | `approved-to-apply` |
| `bva-agent` deployment (stretch) | `deploy` | `approved-to-apply` |
| DAX measure changes | `write` | Standard PR review + `dax` label |

---

## 13. Verification strategy

- **KPI regression test** — for a fixed synthetic seed, ROI / TCO / payback DAX measures return expected values (golden fixtures).
- **RLS test suite** — `demo.guest` sees aggregated only; `super.admin` sees all; each C-suite persona sees their landing page.
- **Adoption join test** — `Fact_ValueRealization` correctly matches Sprint 12 sign-in events (row counts + user coverage).
- **FOCUS shape test** — generated Parquet passes FOCUS validator (columns + types).
- **E2E** — presenter opens Evidence tab → filters to "BVA" → sees CEO/CFO/CIO/COO/CTO card cluster; drill-in opens the corresponding Power BI page.
- **Cost calibration test** — total annualised synthetic cost within ±15% of ROM baseline (CHF 760k/yr).

---

## 14. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Synthetic numbers unrealistic and undermine demo credibility | Calibrate to ROM baseline (BVA v1.0.1); documented seed; reproducible |
| RLS misconfiguration leaks cross-hospital data | Automated RLS test with 4 hospital claims + expected row counts |
| DAX measure drift across revisions | Golden-value regression test per measure |
| Sprint 14 whiteboard incomplete blocks BVA cards | Cards designed as standalone Fluent components; render also in a plain Power BI embed as fallback |
| Adoption pipeline empty on demo day | Backfill 30 days of synthetic sign-ins if real telemetry not yet flowing |
| Board pack draft PR (stretch) publishes speculative claims | Grounding-only rule enforced in `bva-agent` prompt; refusal if KPI value missing |

---

## 15. Dependencies

**In**: Sprint 12 (adoption telemetry), Sprint 14 (presenter whiteboard component + Evidence tab).

**Out**: (none critical downstream — Sprint 16 is independent).

---

## 16. Definition of done

- [ ] `bva-sim-refresh.yml` green nightly.
- [ ] Medallion + semantic model produce all headline KPIs from the KPI table §6.
- [ ] Five C-suite pages rendered in Power BI with RLS verified.
- [ ] BVA card cluster visible on the Sprint 14 presenter whiteboard (BVA filter/tab).
- [ ] FOCUS shape validation green.
- [ ] Cost calibration within ±15% of ROM baseline.
- [ ] Stretch: `bva-agent` drafts one board pack PR (or explicit "not attempted" note in retro).
- [ ] Sprint 15 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
