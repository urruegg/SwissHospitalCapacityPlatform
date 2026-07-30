# Curavias DFL v5 + Product Owner Agent + Backstage narrative — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Backstage Digital Feedback Loop to the approved v5 mockup with the right panel as the live Product Owner Agent grounded answer, inside a reusable vertical-narrative Backstage shell.

**Architecture:** A shared `NarrativeShell` (intro header + sticky Fluent `TabList` section nav + scrollspy) stacks self-describing sections (`SectionHeader` = header + tagline + description). The DFL section renders a v5 loop (4 domain cards + Microsoft IQ core + SMIL-animated signal/action/outcome flows) beside a `PoAgentPanel` that renders the existing `GroundedReco` via `RecoPanel`, updating on domain select, with "Open in Copilot" to expand the docked rail.

**Tech Stack:** React 18 + TypeScript, Fluent UI v9 (`@fluentui/react-components`, griffel `makeStyles`), react-router, react-i18next, Vitest + Testing Library. SMIL `animateMotion` for the flow dots.

**Design source:** `docs/superpowers/specs/2026-07-30-curavias-dfl-po-agent-refine-design.md`; visual target `docs/superpowers/ideas/digital-feedbackloop/digital-feedback-loop-final.html`.

---

## File structure

Base path: `apps/hcc-app-fluent/src/`

- Create: `workspaces/shared/narrative/SectionHeader.tsx` — header + tagline + description block.
- Create: `workspaces/shared/narrative/useScrollSpy.ts` — `IntersectionObserver` hook returning the active anchor id.
- Create: `workspaces/shared/narrative/NarrativeShell.tsx` — intro header + sticky `TabList` + scrollspy + stacked sections; smooth scroll (instant under reduced motion); honours a `#anchor` / legacy `:widget` deep-link.
- Create: `workspaces/backstage/tabs/story/feedback-loop/build-reco.ts` — `buildReco(domain, t)` + `buildInsight(domain, label)` extracted from `DigitalFeedbackLoopSection`.
- Create: `workspaces/backstage/tabs/story/feedback-loop/feedback-loop-detail.ts` — per-domain phase/detail copy + BVA value mapping.
- Create: `workspaces/backstage/tabs/story/feedback-loop/PoAgentPanel.tsx` — inline PO Agent answer (`RecoPanel`) + "Open in Copilot".
- Modify: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.tsx` — rebuild loop to v5.
- Modify: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoopSection.tsx` — compose `SectionHeader` + loop + `PoAgentPanel`; use `build-reco`.
- Modify: `workspaces/backstage/BackstageView.tsx` — `NarrativeShell` with stacked sections (DFL, Opportunities).
- Modify: `workspaces/backstage/BackstageSubNav.tsx` — export the section registry consumed by `NarrativeShell` (nav rendered by the shell).
- Modify: `i18n/en.json` — section headers/taglines/descriptions, DFL v5 copy, PO panel, journey, note.
- Tests: `DigitalFeedbackLoop.test.tsx` (update), `tests/unit/backstage-view.test.tsx` (update), `tests/unit/po-agent-panel.test.tsx` (new), `tests/unit/narrative-shell.test.tsx` (new).

---

## Task 1: Extract `buildReco` into a shared helper

**Files:**

- Create: `workspaces/backstage/tabs/story/feedback-loop/build-reco.ts`
- Modify: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoopSection.tsx`
- Test: `tests/unit/po-agent-panel.test.tsx` (added in Task 3)

Interface:

```ts
import type { TFunction } from 'i18next';
import type { ContextInsight } from '../../../../../journey/RoleBoard';
import type { GroundedReco } from '../../../../../copilot-rail/reco';
import { type FeedbackLoopDomain } from './feedback-loop-model';

export function buildInsight(domain: FeedbackLoopDomain, label: string): ContextInsight;
export function buildReco(domain: FeedbackLoopDomain, label: string, t: TFunction): GroundedReco;
```

- [ ] **Step 1:** Move the existing `buildInsight` + `buildReco` bodies verbatim from `DigitalFeedbackLoopSection.tsx` into `build-reco.ts`, exporting both. Keep the same `GroundedReco` shape (agentLabel `product-owner-agent`, contextChip, read, levers, citations, provenance `simulated`, followUps).
- [ ] **Step 2:** In `DigitalFeedbackLoopSection.tsx`, import `buildInsight`/`buildReco` from `./build-reco` and delete the inline copies.
- [ ] **Step 3:** Typecheck. Run: `npx tsc --noEmit`. Expected: no errors.
- [ ] **Step 4:** Commit `refactor(dfl): extract buildReco/buildInsight into build-reco helper`.

---

## Task 2: Per-domain detail + business-value map

**Files:**

- Create: `workspaces/backstage/tabs/story/feedback-loop/feedback-loop-detail.ts`

```ts
import { type FeedbackLoopDomainId } from './feedback-loop-model';

