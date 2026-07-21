# Curavias App — Prototype Parity Design

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Approved (brainstorming) |
| **Target app** | `apps/hcc-app-fluent` |
| **Source pack** | `docs/superpowers/ideas/curavias-ux-ideas/` (locked prototype) |
| **Predecessors** | Sprint 20 (5-plane shell), Sprint 13 (agent-host), Sprint 11 (agents), Sprint 21 (Trust-A external signals), Sprint 22 (golden-source medallion) |

> **For agentic workers:** This is a design spec. The implementation plan is produced
> separately via `superpowers:writing-plans` and executed via
> `superpowers:subagent-driven-development`. The brainstorming HARD-GATE is satisfied:
> this design was approved before any production code.

---

## 1. Goal

Bring `apps/hcc-app-fluent` to **full parity with the locked Curavias UX prototype**
(3 acts — START, MAIN 6-role journey, BACKSTAGE), wiring every surface to the
**trusted data layer** and to **live agents**, so the app demonstrates the end-to-end
capacity-relief ring: **"Medicine A → 102% occupancy in 72h, site −16 beds."**

## 2. Non-negotiable principles

1. **No fabricated data.** UI components hold **zero** hardcoded domain data. All board
   data flows through the trusted-data contracts (`RoleBoard.load()` →
   `golden-source-client`, Sprint 22 medallion). Where a golden-source table is not yet
   populated, the contract is fed by **synthesized data inside the data layer**, flagged
   by the **live-vs-simulated badge** — never ad-hoc numbers hardcoded in a component.
2. **No fabricated insights.** Every actionable insight and context recommendation is a
   **live agent-host round-trip** (`agent-host-client`, Sprint 13) computed over the
   contracted data. No hardcoded insight strings or reco panels in components. If an
   agent is unavailable, the agent-host returns a **degraded/simulated response flagged
   by the badge** — the UI never fabricates its own insight.
3. **Two modes, one data/agent layer.** A header-ribbon toggle switches **only the
   handoff orchestration**, never the data source:
   - **Demo mode** — choreographed golden-thread showcase: a stateful chain carries the
     residual pressure role→role; banner + loop-back reflect the live journey and close
     the ring back to `ooa`. Demo pins a **scenario scope / time-window** over the real
     trusted data so the golden thread is reproducible (a real, selected slice — not
     fabricated figures).
   - **User mode** — real working mode: each role board is independent; banner shows real
     `fromHandoff` context only; no scripted chain.
4. **RBAC everywhere.** The role lens narrows visible acts/boards and sets each board's
   **agent action ceiling** (`read | suggest | write`), reused from the Sprint 20 model.

## 3. Navigation model (two-tier)

Top-level left nav (`NavigationPlane.tsx`) = the **3 acts** plus app-level Settings.
The 6 role surfaces are **MAIN sub-navigation**, reached via `/main/:board`.

```
START                     /start
MAIN                      /main
  ├ Occupancy   (ooa)     /main/occupancy
  ├ Discharge   (dca)     /main/discharge
  ├ Bed mgmt    (bmca)    /main/bed-manager
  ├ OR steering (orsa)    /main/or-steering
  ├ Staffing    (sba)     /main/staffing
  └ Crisis      (csa)     /main/crisis
BACKSTAGE                 /backstage
Settings (app-level)      /settings
```

**Change from today:** the current top-level `/csa` wizard is retired; crisis/scenario
becomes the 6th board under `/main/crisis`. The role lens + RBAC gate which acts/boards
are visible per role.

## 4. Module layout

Extends the existing `apps/hcc-app-fluent/src` structure and follows current patterns
(Fluent UI v9, react-router-dom v6, i18next, Vitest, Playwright/axe).

