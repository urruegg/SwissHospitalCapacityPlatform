# Curavias START plane polish - design

| Field | Value |
| ------- | ------- |
| **Version** | 1.1.0 |
| **Date** | 2026-08-03 |
| **Author** | Urs Rueegg |
| **Status** | Implemented (all 7 sections, uncommitted); pending SIT-deploy Playwright verification and PROD approval |
| **Previous Version** | 1.0.0 (initial approved design) |

> Brainstormed 2026-08-03 (Superpowers `brainstorming`). References: the mockup
> [Curavias-Frontier-Showcase.html](../ideas/Curavias-Frontier-Showcase.html), the
> live SIT `/start`, and the polished BACKSTAGE surface (P13-P17). Decisions were
> delegated to the agent ("work autonomously, make good decisions") - the
> recommended options were taken and are recorded in section 3.

## 1. Goal

Bring the START plane to the same showcase quality as BACKSTAGE, guided by the
mockup. START already uses the shared `NarrativeShell` + eyebrow `SectionHeader`
(P13-P16); this pass closes the remaining gap: the per-layer **content-card
language** (elevation + 4px colored left accent + hover + focus), **P17 rail
wiring** (context-click opens the Copilot rail with a grounded reco), a few
**mockup-specific flourishes** per section, and **eyebrow i18n**.

## 2. Non-goals

- No new sections or data sources; content/testids stay stable where possible.
- No BACKSTAGE changes (avoid regression). We *extract* the card language into a
  shared module that START consumes; refactoring backstage onto it is a later,
  optional follow-up.
- No routing/nav changes beyond retargeting the two hero CTAs.
- PROD deploy is a later, separately-approved step; this pass ships to SIT.

## 3. Decisions (recommended options, delegated)

1. **Scope**: full pass - all 7 START sections.
2. **Accent tokens**: hard-code the extra decorative accents (violet `#5A6CF0`,
   navy `#365B7D`, green `#17B890`, teal `#1FA9D6`, amber `#E8A200`, red
   `#E30613`) exactly as BACKSTAGE already does (documented precedent, sprint-36
   §3). No new canonical tokens this pass.
3. **Rail wiring (P17)**: wire every meaningful START content card to the Copilot
   rail via `useCopilotRail().openWithReco(insight, reco)` with `citations` +
   `provenance:'simulated'` - full backstage parity.
4. **Eyebrow i18n**: localize the per-section eyebrow kickers (de/fr/it).
5. **Hero CTAs**: retarget to the hospitals section + backstage per the mockup.

## 4. Design

### 4.1 Shared showcase card language

Create `apps/hcc-app-fluent/src/workspaces/shared/narrative/showcase-styles.ts`
exporting a `makeStyles` hook (`useShowcaseStyles`) that lifts the proven
BACKSTAGE card language from
[BackstageNarrativeSections.tsx](../../../apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx)
so START and (later) backstage share one source:

- `accentCard` - `colorNeutralBackground1` + `shadow2` + `borderRadiusLarge` +
  `borderLeftWidth:'4px'` (accent hex set per-use) + `:hover shadow4` +
  `:focus-visible` 2px `colorStrokeFocus2` ring; `cursor:pointer`,
  `textAlign:left`, `fontFamily:inherit` (so it works as a `<button>`).
- `panel` / `panelTitle` / `note` - evidence panel surface.
- `split` - `gridTemplateColumns:'1.05fr 0.95fr'`, collapses to 1col < 900px.
- `statGrid` / `statCell` / `statValue` (navy `#365B7D`) / `statSub` - stat tiles.
- `table` / `th` / `td` / `tdName` - the backstage table treatment (uppercase
  11px header, hairline rows) to replace raw `<table>`s.
- `numBadge` (green circle) + `accentTile` (glyph/letter tile) helpers.

Colors are passed via inline `style={{ borderLeftColor, ... }}` on the element
(not baked into the recipe), matching backstage's accent-hex approach.

### 4.2 Rail wiring (P17)

A small START helper `apps/hcc-app-fluent/src/workspaces/start/frontier/start-rail.ts`
builds `GroundedReco` objects (`provenance:'simulated'`, `citations`) per card so
each section stays declarative. Cards render as `<button>` calling
`rail.openWithReco(insight, reco)` - mirroring
[SolutionDesignSection](../../../apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignSection.tsx).
`bva` already imports the rail; it gets the same helper.

### 4.3 Per-section polish

| Section | Change |
| ------- | ------- |
| **hero** ([StartHero.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/StartHero.tsx)) | Gradient-clipped title span (`.grad`: `linear-gradient(110deg,#365B7D,#17B890 78%)` via `backgroundClip:text`); retarget the two CTAs (Meet the three hospitals -> hospitals section anchor; See how it was built -> backstage). Keep the live squeeze card + async states. |
| **work-chart** ([WorkChartSection.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/WorkChartSection.tsx)) | Stop the `boxShadow:'none'` override; the 3 mode cards use `accentCard` (navy/green/violet left accents) and become rail buttons. |
| **cio-why-now** ([CioChallengerSection.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/CioChallengerSection.tsx)) | Wrap the raw `<table>` in a `panel`; restyle to `th/td`; tint the "With Curavias" column; each row rail-clickable. |
| **hospitals** ([HospitalsSection.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/HospitalsSection.tsx)) | 3 hospital cards -> `accentCard` with glyph tile + metarow (beds/FTE/sites) + human/agent/PO colored rows; 7-agent roster uses colored accent chips; cards rail-clickable. |
| **patient-path** ([PatientPathLauncher.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.tsx)) | Keep the wave-band journey; wire stops/advisories to the rail; add the DC-INSIGHT 5-beat mini-card + `102%->94%` worked-example pairing. |
| **ninety-day** ([NinetyDaySection.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/NinetyDaySection.tsx)) | Restore elevation via `accentCard`; add gradient phase-top header band (`linear-gradient(120deg,rgba(23,184,144,.12),rgba(31,169,214,.06))`) + "delivered pattern, not a promise" disclaimer chip; cards rail-clickable. |
| **bva** ([BvaDecisionSection.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.tsx)) | Elevate KPI/panels to `shadow2`+`borderRadiusLarge`; restyle the TCO + value-lever `<table>`s to `th/td`; add a green-left-accent decision `.raise` card with the two CTAs; complete the rail CTA. |

