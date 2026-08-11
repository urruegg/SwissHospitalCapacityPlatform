<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img src="brandkit/logo/curavias-logo.svg" alt="Curavias" width="240"/>
</p>
<!-- markdownlint-enable MD033 MD041 -->

# Curavias — Business Value Assessment

| Field | Value |
| ----- | ----- |
| **Version** | 2.0.0 |
| **Date** | 2026-08-07 |
| **Author** | Urs Rueegg |
| **Status** | Final — evidence-refined |
| **Previous Version** | 1.1.1 (Sprint 34 WS-3: Curavias anchor + product-anchor line + executive summary; Curavias brand-kit logo added to the document header) |
| **Change in this version** | Introduces a **measured** build-cost evidence base (Azure ActualCost + Copilot telemetry + tracked human effort) and a **Frontier-informed** one-time cost model derived from it. Run-cost model deliberately unchanged. |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

This Business Value Assessment gives executives a Rough Order of Magnitude (ROM)
view of the return on investment and total cost of ownership for the Curavias
MVP over a three-year horizon. Figures are business-case shaping estimates
(plus/minus 30 percent unless labelled **measured**), in CHF, and are not
procurement commitments.

## Purpose

This Business Value Assessment establishes the Return on Investment (ROI) and
Total Cost of Ownership (TCO) baseline for MVP justification.

Version 2.0.0 changes the epistemic status of the cost side. Version 1.0.1 was
ROM throughout. This version separates:

- **Measured cost** — what the Curavias art-of-the-possible showcase actually
  cost to build, from authoritative billing and tracked effort (§3).
- **Modelled cost** — what a hospital implementation is projected to cost,
  informed by that measurement (§4).

Value levers (§6) remain ROM and are unchanged; they require provider-native
finance validation.

---

## 1. Scope and Method

### Scope

- Single-provider MVP deployment model.
- In-scope services and controls from PRD, ARCHITECTURE, AI, SECURITY,
  COMPLIANCE and DATA baselines.
- 3-year planning horizon for the investment decision.

### Method and reliability

| Layer | Status | Confidence |
| ----- | ------ | ---------- |
| Showcase build cost (§3) | **Measured** — Azure Cost Management ActualCost, Copilot CLI telemetry, tracked effort | High (±10%, see §3.5 caveats) |
| Hospital one-time cost (§4) | **Modelled**, anchored on §3 | ROM ±30% |
| Annual run cost (§5) | **Modelled** — no production measurement exists | ROM ±30% |
| Value levers (§6) | **ROM assumption** — unvalidated against provider finance | ROM ±30% |

All values in CHF unless noted. USD converted at **0.88 CHF/USD**.

---

## 2. Demand Baseline Used for Cost and Value Modelling

| Demand signal | Baseline assumption |
| ----- | ----- |
| Operational source events | 180,000 per day |
| Burst headroom | 3x average event rate in 10-minute windows |
| Forecast runs | 24 per day |
| Discharge rescoring | 48 scheduled per day plus event-driven deltas |
| Copilot turns | 8,000 per day |
| Peak concurrent copilot users | 120 |
| Interactive response objective | P95 under 4 seconds |

---

## 3. Measured Build Cost — the Frontier evidence base

The Curavias showcase was built by **one human orchestrating agents** over a
90-day window. This section is the authoritative record of what that cost.

### 3.1 Human effort

| Parameter | Value | Basis |
| ----- | ----- | ----- |
| Fully loaded annual cost (1 person) | CHF 200,000 | Given |
| Swiss working days per year | 220 | Standard |
| Hours per working day | 8.4 | 42-hour week |
| Annual productive hours | 1,848 | 220 x 8.4 |
| **Blended hourly rate** | **CHF 108.23** | 200,000 / 1,848 |
| Daily engagement | 1 h/day x 90 calendar days = 90 h | Tracked |
| Sprint engagement | 5 sprints x 2 days x 8.4 h = 84 h | Tracked |
| **Total effort** | **174 h = 20.7 person-days** | |
| **Total human cost** | **CHF 18,831** | 174 x 108.23 |

Effort represents **9.4% of one FTE-year**.

### 3.2 Azure cloud services — authoritative billed cost

Source: Azure Cost Management **ActualCost**, subscription
`ME-MngEnvMCAP164444-urruegg-1`, period 2026-06-29 to 2026-07-27.
No spend before 2026-06-29 (SIT/PROD stood up after the Sprint 00 tenant
migration).