```
src/
  context/mode-context.tsx            # NEW  Demo|User, persisted, header-toggled
  shell/TopBar/ModeToggle.tsx         # NEW  ribbon control (next to RoleLensDropdown)
  journey/
    RoleBoard.ts                      # NEW  frozen per-surface contract (types)
    handoff-orchestrator.ts           # NEW  journey state machine (residual pressure)
    golden-thread.ts                  # NEW  scripted Demo scenario scope + sequence
  data/roleboard/
    golden-source-client.ts           # NEW  Sprint 22 medallion read adapters
    agent-host-client.ts              # NEW  Sprint 13 live agent round-trips
    live-simulated-badge.ts           # NEW  provenance flag surfaced by the badge
  copilot-rail/
    CopilotRail.tsx                    # NEW  full-height collapsible rail (FAB)
    InsightRouter.ts                   # NEW  clicked insight → agent → reco panel
  shell/HandoffBanner.tsx             # NEW  banner + loop-back note
  shell/planes/agent-context-map.ts   # EXTEND to all 6 roles + orchestrator + ceilings
  copilot-drawer/agent-manifest.ts    # EXTEND to all 6 agents
  workspaces/main/boards/
    occupancy/    (ooa)  NEW
    discharge/    (dca)  NEW
    bed-manager/  (bmca) REFIT to RoleBoard
    or-steering/  (orsa) NEW
    staffing/     (sba)  NEW
    crisis/       (csa)  REFIT wizard→RoleBoard
```

## 5. The `RoleBoard` contract

One frozen interface every surface implements, so sub-agents build all 6 to an identical
shape. Freezing this contract in Sprint 1 is what makes Sprints 2–6 parallelizable.

```ts
type AgentId = 'ooa' | 'dca' | 'bmca' | 'orsa' | 'sba' | 'csa';
type Ceiling = 'read' | 'suggest' | 'write';
type Provenance = 'live' | 'simulated'; // drives the live-vs-simulated badge

interface RoleBoardData {
  provenance: Provenance;              // from the data layer, not the component
  scope: ScenarioScope;                // hospital(s) + time-window (pinned in Demo)
  payload: unknown;                    // board-specific, contract-typed per role
}

interface ContextInsight {
  id: string;
  label: string;                       // e.g. "Medicine A rising"
  context: Record<string, unknown>;    // sent to the agent on click
}

interface ResidualPressure {           // what a role passes to the next (Demo)
  fromAgent: AgentId;
  headline: string;                    // e.g. "site −16 beds"
  metrics: Record<string, number>;
}

interface BannerContext {              // what the banner shows (both modes)
  situation: string;
  loopBackToOoa: boolean;
}

interface RoleBoard {
  agent: AgentId;
  ceiling: Ceiling;
  load(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData>; // golden-source read
  insights(data: RoleBoardData): ContextInsight[];               // rendered as clickable
  toHandoff(data: RoleBoardData): ResidualPressure;              // Demo chain output
  fromHandoff(prev: ResidualPressure | null): BannerContext;     // banner input
}
```

Insight recommendations are **not** part of the contract payload — they are fetched at
click time by `InsightRouter` via `agent-host-client`, keeping the "no fabricated
insights" rule enforceable at the seam.

## 6. Data flow

```
Header ModeToggle ─┐
                   ▼
          ModeContext (Demo | User)
                   │
   role lens + hospital scope ──► ScenarioScope
                   │
   RoleBoard.load(scope, mode) ──► golden-source-client ──► RoleBoardData{provenance}
                   │                                              │
                   ▼                                              ▼
        Board UI renders payload                        live-vs-simulated badge
                   │
   click ContextInsight ──► InsightRouter ──► agent-host-client(agent, context)
                   │                                     │
                   ▼                                     ▼
        CopilotRail opens (FAB)                 real agent reco (or badged degraded)

  Demo only:  toHandoff() ──► handoff-orchestrator ──► next role's fromHandoff()
              ... ooa → dca → bmca → orsa → sba → csa → loop-back to ooa
  User mode:  orchestrator inert; fromHandoff(null) → real context banner only
```

## 7. Agent wiring

- `agent-context-map.ts` expands from the current 4-entry route map to the full
  role→agent map: `/main/occupancy→ooa`, `/main/discharge→dca`,
  `/main/bed-manager→bmca`, `/main/or-steering→orsa`, `/main/staffing→sba`,
  `/main/crisis→csa`; START/BACKSTAGE/Settings fall through to `orchestrator`.