export interface DomainDetail {
  kicker: string;   // category, e.g. 'Command center'
  signal: string;   // "Signal packets arrive" description
  iq: string;       // "Microsoft IQ makes sense" description
  action: string;   // "Action returns" description
  outcome: string;  // "Outcome closes the loop" description
  /** Grounded BVA value line where one exists; undefined => qualitative only. */
  value?: { label: string; figure: string };
}

export const DOMAIN_DETAIL: Record<FeedbackLoopDomainId, DomainDetail>;
```

- [ ] **Step 1:** Populate the four domains with the v5 copy (from the final mockup's `detail` map): care-ecosystem, command-center, frontier-workforce, care-innovation.
- [ ] **Step 2:** For `command-center`, add a `value` line sourced from `data/bva/bva-evidence` (`bvaHeadlineKpis`) where a defensible figure exists; leave others `undefined` (qualitative). Never invent numbers.
- [ ] **Step 3:** Typecheck. Run: `npx tsc --noEmit`. Expected: no errors.
- [ ] **Step 4:** Commit `feat(dfl): per-domain detail + BVA value map`.

---

## Task 3: `PoAgentPanel` — inline Product Owner Agent answer

**Files:**

- Create: `workspaces/backstage/tabs/story/feedback-loop/PoAgentPanel.tsx`
- Test: `tests/unit/po-agent-panel.test.tsx`

Props: `{ domain: FeedbackLoopDomain; onOpenInCopilot: (domain: FeedbackLoopDomain) => void }`.

Renders (inside an `aria-live="polite"` region): the phase kicker + title from `DOMAIN_DETAIL`, a `RecoPanel` fed by `buildReco(domain, label, t)` (read → levers → citations), the value line when present, a `SIMULATED` status footer, and a primary "Open in Copilot" button calling `onOpenInCopilot(domain)`.

- [ ] **Step 1: Write the failing test** `tests/unit/po-agent-panel.test.tsx`:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { vi, describe, it, expect } from 'vitest';
import '../../src/i18n';
import { PoAgentPanel } from '../../src/workspaces/backstage/tabs/story/feedback-loop/PoAgentPanel';
import { FEEDBACK_LOOP_DOMAINS } from '../../src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model';

it('renders the grounded PO Agent answer and opens the rail', () => {
  const onOpen = vi.fn();
  const flow = FEEDBACK_LOOP_DOMAINS.find((d) => d.id === 'command-center')!;
  render(
    <FluentProvider theme={webLightTheme}>
      <PoAgentPanel domain={flow} onOpenInCopilot={onOpen} />
    </FluentProvider>,
  );
  expect(screen.getByTestId('po-agent-panel')).toHaveAttribute('aria-live', 'polite');
  expect(screen.getByTestId('citations')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: /open in copilot/i }));
  expect(onOpen).toHaveBeenCalledOnce();
});
```

- [ ] **Step 2:** Run: `npx vitest run tests/unit/po-agent-panel.test.tsx`. Expected: FAIL (module not found).
- [ ] **Step 3:** Implement `PoAgentPanel.tsx` reusing `RecoPanel` + `buildReco` + `DOMAIN_DETAIL`.
- [ ] **Step 4:** Run the test. Expected: PASS.
- [ ] **Step 5:** Commit `feat(dfl): inline Product Owner Agent panel`.

---

## Task 4: Rebuild the DFL loop to v5

**Files:**

- Modify: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.tsx`
- Test: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.test.tsx`

Rebuild the canvas to the v5 geometry: viewBox `0 0 900 510`, four corner cards (`.d1..d4`, 27% x 31%), central Microsoft IQ core (25%), signal/action/return rails with `animateMotion` traveling dots + SIGNAL/ACTION labels, All loops / Selected domain focus (dim non-selected streams), play/pause via a `useRef<SVGSVGElement>` + `pauseAnimations()`/`unpauseAnimations()`, `prefers-reduced-motion` hides dots, a journey strip (Data points → Microsoft IQ → Action packet → Human approval → Measured outcome) and the animation note. Preserve the test contract: domain buttons (`aria-label` = Curavias label, `aria-pressed`, `onDomainSelect`), All loops/Selected domain toggle, `data-testid="feedback-loop-canvas"` + `data-stream-mode`, pause↔play button.

- [ ] **Step 1:** Keep `DigitalFeedbackLoop.test.tsx` assertions (select emits once → `frontier-workforce`; mode toggle sets `data-stream-mode='selected'`; pause → play visible). Add a check that a `.d1..d4` domain card and the core render.
- [ ] **Step 2:** Run: `npx vitest run tests/unit/backstage-view.test.tsx` to capture the current green baseline.
- [ ] **Step 3:** Rewrite `DigitalFeedbackLoop.tsx` to v5 (styles + geometry + SMIL flows + controls). Token-based colours for light/dark legibility; brand accents `#365B7D` / `#1FA9D6` / `#17B890` / `#E8A200`.
- [ ] **Step 4:** Run: `npx vitest run tests/unit/backstage-view.test.tsx` and the DFL test. Expected: PASS.
- [ ] **Step 5:** Visual parity check in the browser at `/backstage` against the final mockup; adjust spacing/typography.
- [ ] **Step 6:** Commit `feat(dfl): rebuild loop to v5 signal-simulation`.