| Service | USD | Share |
| ----- | ---: | ---: |
| Microsoft Fabric | 218.85 | 44.6% |
| Log Analytics | 69.92 | 14.2% |
| Azure Container Apps | 47.08 | 9.6% |
| Azure Cosmos DB | 35.05 | 7.1% |
| Event Hubs | 32.32 | 6.6% |
| Container Registry | 29.36 | 6.0% |
| Azure Cognitive Search | 28.56 | 5.8% |
| Virtual Network | 12.95 | 2.6% |
| Load Balancer | 10.85 | 2.2% |
| Azure App Service | 5.85 | 1.2% |
| Foundry Models, DNS, Storage | 0.31 | 0.1% |
| **Total billed (5 weeks)** | **491.11** | |

- Observed run rate: **USD 98.22 / week**
- Extrapolated across the 90-day build window: **USD 1,262.85 = CHF 1,111**
- Deployed inventory: **144 Azure resources**

### 3.3 Copilot agent consumption

Source: GitHub Copilot CLI session-store telemetry (AIU series from
2026-07-17).

| Metric | Value |
| ----- | ---: |
| Sessions | 42 |
| Input tokens | 2,365,656,807 |
| — of which cache reads | 2,197,904,813 (92.9%) |
| — fresh input | 167,751,994 |
| Output tokens | 16,455,325 |
| Reasoning tokens | 5,757,871 |
| AI Units consumed | 246,101.68 |

**Monetary estimate** (token-priced, frontier-class list rates — USD 3.00 /
15.00 / 0.30 per 1M input / output / cache-read):

| Component | USD |
| ----- | ---: |
| Fresh input | 503.26 |
| Output | 246.83 |
| Cache read | 659.37 |
| **Total** | **1,409.46 = CHF 1,240** |

Implied rate: **USD 0.00573 per AI Unit**. See §3.5 — this is the weakest
number in the model.

### 3.4 Total measured build cost

| Cost element | CHF | Share |
| ----- | ---: | ---: |
| Human effort (1 person, 174 h) | 18,831 | 88.5% |
| Copilot agent tokens | 1,240 | 5.8% |
| Azure cloud services | 1,111 | 5.2% |
| Copilot subscription (3 months) | 103 | 0.5% |
| **Total 90-day build cost** | **21,286** | **100%** |

#### Unit economics

| Unit | Cost |
| ----- | ---: |
| Per sprint (30 sprints) | CHF 710 |
| Per agent (7 runtime + PO agent) | CHF 2,661 |
| Per deployed Azure resource (144) | CHF 148 |
| Per human hour, all-in | CHF 122 |

### 3.5 Caveats — read before quoting these figures

1. **Copilot cost is an estimate, not a bill.** The session store records AI
   Units but no `$`/AIU rate. The monetary line is derived from token counts at
   frontier-class list pricing. Authoritative figures require the billed AIU
   rate from the GitHub billing dashboard.
2. **Copilot telemetry is incomplete.** The AIU series starts 2026-07-17 and
   covers 42 sessions; earlier sprints are not captured. The true full-build
   token cost is **higher** than stated.
3. **Azure figures are proof-of-technology scope.** Per ADR-0013 the workload
   runs in `westus2` on synthetic data. This is **not** a production
   Swiss-region run rate.
4. **Recent weeks settle upward.** The 2026-07-27 week moved from 26.66 to
   58.10 between two same-day pulls.
5. **The showcase is not a hospital implementation.** It carries no real
   integration, no change management, no cantonal compliance mapping and no
   production HA. §4 addresses that gap explicitly.

---

## 4. One-Time Implementation Cost — Frontier-informed model

### 4.1 What the measurement proves

| Comparison | Amount |
| ----- | ---: |
| BVA v1.0.1 line "MVP design, engineering and integration build" | CHF 640,000 |
| Measured Frontier build (1 human + agents, 90 days) | CHF 21,286 |
| **Ratio** | **30x** |

The showcase does **not** prove a hospital implementation costs CHF 21k. It
proves that the **platform-build component** of the cost stack collapses when
one human orchestrates agents against a reusable blueprint. Hospital-specific
integration, change management and compliance mapping do not collapse — and
two of them were named by reviewers as the actual failure modes.

