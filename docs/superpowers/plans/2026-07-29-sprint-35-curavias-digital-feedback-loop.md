# Sprint 35 Curavias Digital Feedback Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a reusable, accessible Digital Feedback Loop as a distinct
Backstage Story section that routes selected-domain context to the existing
Product Owner Agent rail.

**Architecture:** A typed, framework-independent catalog defines the four
domains and five IQ layers. `DigitalFeedbackLoop` owns presentation and local
interaction only; `DigitalFeedbackLoopSection` is the Backstage adapter that
maps domain selection into the existing Copilot rail. The same visual renders
without the shell at `/present/feedback-loop`.

**Tech Stack:** React 18, TypeScript 5.7, Fluent UI v9, React Router 6, i18next,
Vitest, Testing Library, Playwright, and axe-core.

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for delegation |
| **Previous Version** | n/a (initial implementation plan) |
| **Sprint** | Sprint 35 - Curavias Digital Feedback Loop |
| **Issue** | [#536](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/536) |

**Design:**
[Sprint 35 design](../specs/2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md)

**Tracker:**
[#536](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/536)

---

## Delivery order and ownership

| Slice | Owner | Files owned | Dependency |
| ----- | ----- | ----------- | ---------- |
| WS-A | Visual subagent | `feedback-loop-model.ts`, `DigitalFeedbackLoop.tsx`, `DigitalFeedbackLoop.test.tsx` | none |
| WS-B | Integration subagent | `DigitalFeedbackLoopSection.tsx`, `StoryTab.tsx`, `en.json`, `de.json`, integration E2E assertions | WS-A contract |
| WS-C | Verification subagent | `FeedbackLoopPresentationView.tsx`, `router.tsx`, Playwright visual/a11y coverage | WS-A contract |

WS-A lands first. WS-B and WS-C rebase on that commit and may then run in
parallel. Subagents do not edit files outside their ownership without returning
to the orchestrator. Every slice is reviewed for spec compliance and code
quality before the next dependency is released.

## File structure

Create under
`apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/`:

* `feedback-loop-model.ts` - domain IDs, IQ layers, catalog, and props.
* `feedback-loop-model.test.ts` - catalog invariants and non-PHI checks.
* `DigitalFeedbackLoop.tsx` - visual, controls, local state, and callbacks.
* `DigitalFeedbackLoop.test.tsx` - component interaction and reduced-motion
  tests.
* `DigitalFeedbackLoopSection.tsx` - Backstage-to-Copilot rail adapter.
* `FeedbackLoopPresentationView.tsx` - unframed presentation composition.

Modify:

* `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/StoryTab.tsx` - mount
  the new section after delivery strips.
* `apps/hcc-app-fluent/src/shell/router.tsx` - add the standalone top-level
  route outside `AppShell`.
* `apps/hcc-app-fluent/src/i18n/en.json` and `de.json` - customer-facing copy.
* `apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts` - Backstage,
  presentation, responsive, and rail behavior.
* `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts` - scan both feedback-loop
  surfaces without excluding the new section.

## Task 1: Freeze the visual model contract (WS-A)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model.test.ts`
* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model.ts`

* [ ] **Step 1: Write the failing catalog test**

```ts
import { describe, expect, it } from 'vitest';
import { FEEDBACK_LOOP_DOMAINS, IQ_LAYERS } from './feedback-loop-model';

describe('feedback-loop catalog', () => {
  it('defines four unique domains and all five Microsoft IQ layers', () => {
    expect(FEEDBACK_LOOP_DOMAINS).toHaveLength(4);
    expect(new Set(FEEDBACK_LOOP_DOMAINS.map(({ id }) => id)).size).toBe(4);
    expect(IQ_LAYERS).toEqual([
      'work',
      'foundry',
      'fabric',
      'process',
      'governance',
    ]);
  });

  it('provides a complete, non-PHI context for every domain', () => {
    for (const domain of FEEDBACK_LOOP_DOMAINS) {
      expect(domain.signalIds.length).toBeGreaterThan(0);
      expect(domain.proposedActionId).toBeTruthy();
      expect(domain.outcomeId).toBeTruthy();
      expect(domain.iqLayers.length).toBeGreaterThan(0);
      expect(JSON.stringify(domain)).not.toMatch(/patient|person|birth|mrn/i);
    }
  });
});
```

* [ ] **Step 2: Run the test and verify the contract is absent**

Run from `apps/hcc-app-fluent`:

```powershell
npx vitest run src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model.test.ts
```

Expected: FAIL because `./feedback-loop-model` does not exist.

* [ ] **Step 3: Implement the typed catalog**

Define these exported types and constants:

```ts
export const IQ_LAYERS = [
  'work',
  'foundry',
  'fabric',
  'process',
  'governance',
] as const;

export type IqLayer = (typeof IQ_LAYERS)[number];
export type FeedbackLoopMode = 'all' | 'selected';
export type FeedbackLoopDomainId =
  | 'care-ecosystem'
  | 'command-center'
  | 'frontier-workforce'
  | 'care-innovation';

export interface FeedbackLoopDomain {
  id: FeedbackLoopDomainId;
  curaviasLabelKey: string;
  microsoftLabelKey: string;
  groupLabelKey: string;
  signalIds: readonly string[];
  proposedActionId: string;
  outcomeId: string;
  iqLayers: readonly IqLayer[];
  citations: readonly string[];
}

export interface DigitalFeedbackLoopProps {
  domains: readonly FeedbackLoopDomain[];
  onDomainSelect?: (domain: FeedbackLoopDomain) => void;
  presentationMode?: boolean;
}
```

Populate `FEEDBACK_LOOP_DOMAINS` with the exact four rows from design section 4.
Use these citations for the deterministic demonstration cards:

* `docs/PRD.md#fr-poa-001`
* `docs/PRD.md#fr-poa-002`
* `docs/ARCHITECTURE.md`
* `docs/adr/0043-product-owner-agent-foundry-iq-domain.md`

* [ ] **Step 4: Run the focused test**

Run the Step 2 command.

Expected: PASS, 2 tests.

* [ ] **Step 5: Commit WS-A contract**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model.ts apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/feedback-loop-model.test.ts
git commit -m "feat(backstage): define feedback-loop domain contract"
```

## Task 2: Build the Living Infinity component (WS-A)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.test.tsx`
* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.tsx`

* [ ] **Step 1: Write failing interaction tests**

```tsx
import { fireEvent, render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it, vi } from 'vitest';
import { DigitalFeedbackLoop } from './DigitalFeedbackLoop';
import { FEEDBACK_LOOP_DOMAINS } from './feedback-loop-model';

const renderLoop = (onDomainSelect = vi.fn()) => {
  render(
    <FluentProvider theme={webLightTheme}>
      <DigitalFeedbackLoop
        domains={FEEDBACK_LOOP_DOMAINS}
        onDomainSelect={onDomainSelect}
      />
    </FluentProvider>,
  );
  return onDomainSelect;
};

describe('DigitalFeedbackLoop', () => {
  it('selects a domain and emits it once', () => {
    const onSelect = renderLoop();
    const button = screen.getByRole('button', { name: /empower care teams/i });
    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-pressed', 'true');
    expect(onSelect).toHaveBeenCalledOnce();
    expect(onSelect.mock.calls[0][0].id).toBe('frontier-workforce');
  });

  it('toggles selected-loop mode and pause state accessibly', () => {
    renderLoop();
    fireEvent.click(screen.getByRole('button', { name: /selected domain/i }));
    expect(screen.getByTestId('feedback-loop-canvas')).toHaveAttribute(
      'data-stream-mode',
      'selected',
    );
    fireEvent.click(screen.getByRole('button', { name: /pause simulation/i }));
    expect(screen.getByRole('button', { name: /play simulation/i })).toBeVisible();
  });
});
```

* [ ] **Step 2: Run the component test and observe failure**

```powershell
npx vitest run src/workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.test.tsx
```

Expected: FAIL because `DigitalFeedbackLoop.tsx` does not exist.

* [ ] **Step 3: Implement the component**

Use Fluent `Button`, `Badge`, `Body1`, `Caption1`, `Title3`, `Tooltip`, and
`makeStyles`. Use `PauseRegular` and `PlayRegular` icons. Implement:

* initial selected ID `command-center`, mode `all`, playing `true`;
* four real buttons with `aria-pressed` and stable `data-domain-id`;
* two mode buttons labelled "All loops" and "Selected domain";
* play/pause icon button with a state-dependent accessible name;
* an SVG with one static inbound, outbound, and return path per domain;
* marker classes controlled by `data-playing` and `data-stream-mode`;
* a CSS `@media (prefers-reduced-motion: reduce)` rule that disables marker
  animation;
* a narrow layout breakpoint that renders IQ first and domain buttons as a
  single-column list;
* a labelled empty state when `domains.length === 0`;
* no Copilot or agent imports.

The SVG uses `aria-hidden="true"`; the domain buttons and flow legend expose all
meaningful text. Preserve stable dimensions with `minHeight`, `aspectRatio`,
and explicit grid tracks so selection does not shift the layout.

* [ ] **Step 4: Run WS-A tests and typecheck**

```powershell
npx vitest run src/workspaces/backstage/tabs/story/feedback-loop
npm run lint
```

Expected: all focused tests PASS and TypeScript exits 0.

* [ ] **Step 5: Commit the visual component**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop
git commit -m "feat(backstage): add animated Digital Feedback Loop"
```

## Task 3: Integrate Backstage and Product Owner context (WS-B)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoopSection.tsx`
* Modify: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/StoryTab.tsx`
* Modify: `apps/hcc-app-fluent/src/i18n/en.json`
* Modify: `apps/hcc-app-fluent/src/i18n/de.json`
* Create: `apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts`

* [ ] **Step 1: Write the failing Backstage E2E test**

```ts
import { expect, test } from '@playwright/test';

test('Backstage feedback loop routes domain context to the PO rail', async ({ page }) => {
  await page.goto('/backstage/story');
  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
  await expect(page.locator('[data-testid^="backstage-nav-"]')).toHaveCount(3);

  await page.getByRole('button', { name: /empower care teams/i }).click();
  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail).toContainText('product-owner-agent');
  await expect(rail).toContainText(/skills|staffing|workload/i);
  await expect(rail).toContainText(/source|citation|grounded/i);
});
```

* [ ] **Step 2: Run the focused test and verify failure**

```powershell
npx playwright test tests/e2e/feedback-loop.spec.ts
```

Expected: FAIL because `digital-feedback-loop-section` is absent.

* [ ] **Step 3: Implement the Backstage adapter**

`DigitalFeedbackLoopSection` imports `FEEDBACK_LOOP_DOMAINS`,
`DigitalFeedbackLoop`, `useCopilotRail`, `ContextInsight`, and `GroundedReco`.
For each selected domain, build:

```ts
const insight: ContextInsight = {
  id: `feedback-loop-${domain.id}`,
  label: t(domain.curaviasLabelKey),
  context: {
    domainId: domain.id,
    signalIds: domain.signalIds,
    proposedActionId: domain.proposedActionId,
    outcomeId: domain.outcomeId,
    iqLayers: domain.iqLayers,
    source: 'backstage-digital-feedback-loop',
  },
};
```

Map the same domain to a `GroundedReco` with:

* `agentLabel: 'product-owner-agent'`;
* a `signal` context chip;
* one concise advisory `read` describing signal -> governed action -> outcome;
* one lever labelled as a recommendation, never an applied action;
* `citations: [...domain.citations]`;
* snapshot provenance and follow-ups for evidence, IQ layers, and business
  value.

Call `rail.openWithReco(insight, reco)` from `onDomainSelect`. If no mapping is
available, emit `console.warn` in development and preserve the current rail.

* [ ] **Step 4: Mount the new Story section**

Import and render `<DigitalFeedbackLoopSection />` in `StoryTab.tsx` immediately
after the delivery-strips section and before the Copilot roster. Do not modify
`NAV_ITEMS` or `WIDGETS` in `BackstageView.tsx`.

Add English and German keys under `backstage.story.feedbackLoop` for the title,
purpose, controls, four domains, five IQ layers, signal/action/outcome labels,
legend, advisory note, and empty state. English remains the runtime fallback.

* [ ] **Step 5: Re-run focused checks**

```powershell
npx playwright test tests/e2e/feedback-loop.spec.ts
npm run lint
```

Expected: the Backstage test PASSes, exactly three nav items remain, and
TypeScript exits 0.

* [ ] **Step 6: Commit WS-B**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story apps/hcc-app-fluent/src/i18n/en.json apps/hcc-app-fluent/src/i18n/de.json apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts
git commit -m "feat(backstage): route feedback-loop context to PO Agent"
```

## Task 4: Add standalone presentation reuse (WS-C)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/FeedbackLoopPresentationView.tsx`
* Modify: `apps/hcc-app-fluent/src/shell/router.tsx`
* Modify: `apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts`

* [ ] **Step 1: Add the failing presentation-route test**

Append:

```ts
test('standalone route reuses the loop without app-shell chrome', async ({ page }) => {
  await page.goto('/present/feedback-loop');
  await expect(page.getByTestId('feedback-loop-presentation')).toBeVisible();
  await expect(page.getByTestId('feedback-loop-canvas')).toBeVisible();
  await expect(page.getByRole('navigation', { name: /primary/i })).toHaveCount(0);
  await expect(page.getByRole('complementary', { name: /agent/i })).toHaveCount(0);
});
```

* [ ] **Step 2: Run the test and verify route failure**

Run the focused Playwright command from Task 3.

Expected: the new test FAILs because the wildcard redirects to `/start`.

* [ ] **Step 3: Implement the presentation view and route**

Render `DigitalFeedbackLoop` with `FEEDBACK_LOOP_DOMAINS` and
`presentationMode`. Include the Curavias wordmark, title, synthetic/no-PHI
badge, and flow legend; do not mount `AppShell`, `AgentPlane`, or duplicate
domain data.

Add a top-level route before the `AppShell` route:

```tsx
{
  path: 'present/feedback-loop',
  element: <FeedbackLoopPresentationView />,
},
```

* [ ] **Step 4: Verify presentation reuse**

```powershell
npx playwright test tests/e2e/feedback-loop.spec.ts
npm run build
```

Expected: all feedback-loop E2E tests PASS and the production build exits 0.

* [ ] **Step 5: Commit WS-C route**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/FeedbackLoopPresentationView.tsx apps/hcc-app-fluent/src/shell/router.tsx apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts
git commit -m "feat(backstage): add feedback-loop presentation route"
```

## Task 5: Responsive, motion, visual, and accessibility gates (WS-C)

**Files:**

* Modify: `apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts`
* Modify: `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts`

* [ ] **Step 1: Add responsive and reduced-motion checks**

Append tests that:

* set `1440 x 900`, open `/backstage/story`, and save
  `test-results/feedback-loop-desktop.png`;
* set `390 x 844`, assert each domain button and the IQ core are visible, assert
  `document.documentElement.scrollWidth === document.documentElement.clientWidth`,
  and save `test-results/feedback-loop-narrow.png`;
* call `page.emulateMedia({ reducedMotion: 'reduce' })` before navigation and
  assert the canvas has `data-reduced-motion="true"`;
* click pause and assert the canvas has `data-playing="false"`.

Use `expect(...).toHaveScreenshot(...)` only after the first reviewed baseline
is accepted; before that, attach screenshots as PR evidence without committing
unstable snapshots.

* [ ] **Step 2: Extend the axe surface list**

Add `/backstage/story` and `/present/feedback-loop` to `SURFACES`. Do not exclude
`digital-feedback-loop-section` or `feedback-loop-presentation` from axe.

* [ ] **Step 3: Run focused browser verification**

```powershell
npx playwright test tests/e2e/feedback-loop.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

Expected: all tests PASS; no serious or critical WCAG 2.1 AA violations; desktop
and narrow screenshots show no clipped labels, overlap, or horizontal scroll.

* [ ] **Step 4: Run complete app gates**

```powershell
npm test
npm run lint
npm run build
npm run test:e2e
```

Expected: all commands exit 0. Record exact command results and screenshot paths
in the PR body.

* [ ] **Step 5: Commit verification coverage**

```powershell
git add apps/hcc-app-fluent/tests/e2e/feedback-loop.spec.ts apps/hcc-app-fluent/tests/e2e/a11y.spec.ts
git commit -m "test(backstage): verify feedback-loop UX and accessibility"
```

## Task 6: Documentation and PR close-out

**Files:**

* Verify: `docs/superpowers/specs/2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md`
* Verify: `docs/superpowers/plans/2026-07-29-sprint-35-curavias-digital-feedback-loop.md`

* [ ] **Step 1: Run document gates**

```powershell
python scripts/lint/check_mojibake.py docs/superpowers/specs/2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md docs/superpowers/plans/2026-07-29-sprint-35-curavias-digital-feedback-loop.md
npx --yes markdownlint-cli2 "docs/superpowers/specs/2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md" "docs/superpowers/plans/2026-07-29-sprint-35-curavias-digital-feedback-loop.md"
```

Expected: no mojibake and 0 Markdown issues.

* [ ] **Step 2: Confirm scope and contract boundaries**

Run:

```powershell
git diff --name-only origin/main...HEAD
rg "useCopilotRail|useConversation" apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/feedback-loop/DigitalFeedbackLoop.tsx
```

Expected: changed implementation files are limited to the experience lane and
Sprint 35 docs; the `rg` command returns no matches.

* [ ] **Step 3: Open the human-reviewed PR**

The PR must link #536 and include:

* requirements advanced: `FR-POA-001`, `FR-POA-002`, `FR-CX-006`,
  `FR-UX-001`, `FR-UX-004`, `NFR-POA-001`, `NFR-POA-004`, and `NFR-UX-001`
  through `NFR-UX-004`;
* experience-lane impact only;
* no API, infra, MCP allow-list, PHI, deploy, or delete impact;
* unit, lint, build, Playwright, screenshot, and axe evidence;
* residual risk: SVG path/layout differences across browser text rendering.

Never self-merge. A human reviewer verifies the visual evidence and Product
Owner advisory/citation behavior first.

## Final acceptance checklist

* [ ] Four unique domains and five IQ layers are represented.
* [ ] The section is inside Backstage Story and no fourth tab exists.
* [ ] Signal, proposed action, human approval, and outcome are explicit.
* [ ] Domain selection updates the existing Product Owner Agent rail.
* [ ] `DigitalFeedbackLoop` has no agent/runtime dependency.
* [ ] All-loop, selected-loop, pause, and reduced-motion modes work.
* [ ] Desktop and narrow layouts have no overlap or horizontal scroll.
* [ ] Standalone presentation reuses the same visual and catalog.
* [ ] Unit, lint, build, Playwright, screenshot, and axe gates pass.
* [ ] Synthetic/no-PHI and advisory-only postures remain visible.