- Each entry carries the RBAC **action ceiling** for the current role lens.
- `agent-manifest.ts` expands from the current `bmca-agent` stub to all 6 agents.
- `csa` additionally consumes **trusted external + internal signals → scenarios →
  probability** using the Sprint 21 Trust-A design (`DC-EXT-SIGNAL-v1`: MeteoSwiss,
  Alertswiss/BABS, SED-ETH, BAG/FOPH; certainty→probability mapping).

## 8. Sprint roadmap (Approach B — walking-skeleton hybrid)

**Sprint 1 — Foundation + `ooa` walking skeleton** *(prerequisite for all)*
Build L0–L3 once + the first real role end-to-end. Deliverables: `ModeContext` +
`ModeToggle`; `CopilotRail` (FAB) + `HandoffBanner` + `InsightRouter`; `RoleBoard`
contract + `golden-source-client` + `agent-host-client` seam + `live-simulated-badge`;
`handoff-orchestrator` + `golden-thread` scaffold; two-tier navigation (retire top-level
`/csa`); expand `agent-context-map` to 6 roles + `agent-manifest`; **Occupancy (ooa)
board fully wired** — real data + live agent insights + banner + both modes. Proves the
entire stack is demoable and **freezes the `RoleBoard` contract**.

| Sprint | Scope | Sub-agent shape | Depends on |
|--------|-------|-----------------|------------|
| **1** | Foundation + **ooa** walking skeleton | 1 driver (heavy) | — |
| **2** | **dca** (new) + **bmca** (refit→contract) | 2 parallel role tasks | S1 |
| **3** | **orsa** (new) + **sba** (new) | 2 parallel role tasks | S1 |
| **4** | **csa** (refit wizard→board) + close the ring + csa signal→scenario→probability (Sprint 21 Trust-A) | 1 role + chain closeout | S1 (+S2/S3 for full chain) |
| **5** | **START** act — exec/persona entry, role launcher, live-vs-sim badge | 1 task | S1 |
| **6** | **BACKSTAGE** act — C-level KISS (built-by-agents, Fabric+FHIR, DSG, DEV→SIT→PROD) | 1 task | S1 |

**Parallelism for sub-agents:** after Sprint 1 freezes the `RoleBoard` contract, Sprints
2–3 (and 5–6) are independent tasks a fresh sub-agent can own end-to-end; each role has an
identical shape (board UI + `load()` binding + agent wiring + insights + banner). Sprint 4
performs light chain-integration coordination.

## 9. Testing strategy

Follows the existing Vitest + Playwright/axe patterns in `apps/hcc-app-fluent`.

- **Unit (Vitest):** `RoleBoard` contract conformance per role; `load()` data binding;
  `handoff-orchestrator` state transitions (residual pressure carried correctly);
  `agent-context-map` route→agent + ceiling; `InsightRouter` sends context and renders
  the agent response. `agent-host-client` and `golden-source-client` are mocked at the
  client boundary.
- **E2E (Playwright + axe):** each surface renders; Mode toggle switches handoff behavior
  (Demo chain vs User independent); HandoffBanner shows carried situation in Demo and real
  context in User; navigation two-tier works; a11y passes on every surface.
- **Reproducibility:** Demo mode uses the pinned `golden-thread` scenario snapshot so the
  showcase is deterministic while still reading through the trusted-data contract.
- **One live smoke e2e** exercises a real `agent-host` round-trip on the `ooa` board.

## 10. Out of scope

- Backend/agent implementation changes (agents come from Sprint 11/13; this effort wires
  the app to them).
- Golden-source medallion population (Sprint 22 owns the data; where absent, the layer
  serves badged synthesized data).
- Production deployment/hosting changes for the app.

## 11. Open items / assumptions

- `ScenarioScope` shape (hospital selector + time-window) reuses the existing
  `hospital-context` + a Demo-pinned window; exact fields finalized in Sprint 1.
- `agent-host-client` transport (REST vs existing `AgentInvoker`) is confirmed against the
  Sprint 13 host contract in Sprint 1 before the contract freezes.
- START and BACKSTAGE act layouts reuse the deferred prototype intent; detailed mock is
  produced at the start of Sprints 5/6 respectively.