### 4.2 Revised one-time cost model

| Cost element | ROM v1.0.1 | Frontier-informed | Rationale |
| ----- | ---: | ---: | ----- |
| Platform build (design, engineering) | 640,000 | 60,000 | Platform exists and is reusable; agents perform the build. Evidence: §3.4 |
| Hospital-specific integration (Epic / KIS) | — | 180,000 | Split out. Epic API-first; Polypoint documented as a risk path with fallback (COO review 24.07.2026) |
| Security and compliance hardening | 180,000 | 140,000 | IaC and control evidence reusable; cantonal legal mapping remains per-provider (Cantonal IT review 08.06.2026) |
| Data onboarding and contract implementation | 220,000 | 180,000 | Analytical-layer availability assessment is a pilot precondition (CIO review 17.07.2026) |
| Training, change adoption and hypercare | 120,000 | 120,000 | **Unchanged by design.** The COO named adoption and the human factor as the make-or-break; cutting this line would contradict the primary review finding |
| Program contingency reserve | 140,000 | 100,000 | Scaled with reduced build risk |
| **Total one-time cost** | **1,300,000** | **780,000** | **−40%** |

### 4.3 What did not change, and why

The 40% reduction falls almost entirely on **build**. Training and change
adoption is held flat deliberately: the strongest finding across the review
programme was that technology is not the bottleneck. A business case that
banks Frontier savings by cutting change management would fail on exactly the
risk the reviewers identified.

---

## 5. Recurring Annual Cost (Run Cost)

Unchanged from v1.0.1. The measured Azure figure (USD ~5.1k/yr extrapolated)
is a proof-of-technology footprint on synthetic data in a non-Swiss region and
is **not** evidence for a production run rate at 180,000 events/day, 8,000
copilot turns/day, Fabric F-capacity and HA.

| Cost element | ROM per year |
| ----- | ---: |
| Azure and platform service consumption | 760,000 |
| Operations, support and reliability engineering | 260,000 |
| Security operations, audit evidence and compliance cadence | 140,000 |
| Model monitoring and continuous evaluation operations | 90,000 |
| **Total annual run cost** | **1,250,000** |

**Open action:** re-baseline this section after pilot month 2 using observed
production telemetry. Until then it remains the least evidenced part of the model.

---

## 6. Business Value Model (ROM — unchanged)

| Value lever | ROM annual benefit | Value logic |
| ----- | ---: | ----- |
| Reduced avoidable bed-day blocking and discharge delay | 1,650,000 | Faster coordination and discharge-readiness decisions increase effective bed turnover |
| Improved command-center productivity | 980,000 | 120 peak users with reduced manual triage and faster decisions |
| Reduced overtime and agency premium | 620,000 | Forecast-informed planning reduces expensive reactive staffing |
| Lower integration and coordination failure cost | 350,000 | Improved workflow reliability, fewer manual recoveries |
| Compliance and audit preparation efficiency | 220,000 | Evidence-ready controls reduce recurring audit effort |
| **Total gross annual benefit** | **3,820,000** | |

| Metric | Amount |
| ----- | ---: |
| Gross annual benefit | 3,820,000 |
| Annual run cost | 1,250,000 |
| **Net annual benefit** | **2,570,000** |

---

## 7. ROI and Payback

### 7.1 Comparison of both models

| KPI | ROM v1.0.1 | Frontier-informed v2.0.0 |
| ----- | ---: | ---: |
| One-time cost | 1,300,000 | **780,000** |
| Annual run cost | 1,250,000 | 1,250,000 |
| 3-year TCO | 5,050,000 | **4,530,000** |
| 3-year gross benefit | 11,460,000 | 11,460,000 |
| 3-year net value | 6,410,000 | **6,930,000** |
| **3-year ROI** | **127%** | **153%** |
| **Simple payback** | **~6.1 months** | **~3.6 months** |

### 7.2 Sensitivity — Frontier-informed model

| Scenario | Annual benefit | Annual run | One-time | 3-year TCO | 3-year ROI | Payback |
| ----- | ---: | ---: | ---: | ---: | ---: | ---: |
| Conservative | 2,600,000 | 1,320,000 | 900,000 | 4,860,000 | **60%** | 8.4 mo |
| Base | 3,820,000 | 1,250,000 | 780,000 | 4,530,000 | **153%** | 3.6 mo |
| Upside | 5,000,000 | 1,230,000 | 700,000 | 4,390,000 | **242%** | 2.2 mo |