---

## Task 5: Compose the DFL section

**Files:**

- Modify: `workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoopSection.tsx`
- Create: `workspaces/shared/narrative/SectionHeader.tsx`

`SectionHeader` props: `{ id: string; header: string; tagline: string; description: string; tools?: ReactNode }` — renders an anchor (`id`) + header + tagline + description, with optional right-aligned tools.

- [ ] **Step 1:** Implement `SectionHeader.tsx` (griffel; `<h2>` header, tagline caption, body description).
- [ ] **Step 2:** In `DigitalFeedbackLoopSection.tsx`, render `SectionHeader` (Digital feedback loop / "Watch trusted signals become governed action through Microsoft IQ" / description) then a two-column layout: `DigitalFeedbackLoop` (loop) + `PoAgentPanel` (right). Wire `onDomainSelect` to update the selected domain state (drives the panel) and pass `onOpenInCopilot` → `rail.openWithReco(buildInsight(...), buildReco(...))`.
- [ ] **Step 3:** Typecheck + run the DFL + backstage-view tests. Expected: PASS.
- [ ] **Step 4:** Commit `feat(dfl): compose section header + loop + PO Agent panel`.

---

## Task 6: Backstage vertical-narrative shell

**Files:**

- Create: `workspaces/shared/narrative/useScrollSpy.ts`, `workspaces/shared/narrative/NarrativeShell.tsx`
- Modify: `workspaces/backstage/BackstageView.tsx`, `workspaces/backstage/BackstageSubNav.tsx`
- Test: `tests/unit/narrative-shell.test.tsx`, `tests/unit/backstage-view.test.tsx`

`NarrativeShell` props: `{ introTitle; introDescription; sections: { key; labelKey; render: () => ReactNode }[] }`. Renders the intro header, a sticky `TabList` (selected = active scrollspy anchor; click → `scrollIntoView`), and the stacked sections each with `id={key}`. `useScrollSpy(ids)` uses `IntersectionObserver` (guarded for jsdom) to return the active id.

- [ ] **Step 1: Write the failing test** `tests/unit/narrative-shell.test.tsx`: renders intro title, a tab per section, and each section anchor (`data-testid`), with the first section's tab selected by default.
- [ ] **Step 2:** Run: `npx vitest run tests/unit/narrative-shell.test.tsx`. Expected: FAIL.
- [ ] **Step 3:** Implement `useScrollSpy.ts` + `NarrativeShell.tsx`.
- [ ] **Step 4:** Rework `BackstageView.tsx` to render `NarrativeShell` with sections = [feedback-loop (DigitalFeedbackLoopSection), opportunities (OpportunityPipelineView)]; keep intro header (`backstage.header.*`). On mount, scroll to the `:widget`/hash anchor for deep-link back-compat.
- [ ] **Step 5:** Update `tests/unit/backstage-view.test.tsx` to assert the intro header, the section `TabList`, and both section anchors; `/backstage/opportunities` still resolves (scrolls to that section).
- [ ] **Step 6:** Run the narrative + backstage tests. Expected: PASS.
- [ ] **Step 7:** Commit `feat(backstage): vertical-narrative shell + sticky section nav`.

---

## Task 7: i18n keys

**Files:**

- Modify: `i18n/en.json`

- [ ] **Step 1:** Add keys under `backstage.story.feedbackLoop` for the v5 copy (tagline, section description, per-domain signal/action/return, core sub, HITL, journey steps, note) and under `backstage.sections.*` for each section header/tagline/description. Reuse existing keys where present.
- [ ] **Step 2:** Run: `python scripts/lint/check_mojibake.py apps/hcc-app-fluent/src/i18n/en.json`. Expected: clean.
- [ ] **Step 3:** Commit `feat(i18n): DFL v5 + Backstage section copy`.

---

## Task 8: Verify + self-review

- [ ] **Step 1:** `npx tsc --noEmit` — no errors.
- [ ] **Step 2:** `npx vitest run tests/unit/backstage-view.test.tsx tests/unit/narrative-shell.test.tsx tests/unit/po-agent-panel.test.tsx` + the DFL co-located test — all PASS.
- [ ] **Step 3:** Browser parity pass at `/backstage` (light + dark) vs the final mockup; capture a screenshot.
- [ ] **Step 4:** Confirm `prefers-reduced-motion` stops the flow dots and play/pause works.
- [ ] **Step 5:** Commit any polish; summarise residual items (Solution Design / Frontier sections stubbed; Start restructure = fast-follow).

---

## Notes

- Backstage sections beyond DFL + Opportunities (Solution Design — Sprint 36, Frontier — Sprint 37) are stubbed placeholders in the section registry until that content is integrated.
- Start adopting the same `NarrativeShell` + `SectionHeader` is the fast-follow (separate plan).
- Full unit suite has two pre-existing unrelated failures (`router.test.tsx` undici `AbortSignal`); out of scope here.
