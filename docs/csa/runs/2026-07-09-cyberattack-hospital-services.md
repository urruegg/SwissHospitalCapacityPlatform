---
scenarioId: cyberattack-hospital-services
runId: run-cyber-2026-07-09-demo
tier: 3
requestedBy: operations.lead
synthetic: true
---

# CSA run — Cyberattack on hospital services — 2026-07-09

| Field | Value |
| ----- | ----- |
| **Scenario** | `cyberattack-hospital-services` (F4) |
| **Requested by** | `operations.lead` (`HCC.OperationsLead`) |
| **Tier** | **3 — Ausserordentliche Lage** |
| **Rules version** | ADR-0024 v1.0.0 |
| **Data** | Synthetic (ADR-0016) — computed via `csa-simulate.simulate()` |

## Tier classification

**Tier 3 (Ausserordentliche Lage).** Ransomware degrades clinical IT, modelled as
a 30% capacity loss on critical care. ICU effective capacity drops from 20 to 14
beds against 18 occupied — **demand exceeds site capacity even after internal
levers**. This crosses the Tier 3 threshold: internal reallocation cannot absorb
the shortfall, so multi-agency escalation is required.

Rule fired: *demand exceeds site capacity even after internal levers.*

## Key impacts

- Peak utilisation **1.29**; ICU-bed shortfall **4 beds** after levers.
- Systemic IT loss cascades to throughput collapse and degraded diagnostics.
- Sudden onset; escalates beyond internal levers.

## Recommended response levers

| Lever | Rationale |
| ----- | --------- |
| `lever-fail-over-to-backup-clinical-it-systems` | Restore clinical throughput off the compromised estate. |
| `lever-activate-downtime-paper-procedures` | Maintain safe care during IT outage. |
| `lever-isolate-affected-network-segments` | Contain ransomware spread. |
| `lever-engage-cyber-incident-response-retainer` | Bring in specialist IR capacity. |
| `lever-protect-critical-care-from-it-outage-impact` | Shield ICU from the throughput collapse. |

## KPI expectations

- `throughput-reduction-pct` → recover toward baseline as failover completes.
- `icu-bed-shortfall` → clear the 4-bed gap via inter-site transfer + failover.

## Doctrine citations

- Swiss *Lage* tiers per [ADR-0024](../../adr/0024-csa-tier-classifier-rules.md);
  Tier 3 (VKSD Art. 2 — special capability / systemic overwhelm).
- Advisory only — no lever auto-executed (AGENTS.md §5).
