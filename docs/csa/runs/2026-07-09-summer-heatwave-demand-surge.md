---
scenarioId: summer-heatwave-demand-surge
runId: run-heatwave-2026-07-09-demo
tier: 2
requestedBy: crisis.manager
synthetic: true
---

# CSA run — Summer heatwave demand surge — 2026-07-09

| Field | Value |
| ----- | ----- |
| **Scenario** | `summer-heatwave-demand-surge` (F8) |
| **Requested by** | `crisis.manager` (`HCC.CrisisManager`) |
| **Tier** | **2 — Besondere Lage** |
| **Rules version** | ADR-0021 v1.0.0 |
| **Data** | Synthetic (ADR-0016) — computed via `csa-simulate.simulate()` |

## Tier classification

**Tier 2 (Besondere Lage).** A prolonged heatwave drives a +20% general-bed
demand shock. Bed utilisation reaches **102%** (261 occupied vs 300 capacity),
breaching the 90% threshold and requiring internal reallocation and flow levers.
The breach is modest and single-site — no special capability is overwhelmed — so
it stays Besondere Lage.

Rule fired: *beds utilization 102% breaches threshold 90% — internal
reallocation required.*

## Key impacts

- Peak utilisation **1.02**; general-bed shortfall **6 beds**.
- ED crowding from walk-in cardiorespiratory presentations.
- Gradual onset over ~7 days.

## Recommended response levers

| Lever | Rationale |
| ----- | --------- |
| `lever-accelerate-discharge-of-medically-fit-patients` | Free the 6-bed shortfall via early discharge. |
| `lever-activate-discharge-lounge` | Decouple discharge from bed turnover. |
| `lever-mobilise-spitex-for-discharge-support` | Enable safe home discharge for elderly patients. |
| `lever-redirect-walk-ins-to-urgent-care-partners` | Relieve ED crowding. |

## KPI expectations

- `bed-shortfall` → target ≤ 0 after discharge levers.
- `ed-occupancy-pct` → back below threshold as walk-ins are redirected.

## Doctrine citations

- Swiss *Lage* tiers per [ADR-0021](../../adr/0021-csa-tier-classifier-rules.md).
- Advisory only — no lever auto-executed (AGENTS.md §5).