Even the conservative case clears the >60% governance target — but only just.
The binding constraint is **benefit realisation**, not cost.

---

## 8. KPI Framework for Executive Governance

### Financial KPIs

| KPI | Target | Cadence |
| ----- | ----- | ----- |
| 3-year ROI | > 60% | Quarterly |
| Payback period | < 24 months | Monthly in first 12 months |
| Annual run cost variance to budget | Within ±10% | Monthly |
| Cost per copilot turn | Tracked, reducing QoQ | Monthly |
| Cost per forecast / discharge decision cycle | Tracked, trend down | Monthly |
| **Build cost per sprint** | **< CHF 1,000** | **Per sprint** |
| **Agent token cost per delivered feature** | **Tracked, trend down** | **Monthly** |

### Operational value KPIs

| KPI | Direction | Cadence |
| ----- | ----- | ----- |
| Time to bed-assignment decision | Down | Weekly |
| Delayed discharge cases | Down | Weekly |
| Avoidable bed-day blocking | Down | Monthly |
| Forecast error at operational horizon | Down | Weekly |
| Manual coordination touches per discharge case | Down | Weekly |

### Governance and risk KPIs

| KPI | Target | Cadence |
| ----- | ----- | ----- |
| Evidence completeness for compliance controls | 100% at release gates | Monthly |
| PHI transfer policy violations | Zero | Continuous |
| High-severity findings open beyond SLA | Zero | Weekly |

---

## 9. Key Risks to the Business Case

1. **Adoption risk (highest).** If operational teams do not embed forecast and
   discharge recommendations into daily cadence, realised value underperforms.
   Named independently by the COO as the primary failure mode.
2. **Data quality risk.** Low-quality source feeds reduce forecast and
   recommendation reliability, and rejected reports create a self-reinforcing
   adoption decline.
3. **Run-cost estimation risk.** Section 5 is the least evidenced part of the
   model. A production Swiss-region footprint could exceed the ROM.
4. **Copilot cost-rate risk.** §3.3 uses a derived rate. A materially higher
   billed AIU rate raises build cost — though from a small base.
5. **Scope creep risk.** Adding non-MVP capability before value stabilises
   raises TCO ahead of benefit.
6. **Compliance delay risk.** Unresolved cantonal legal mapping can defer
   production rollout and value realisation.

---

## 10. Decision Guidance and Next Steps

1. Use the **Frontier-informed model (§7)** as the executive go/no-go baseline;
   retain the ROM v1.0.1 model as the conservative comparison.
2. Obtain the **billed AIU rate** from the GitHub billing dashboard and replace
   the derived figure in §3.3.
3. Confirm local finance assumptions for bed-day economics, staffing cost and
   audit effort reduction — the value side remains entirely unvalidated.
4. Run the **data-availability assessment** (Epic to analytical layer) before
   pilot commitment.
5. Re-baseline run cost after pilot month 2 with observed production telemetry.
6. Convert this model into a tracked business-value dashboard with monthly KPI
   reporting.

---

## 11. Requirement and Control Alignment

This BVA supports investment justification for:

- PRD demand and performance requirements (NFR-PERF, NFR-REL families)
- Governance and evidence requirements (FR-GOV, NFR-COMP families)
- Security and responsible-AI controls as value-protection mechanisms

## 12. Source Evidence

| Source | Type | Used for |
| ----- | ----- | ----- |
| Azure Cost Management ActualCost (subscription MCAP164444) | Authoritative billing | §3.2 |
| `agent_cost.md` — Copilot CLI session-store telemetry | Telemetry | §3.3 |
| `agent-cost-bom.md`, `bom.yaml` — deployed inventory (144 resources) | Configuration | §3.2 |
| Tracked engagement, 90-day window | Effort record | §3.1 |
| COO review 24.07.2026 | Review record | §4.2, §9 |
| CIO review 17.07.2026 | Review record | §4.2 |
| Cantonal IT review 08.06.2026 | Review record | §4.2 |
| [`data/master-data/bva/`](../data/master-data/bva/README.md) — dim/fact evidence master data (this document's figures reduced to a citable star schema, each row carrying an `evidence_status`) | Structured master data | Every figure in this document; grounds the `bva-agent` and Product Owner Agent Class C answers |
