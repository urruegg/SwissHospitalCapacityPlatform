<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img src="brandkit/logo/curavias-logo.svg" alt="Curavias" width="240"/>
</p>
<!-- markdownlint-enable MD033 MD041 -->

# Curavias — Business Value Assessment

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.1 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.1.0 (Sprint 34 WS-3: Curavias anchor + product-anchor line + executive summary); this bump adds the Curavias brand-kit logo to the document header |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

This Business Value Assessment gives executives a Rough Order of Magnitude (ROM)
view of the return on investment and total cost of ownership for the Curavias
MVP over a three-year horizon. Figures are business-case shaping estimates
(plus/minus 30 percent), in CHF, and are not procurement commitments.

## Purpose

This Business Value Assessment (BVA) establishes a first
Return on Investment (ROI) and Total Cost of Ownership (TCO) baseline for
MVP justification.

It uses the current demand assumptions and architecture scope as a
Rough Order of Magnitude (ROM) model for executive decision support.

## Scope and Method

### Scope

- Single-provider MVP deployment model.
- In-scope services and controls from PRD, ARCHITECTURE, AI, SECURITY,
  COMPLIANCE, and DATA baselines.
- 3-year planning horizon for investment decision.

### Method and Reliability

- Financial values are ROM assumptions for business-case shaping,
  not final procurement commitments.
- ROM confidence band: plus/minus 30 percent.
- All values are presented in CHF unless noted.

## Demand Baseline Used for Cost and Value Modeling

The BVA uses the current stress-tested architecture assumptions:

| Demand Signal | Baseline Assumption |
| ----- | ----- |
| Operational source events | 180000 per day |
| Burst headroom | 3x average event rate in 10-minute windows |
| Forecast runs | 24 per day |
| Discharge rescoring | 48 scheduled per day plus event-driven deltas |
| Copilot turns | 8000 per day |
| Peak concurrent copilot users | 120 |
| Interactive response objective | P95 under 4 seconds |

## ROM Cost Model (TCO Inputs)

### One-Time Implementation Costs (Year 0 to Year 1)

| Cost Element | ROM Assumption |
| ----- | ----- |
| MVP design, engineering, and integration build | 640000 |
| Security and compliance implementation hardening | 180000 |
| Data onboarding and contract implementation | 220000 |
| Training, change adoption, and hypercare | 120000 |
| Program contingency reserve | 140000 |
| **Total One-Time Cost** | **1300000** |

### Recurring Annual Costs (Run Cost)

| Cost Element | ROM Assumption per Year |
| ----- | ----- |
| Azure and platform service consumption | 760000 |
| Operations, support, and reliability engineering | 260000 |
| Security operations, audit evidence, and compliance cadence | 140000 |
| Model monitoring and continuous evaluation operations | 90000 |
| **Total Annual Run Cost** | **1250000** |

### 3-Year TCO

| TCO Component | Amount |
| ----- | ----- |
| One-time implementation | 1300000 |
| Recurring run cost (3 x 1250000) | 3750000 |
| **3-Year TCO** | **5050000** |

## ROM Business Value Model

### Value Levers and Annual Benefit Assumptions

| Value Lever | ROM Annual Benefit Assumption | Value Logic |
| ----- | ----- | ----- |
| Reduced avoidable bed-day blocking and discharge delay | 1650000 | Faster coordination and discharge readiness decisions increase effective bed turnover |
| Improved command-center productivity | 980000 | 120 peak users with reduced manual triage and faster decisions |
| Reduced overtime and agency premium through better demand visibility | 620000 | Forecast-informed planning reduces expensive reactive staffing |
| Lower integration and coordination failure cost | 350000 | Better outbound/inbound workflow reliability and fewer manual recoveries |
| Compliance and audit preparation efficiency gain | 220000 | Evidence-ready controls reduce recurring compliance and audit effort |
| **Total Gross Annual Benefit** | **3820000** |  |

### Net Annual Benefit

| Metric | Amount |
| ----- | ----- |
| Gross annual benefit | 3820000 |
| Annual run cost | 1250000 |
| **Net annual benefit (post run cost)** | **2570000** |

## ROI and Payback (Base ROM Scenario)

| KPI | Formula | Result |
| ----- | ----- | ----- |
| 3-year gross benefit | 3 x 3820000 | 11460000 |
| 3-year net value | 11460000 minus 5050000 | 6410000 |
| 3-year ROI | (11460000 minus 5050000) divided by 5050000 | 127 percent |
| Year-1 total cost | 1300000 plus 1250000 | 2550000 |
| Year-1 net value | 3820000 minus 2550000 | 1270000 |
| Simple payback period | 1300000 divided by 2570000 | approximately 6 months |

## Sensitivity Analysis

| Scenario | Annual Benefit | Annual Run Cost | 3-Year TCO | 3-Year ROI | Comment |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Conservative | 2600000 | 1320000 | 5260000 | 48 percent | Lower operational uptake and slower process adoption |
| Base ROM | 3820000 | 1250000 | 5050000 | 127 percent | Balanced adoption and expected improvement profile |
| Upside | 5000000 | 1230000 | 4990000 | 201 percent | Strong adoption and larger throughput gains |

## KPI Framework for Executive Governance

### Financial KPIs

| KPI | Target | Cadence |
| ----- | ----- | ----- |
| 3-year ROI | More than 60 percent | Quarterly |
| Payback period | Less than 24 months | Monthly in first 12 months |
| Annual run cost variance to budget | Within plus/minus 10 percent | Monthly |
| Cost per copilot turn | Tracked and reduced quarter-over-quarter | Monthly |
| Cost per forecast/discharge decision cycle | Tracked with trend down target | Monthly |

### Operational Value KPIs

| KPI | Target Direction | Cadence |
| ----- | ----- | ----- |
| Time to bed-assignment decision | Down | Weekly |
| Delayed discharge cases | Down | Weekly |
| Avoidable bed-day blocking | Down | Monthly |
| Forecast error at operational horizon | Down | Weekly |
| Manual coordination touches per discharge case | Down | Weekly |

### Governance and Risk KPIs

| KPI | Target | Cadence |
| ----- | ----- | ----- |
| Evidence completeness for compliance controls | 100 percent for release gates | Monthly |
| PHI transfer policy violations | Zero tolerated | Continuous monitoring |
| High-severity security or privacy findings open beyond SLA | Zero tolerated | Weekly |

## Requirement and Control Alignment

This BVA supports investment justification for:

- PRD demand and performance requirements (NFR-PERF and NFR-REL families).
- Governance and evidence requirements (FR-GOV and NFR-COMP families).
- Security and responsible AI controls as value-protection mechanisms,
  not only compliance overhead.

## Key Risks to the Business Case

1. Adoption risk: if operational teams do not embed forecast and discharge
   recommendations into daily cadence, realized value will underperform.
2. Data quality risk: low-quality source feeds can reduce forecast and
   recommendation reliability.
3. Scope creep risk: adding non-MVP capabilities too early can raise TCO before
   value stabilization.
4. Compliance delay risk: unresolved legal and runbook decisions can slow
   production rollout and defer value realization.

## Decision Guidance and Next Steps

1. Use this BVA as the executive go/no-go baseline for MVP funding approval.
2. Confirm local finance assumptions for bed-day economics, staffing cost,
   and audit effort reduction.
3. Convert this ROM model into a tracked business-value dashboard with
   monthly KPI reporting.
4. Re-baseline the BVA after pilot month 2 and month 6 using observed
   operational and cost telemetry.
