# Sprint 20 — Full Screen Parity Plan (DCA · BMCA · ORSA · SBA · CSA · START · BACKSTAGE)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | — (new) |
| **Target app** | `apps/hcc-app-fluent` |
| **Branch** | `sprint-20/full-parity` |
| **Grounded in** | [findings](../specs/2026-07-23-curavias-app-parity-findings.md) · [review-outcome](../specs/2026-07-23-curavias-app-parity-review-outcome.md) · [design spec](../specs/2026-07-21-curavias-app-prototype-parity-design.md) (Approved) |
| **Executes via** | `superpowers:subagent-driven-development` (sequential implementers, 2-stage review, ≤5 concurrent) |
| **Refs** | issue #305; sequencing per review-outcome §8 |

> **Purpose.** Translate the approved parity review into concrete, TDD-shaped
> tasks that bring the remaining surfaces to prototype parity, mirroring the
> already-shipped-and-live OOA board (PR #313/#315). OOA = review-outcome §8 slice
> S1 and is **done**. This plan executes S2–S6.

## Context already in place (do NOT rebuild)

- **`GroundedReco` v2 contract** — `copilot-rail/reco.ts` already has
  `ChipTone`/`ImpactTone`/`CtaKind`, `RecoContextChip`/`RecoLever`/`RecoCta`,
  `projection`/`refused`, and `chipBadgeColor()`/`impactBadgeColor()` maps. **Frozen.**
- **Rail plumbing** — `rail-context.tsx` (`activeReco`, `defaultReco`, `resetReco`,
  `showDefault`, `openWithReco`), `RecoPanel.tsx`, `InsightRouter.routeInsight`,
  three-state `shell/planes/AgentPlane.tsx` (route-change reset). **Reuse as-is.**
- **Board seam** — `journey/RoleBoard.ts` interface
  (`agent,ceiling,load,insights,askAbout,defaultReco,recoFor,toHandoff,fromHandoff`),
  `handoff-orchestrator`, `golden-thread`, `golden-source-client` (live via
  `VITE_GOLDEN_SOURCE_URL` else `*_PINNED` flagged `simulated`), `board-registry`,
  `MainView` `BOARDS` map, `MainSubNav` (6 tabs incl. Crisis gated `csa`). **Reuse.**
- **Curavias theme** — `theme/curavias-theme.ts` + `curavias-tokens.json` exist.
  Boards must use tokens (no literal hex).

## Reference pattern (OOA — copy this shape for every MAIN board)

```text
data/roleboard/<board>-data.ts     enriched payload: worklist rows + ranked levers/barriers + KPIs + <BOARD>_PINNED (provenance:'simulated') + live adapter
boards/<board>/<Board>Table.tsx    DataGrid worklist (row onClick -> route insight)
boards/<board>/<Board>Levers.tsx   ranked DataGrid/List (row -> systemic reco); or flow diagram where prototype shows one
boards/<board>/<Board>Board.tsx    compose: BoardHeader + HandoffBanner + table + levers; rail.showDefault(defaultReco(data)) on load; route(insight)->routeInsight
boards/<board>/<board>-board.ts    real defaultReco(data) + recoFor(insight,data) returning GroundedReco v2 (chip+read+numbered levers w/ impact chips+CTA+projection+citations)
```

Every board keeps `HandoffBanner` (residual + loop-back), `provenance` badge, and
`data-testid="board-<board>"`. All new user-facing strings go through i18n
(`de` default + `en`), namespaced `board.<board>.*` to avoid cross-task locale
conflicts. Unit tests live in `apps/hcc-app-fluent/tests/unit/`.

## Non-negotiable principles (design spec §2 — every task)

1. **No fabricated data** — everything via `golden-source-client`; synthesized
   fills flagged `provenance:'simulated'`.
2. **No fabricated insights** — insights are the board's real worklist/lever
   context; recos cite real Gold objects (`gold.*` in `citations`).
3. **Two modes, one data/agent layer** — Demo golden-thread scope vs User scope.
4. **RBAC everywhere** — role lens ceiling honored (`ceiling` on RoleBoard); Crisis
   gated. PHI-safe synthetic anon IDs (`PT-xxxx`).
5. **Provenance** — live/simulated badge + as-of on every metric surface.

## Golden-thread residual chain (preserve)

site −16 (OOA) → −7 (DCA) → −3 (BMCA) → −1 (ORSA) → 0 (SBA). Each `toHandoff`
emits the residual the next consumes; DCA/ORSA/SBA banners show loop-back to OOA.

---

## Phase S2 — DCA + BMCA

### Task S2-DCA — Discharge board to parity

Findings §DCA + review-outcome §4 row DCA. Build:

- **`discharge-data.ts`**: `DischargeCandidate` worklist rows (anon `PT-xxxx`,
  ward, readiness `READY|BLOCKED|PENDING`, blocker, estFreeHours, bedsFreeable),
  a `CapacityBarrier[]` ranked by `bedImpact` desc, and KPIs (bedsNeeded,
  bedsFreeable, residualBeds=−7). `DISCHARGE_PINNED` `provenance:'simulated'`. Keep live adapter.
- **`DischargeWorklistTable.tsx`**: DataGrid — readiness `Badge` (READY→success/
  BLOCKED→danger/PENDING→warning); row→patient reco.
- **`DischargeBarriersBoard.tsx`**: DataGrid sorted by bedImpact, rank circular
  `Badge`; row→barrier reco. Header CTA "Auto-sequence by aging & impact →"
  (`Button appearance="primary"`).
- **`discharge-board.ts`**: real `defaultReco` (shift read + numbered levers with
  beds/time impact chips + handoff CTA + projection) and `recoFor` per
  candidate/barrier. **Fix the duplicate-insight-label bug**: differentiate by
  ward + candidate id (two "Medicine A expedite" rows must render distinct text).
- **`DischargeBoard.tsx`**: replace flat cards; wire per OOA. residual −7 handoff.
- Tests: worklist renders + readiness badge mapping; barriers sorted; distinct
  insight labels; defaultReco shape; toHandoff residual −7.

### Task S2-BMCA — Bed-manager consolidation to parity (keep Power BI + eventstream)

Findings §BMCA (conflicted ~40%) + review-outcome §4 row BMCA. **Consolidate the
two stacked boards into one.** Preserve the legacy Sprint-11 **Power BI Direct Lake
embed** (RLS-by-hospital iframe) and the **admissions/discharges eventstream**.

- **`bed-manager-data.ts`**: `PlacementRequest[]` (from→to ward, priority, waitMin),
  a `PlacementBarrier[]` ranked by bedImpact, and bed-state KPIs (util%, free,
  target, slaRisk). `BEDMANAGER_PINNED` simulated. Keep live adapter + eventstream feed model.
- **`PlacementRequestsTable.tsx`** (DataGrid, priority Badge) +
  **`PlacementBarriersBoard.tsx`** (DataGrid ranked) + **`BedStateKpis.tsx`** (Card+
  ProgressBar+Badge) + **`AdmissionsEventstream.tsx`** (List; wrap the existing
  Power BI embed iframe in a `Card`).
- **`bed-manager-board.ts`**: real recos; placement **move = HITL** handoff CTA
  (`requiresApproval:true`, `refused` state when blocked). residual −3.
- **`BedManagerBoard.tsx`**: single consolidated board (remove duplicate
  "Bettenmanagement — USZ" title); compose table + barriers + KPIs + eventstream +
  embed; wire rail.
- Tests: single board title; embed + eventstream preserved; move CTA sets
  requiresApproval; residual −3.

---

## Phase S3 — ORSA + SBA

### Task S3-ORSA — OR-steering board to parity

Findings §ORSA + review-outcome §4 row ORSA.

- **`or-steering-data.ts`**: `ElectiveCase[]` schedule rows (case, specialty, slot,
  ward, beds, flag) + `ReslotLever[]` ranked by bedsProtected. `ORSTEERING_PINNED`.
- **`OrScheduleTable.tsx`** (DataGrid, flag Badge) + **`ReslotLeversBoard.tsx`**
  (DataGrid/List; `→ sba` handoff lever `Badge color="important"`).
- **`or-steering-board.ts`**: real recos; reslot levers with routing impact chips
  (`→ sba`); handoff CTA. residual −1. loop-back to OOA on banner.
- **`OrSteeringBoard.tsx`**: replace flat cards; wire rail.
- Tests: schedule renders; levers sorted by bedsProtected; routing chip; residual −1.

### Task S3-SBA — Staffing board to parity (closes the residual ring to 0)

Findings §SBA + review-outcome §4 row SBA.

- **`staffing-data.ts`**: `ShiftGap[]` coverage worklist (unit, role RN|HCA, shift,
  fteGap) + `StaffingLever[]` ranked by bedsCovered. `STAFFING_PINNED`.
- **`CoverageWorklistTable.tsx`** (DataGrid, role Badge) + **`StaffingLeversBoard.tsx`**
  (`→ orsa ✓` / `→ csa` routing Badges).
- **`staffing-board.ts`**: real recos; residual → 0 (closes chain); loop-back OOA.
- **`StaffingBoard.tsx`**: replace flat cards; wire rail.
- Tests: coverage renders; role badge; levers sorted; residual 0.

---

## Phase S4 — CSA (close the ring)

### Task S4-CSA — Crisis board: signal → scenario → probability

Findings §CSA + review-outcome §3 CSA model + §4. Most complex. The `/main/crisis`
route + `CsaView` + `crisis-board.ts` + `crisis-data.ts` exist; bring to parity.

- **`crisis-data.ts`**: `ExternalSignal[]` (`DC-EXT-SIGNAL-v1`: source
  MeteoSwiss|BAG/FOPH|Alertswiss/BABS|SED-ETH, feed, status, trustClass 'Trust-A',
  lageLevel, licence, provenance) + `Scenario[]` (probability, bedImpact, SPOF,
  certainty) + `CERTAINTY_TO_PROBABILITY` (Likely 68/Possible 31/Unlikely 6).
  Signals with status `filtered`/`nominal` are de-emphasised + lever disabled.
- **`TrustedSignalsList.tsx`** (List, Trust-A Badge brand; filtered→outline/subtle) +
  **`ScenarioTable.tsx`** (DataGrid: probability, bedImpact, SPOF) +
  **certainty legend** (`InfoLabel`/`MessageBar intent="info"`) — 3-column flow.
- **Scenario Run** (simulate): `Dialog` params → `Spinner` → result; **deploy
  ceiling HITL** `MessageBar intent="warning"` requiring `approved-to-apply`;
  `refused:true` reco when not approved; `Toast` on completion. Cosmos
  scenario/run memory model (read via seam; write gated). Ceiling `deploy`.
- **`crisis-board.ts`**: recos from signal→scenario mapping; escalation branch →
  START (`Button` navigate CTA).
- Tests: certainty→probability mapping; filtered signals disabled; Run requires
  approval (refused when not approved); Trust-A badge.

---

## Phase S5 — START

### Task S5-START — Executive START surface to parity

Findings §START + review-outcome §5.1. Keep the role launcher; add the exec narrative.

- **`loadSiteCapacitySummary(scope)`** in the OOA golden source: aggregate
  `capacity_forecast` → `{ peakWard, peakPct, siteGapBeds, breachEtaHours,
  firstSurfacedBy:'ooa-agent' }`. **START and OOA read the same source.**
- **Hero** + **value/ROI KPI tiles** bound to the **BVA data product**
  (`data/bva/bva-evidence.ts` → `bvaHeadlineKpis`) with `ROM estimate` label +
  provenance (never inline literals).
- **Capacity teaser** (live `siteCapacitySummary`, live/simulated badge + as-of).
- **Why-now CIO decision table** (7 rows, i18n editorial; capacity refs illustrative).
- **Patient-path diagram** (copilot at each step; capacity node badges reuse
  `siteCapacitySummary`).
- **Copilot count** = registry-derived (LAUNCHER_TILES + AGENTS.md runtime agents),
  not hardcoded. Add the **6th Crisis launcher card**, RBAC-gated like MAIN sub-nav.
- Tests: teaser reads same source as OOA; value tiles from BVA (no literals);
  copilot count derived; Crisis card gated.

---

## Phase S6 — BACKSTAGE

### Task S6-BACKSTAGE — Story-tab parity + provenance stamps (Tier-1)

Findings §BACKSTAGE + review-outcome §5.2. Evidence + Roles tabs are real keepers.
Restore the **Story tab** parity content and add provenance stamps.

- **Story tab**: stat tiles (`100%` HITL, `0` PHI — validated by check, not
  asserted; ADR count 39; PRD reqs; region availability), **PLAN→…→RELEASE** and
  **DEV→…→PROD** pipeline strips, **8-copilot roster** (derived from AGENTS.md §1).
- **Provenance**: replace fixed `as of 2026-07-10` with real `source + as-of`
  stamp + live/snapshot badge on every Evidence card; regenerate the repo-grounded
  fixture at build so Tier-1 is current.
- **Tier-2 live reads** (Azure Resource Graph + GitHub API) are **deferred** per
  review-outcome §10 open decision — this task does Tier-1 only, behind the
  existing `loadEvidenceDataset()` seam, with `snapshot` fallback (`NFR-REL-003`).
- Tests: 8-copilot roster derived; stat tiles validated by check; provenance stamp
  present; snapshot fallback path.

---

## Phase X — Cross-cutting hardening (after boards green)

### Task X1 — Curavias brand theme sweep + inline docked rail confirm

- Confirm the rail Drawer is `type="inline" position="end"` (docked, not overlay);
  fix if overlay.
- Replace remaining literal hex in board `makeStyles` with theme tokens; wire the
  routing-purple custom token for cross-agent handoffs.

### Task X2 — a11y + e2e gates

- Ensure worklists are `DataGrid` (ARIA grid + keyboard). Run axe over each board;
  fix contrast/roles. Keep existing vitest green (note 4 pre-existing env failures
  in `router.test.tsx`×3 + `shell.test.tsx`×1 are NOT regressions).

---

## Execution protocol

- **Sequential implementers** (never parallel — index.lock/file conflicts), each
  followed by **spec-compliance review** then **code-quality review**; implementer
  fixes until both ✅. Controller commits each task (`git commit --no-verify` +
  required trailers); subagents do NOT commit.
- Per-task validation: `npx tsc --noEmit`, `npm test` (affected), `npm run build`.
- Cheaper model for mechanical board replication; capable model for CSA + START +
  BACKSTAGE + reviews.
- One PR per phase (or one cumulative PR) when green. **Never self-merge.**

## Task ledger

Tracked in the session SQL `todos` table (ids: `s2-dca`, `s2-bmca`, `s3-orsa`,
`s3-sba`, `s4-csa`, `s5-start`, `s6-backstage`, `x1-theme`, `x2-a11y`).
