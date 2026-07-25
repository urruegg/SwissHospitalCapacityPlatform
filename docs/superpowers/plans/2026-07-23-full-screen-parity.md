# Sprint 20 — Full Screen Parity Plan (DCA · BMCA · ORSA · SBA · CSA · START · BACKSTAGE)

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Delivered (merged) — e2e hotfix in review (PR #355); SIT deploy pending |
| **Previous Version** | 1.0.0 (initial plan, Draft) |
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

---

## Delivery status (as executed) — 2026-07-24

### What shipped

| Phase | Task | Status | Evidence |
|-------|------|--------|----------|
| S2 | DCA discharge board | ✅ Done | PR #352 (`80de85e`) |
| S2 | BMCA bed-manager consolidation (Power BI + eventstream preserved) | ✅ Done | PR #352 |
| S3 | ORSA OR-steering board | ✅ Done | PR #352 |
| S3 | SBA staffing board (residual ring → 0) | ✅ Done | PR #352 |
| S4 | CSA crisis board (signal → scenario → probability, HITL Run) | ✅ Done | PR #352 |
| S5 | START executive surface (BVA tiles, capacity teaser, why-now, patient-path) | ✅ Done | PR #352 (`2f05f93`) |
| S6 | BACKSTAGE Story-tab parity + provenance stamps (Tier-1) | ✅ Done | PR #352 (`04035b9`) |
| X1 | Curavias theme sweep + inline-docked rail | ✅ Done (rail already inline-docked; teal theme pre-existing; `routing-purple` token **deferred** — handoffs already distinguished via MessageBar + loop icon + provenance badge) | PR #352 (`be56d0c`) |
| X2 | a11y + e2e gates | ✅ Done (Space-key `preventDefault()` fixed on all 4 tables; axe green on 5 surfaces) | PR #352 (`be56d0c`) |

**PR #352** — `feat(hcc-app-fluent): Sprint 20 full screen parity (…)` — **MERGED**
to `main` at `80de85e` (2026-07-24T03:59:48Z). All S2–S6 + X1–X2 boards delivered.

### Regression found + fixed (post-merge)

The #352 merge turned `main` **red on `app-e2e`** — this gate was never run locally
during the sprint (only vitest + `npm run build`), so the failure slipped through.
Three root causes, all fixed in **PR #355** (`sprint-20/fix-e2e-testid`, **open, not
self-merged**):

1. **Strict-mode testid collision** — `MainView` wrapped `<BedManagerBoard/>` in a
   `data-testid="board-bed-manager"` div while the board `<section>` reuses the same
   id → `getByTestId('board-bed-manager')` matched 2 elements. Wrapper renamed to
   `board-bed-manager-slot` (the established `-slot` pattern). The **latent crisis
   duplicate** (`CsaView` conditional panel vs. `MainView` `board-crisis` wrapper)
   fixed the same way: panel → `board-crisis-panel`.
2. **Stale `smoke.spec.ts`** — asserted the removed whiteboard `data-card-type`
   cards; rewritten to the new bmca surface (board root + Power BI embed + worklist).
3. **Stale `copilot-drawer-bmca.spec.ts`** — clicked the removed per-board "BMCA
   fragen" drawer; rewritten to open the inline-docked `AgentPlane` and assert the
   grounded `HITL-02` reply + `gold.` citations.

Validation after fix: **13/13 Playwright e2e pass** (was 11/2); **394 unit pass**
(the 4 failing `router.test.tsx`×3 + `shell.test.tsx`×1 are pre-existing jsdom/undici
env failures, unchanged); `tsc` clean.

### SIT deployment status — NOT yet showing full parity

- `appsit.curavias.ch` serves bundle **`index-JxSB0PJl.js`** = image
  **`hcc-app-fluent:cb21e2c`** (the **OOA-only** parity slice from PR #315,
  2026-07-23). Pinned in `infra/environments/sit.bicepparam:179`.
- The full-parity work (PR #352, `80de85e`) is **merged to `main` but NOT deployed
  to SIT** — the `appFluentImage` tag has not been bumped past `cb21e2c`.
- **SIT deploy is a deliberate manual, human-gated step** (per
  `sit.bicepparam:170-171`): `ci-build-app-fluent.yml` pushes a new image tag to
  ACR → bump `appFluentImage` in `sit.bicepparam` → run `cd-infra-deploy-sit.yml`.
  There is **no CI workflow that auto-deploys the Fluent app** to SIT.

## Next steps (sprint close-out)

1. **Merge PR #355** to make `main` green on `app-e2e` (do not self-merge — awaiting review/approval).
2. **Build + push** a new `hcc-app-fluent` image from the post-#355 `main` commit via `ci-build-app-fluent.yml`.
3. **Bump `appFluentImage`** in `infra/environments/sit.bicepparam` to the new tag and run `cd-infra-deploy-sit.yml` (human-gated Azure deploy).
4. **Validate SIT parity** at `appsit.curavias.ch/main` — confirm the new bundle hash + walk the 6 boards + START + BACKSTAGE against the prototype baseline (Playwright against the live SIT URL).
5. **Deferred / follow-up** (not blockers): `routing-purple` cross-agent handoff token (X1); BACKSTAGE Tier-2 live reads (Azure Resource Graph + GitHub API) per review-outcome §10; consider adding a lightweight `app-e2e` pre-merge gate reminder so the Playwright suite is run locally before future app PRs.
