# Curavias UX Ideas - Brainstorming Source Pack

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-20 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | - (new document) |

> **Purpose**: Committed source pack for the Curavias / Swiss Hospital Capacity
> Platform end-to-end demo UX. These artefacts are the output of a Superpowers
> brainstorming session and are the hand-off source for a separate design + plan
> sprint. Nothing here is production code - the brainstorming HARD-GATE applies
> until a design is written and approved via `writing-plans`.

## Overview

The session refined the end-to-end demo showcase UX, reusing the Sprint 20 UX
mockup as the visual baseline. The golden thread that flows through every role is:

> **"Medicine A -> 102% occupancy in 72h, site -16 beds"**

Each role picks up the same situation from the previous role, acts on it through a
context-based Copilot rail, and hands the residual pressure to the next role -
closing a 6-role capacity-relief ring.

## Demo information architecture (3 acts)

| Act | Purpose | Status |
|-----|---------|--------|
| **START** | Exec vs persona entry, role launcher, live-vs-simulated badge | Not built (deferred) |
| **MAIN** | The functional capacity-relief journey (6 role surfaces) | Complete - all 6 surfaces locked |
| **BACKSTAGE** | C-level KISS view (built-by-agents, Fabric + FHIR, DSG, DEV->SIT->PROD) | Not built (deferred) |

## MAIN journey - 6-role capacity-relief chain

| # | Agent | Role lens | Mockup | Screenshot | Status |
|---|-------|-----------|--------|------------|--------|
| 1 | ooa | Foresight - 72h occupancy forecast surfaces the pressure | `mockups/07-occupancy-actionable-v1.html` | `screenshots/1-ooa-occupancy-actionable.png` | Locked |
| 2 | dca | Discharge - rank systemic barriers to free beds | `mockups/09-discharge-barriers-board-v1.html` | `screenshots/2-dca-discharge-barriers.png` | Locked |
| 3 | bmca | Bed management - place freed beds, ED boarders, transfers | `mockups/10-bed-management-v1.html` | `screenshots/3-bmca-bed-management.png` | Locked |
| 4 | orsa | OR steering - protect the plan, reslot electives feeding Med A | `mockups/11-or-steering-v1.html` | `screenshots/4-orsa-or-steering.png` | Locked |
| 5 | sba | Staffing balance - match staff to the capacity plan | `mockups/12-staffing-balance-v1.html` | `screenshots/5-sba-staffing-balance.png` | Locked |
| 6 | csa | Crisis / scenario - pressure-test the committed relief | `mockups/13-crisis-scenario-v1.html` | `screenshots/6-csa-crisis-scenario.png` | Locked |

## Key interaction patterns (settled)

- **Full-height collapsible Copilot rail** - a FAB in the bottom-left/right corner
  opens a rail that spans the full height of the two role insight columns. Two
  states: open (context reco) and closed (icon-only overlay).
- **Actionable context-based insights** - clicking a role insight (for example
  "Medicine A rising") routes the Copilot to a matching recommendation panel and
  auto-opens the rail if collapsed. Recommendations are systemic, not single-metric.
- **Handoff banner** - each surface leads with a banner carrying the situation
  forward from the previous role, and closes with a loop-back note to the ooa forecast.

## Signal-flow enrichment (ooa + csa)

- **ooa** reuses a 3-column "signal channels" capacity-flow block.
- **csa** replaces channels with **trusted external + internal signals** mapped to
  **potential scenarios** and **probability**, then keeps the shock stress-test
  queue and resilience board below. External signals follow the Trust-A design in
  [`docs/superpowers/specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md`](../../specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md)
  (MeteoSwiss, Alertswiss/BABS, SED-ETH, BAG/FOPH; `DC-EXT-SIGNAL-v1` contract;
  certainty -> probability mapping).

## Folder contents

| Path | Description |
|------|-------------|
| `sprint-20-curavias-ux-mockup.html` | Committed Sprint 20 baseline (starting point) |
| `mockups/` | Full working set of brainstorming surfaces (all iterations, as source) |
| `screenshots/` | Full-page renders of the 6 locked MAIN surfaces |
| `README.md` | This index |

## Hand-off note

This pack is **brainstorming source**, not an approved design. Next steps (separate
sprint):

1. Present the full 6-role design and capture approval.
2. Write the design spec to `docs/superpowers/specs/`.
3. Transition to `writing-plans` for the implementation plan.

Deferred within the brainstorming track: START act mock, BACKSTAGE KISS mock.
UX ownership sits with the `ux-design-agent` ([`agents/ux-design-agent/AGENT.md`](../../../../agents/ux-design-agent/AGENT.md)).