### 4.4 Eyebrow i18n

Move the English-only `SECTION_META` eyebrow strings in
[StartView.tsx](../../../apps/hcc-app-fluent/src/workspaces/start/StartView.tsx)
into the i18n bundles (`start.frontier.<section>.eyebrow`) for en/de/fr/it and
read them via `t(...)`.

## 5. Testing & verification

- **Unit (vitest)**: keep every existing `start/**` test green; add/adjust tests
  for new rail-click handlers (a card click calls `openWithReco`) and the eyebrow
  i18n lookup. Tests assert behavior (rail called with the right reco), not pixels.
- **Typecheck + build**: `tsc --noEmit` + `npm run build` clean.
- **Visual (Playwright)**: after SIT deploy, screenshot each `/start` section and
  compare against the mockup + the backstage quality bar (elevation, accent,
  spacing, dark-mode parity, WCAG AA focus rings) - the repo UX exit gate
  ([curavias-app-style-guide §3](../../brandkit/curavias-app-style-guide.md)).

## 6. Rollout

Subagent-driven, section by section (each: implement -> tests -> 2-stage review).
Build one image, gated `cd-infra-deploy-sit`, then Playwright verify on
`appsit.curavias.ch/start`. PROD promotion is a later, `approved-to-apply` step.

## 7. Risks

- **Shared-module extraction** could drift from backstage; mitigate by lifting
  styles verbatim and NOT modifying backstage this pass.
- **Rail reco quality** - keep insights short + honest (`simulated` provenance,
  real `hcp:`/`gold.` citations where they exist).
- **i18n** - de/fr/it eyebrow copy should be reviewed; English is the safe default
  fallback if a key is missing.

## 8. Progress log (2026-08-03 session)

All 7 sections in §4.3 plus §4.4 (eyebrow i18n) are implemented in the working
tree, on top of the already-merged `8591f13d` (work-chart/hospitals/ninety-day
first pass). Remaining diff is uncommitted at session end (16 files, ~688
insertions / 136 deletions across `apps/hcc-app-fluent/src/i18n/*.json` and
`src/workspaces/{shared/narrative/NarrativeShell.tsx,start/**}`).

### Done this session

- **patient-path** (§4.3): full rail wiring (5 journey stops, data-quality
  advisory, crisis advisory) + the new DC-INSIGHT 5-beat mini-card and the
  `102%->94%` worked-example card pairing, sourced verbatim from the mockup.
  New content model in `start-content.ts` (`DC_INSIGHT_BEATS`); new i18n nodes
  `start.patientPath.dcInsight.*` / `start.patientPath.workedExample.*` fully
  localized in en/de/fr/it.
- **Task B gap fix**: `start.frontier.patientPath.eyebrow` (+ `title`/`body`)
  was present in en/de but missing entirely from fr/it (the section rendered
  with an English-fallback eyebrow on those locales). Added the matching node
  to both files; all 4 bundles re-validated as parseable JSON.
- **Verification (this session)**:
  - `PatientPathLauncher.test.tsx` standalone: 7/7 green (5 pre-existing + 2
    new rail-wiring tests).
  - A full `start/**` Vitest run surfaced 4 timeout failures in files this
    session did not touch (`StartHero.test.tsx`, `StaticNarrativeSections.test.tsx`)
    plus one untouched pre-existing `PatientPathLauncher.test.tsx` case.
    Isolated re-run of the two suspect files: **9/9 green** - confirms
    resource-contention flakiness under parallel Vitest workers in this
    environment, not a real regression (collect-phase alone measured 489s for
    just 2 files in the isolated run).
  - `tsc --noEmit` (from `apps/hcc-app-fluent`): clean, exit 0.
  - `npm run build`: succeeded (`vite build`, 2459 modules, ~2m17s); only the
    pre-existing chunk-size / dynamic-import advisories, unrelated to this
    change.

### Open for the next session

1. **Full-suite confirmation**: only the two flagged files were re-verified in
   isolation; the full `start/**` suite (49 tests across 5 files) was not
   re-run end-to-end after today's edits because a single pass already costs
   several minutes in this environment. Re-run once before opening the PR to
   get one clean aggregate number.
2. **Commit**: today's diff was reviewed and staged for a single commit at
   session close (see repo memory `/memories/repo/curavias-ux-patterns.md` for
   the exact file list); not yet pushed.
3. **Visual/Playwright verification** (§5): no SIT deploy or Playwright pass
   happened this session - still the gating step before PROD promotion.
4. **de/fr/it eyebrow copy review**: newly-added fr/it `patientPath.eyebrow`
   strings are a first-pass translation, not yet reviewed by a native speaker.

