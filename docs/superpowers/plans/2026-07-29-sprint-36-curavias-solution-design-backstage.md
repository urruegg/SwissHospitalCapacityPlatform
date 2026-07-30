# Sprint 36 Curavias Backstage - full showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the full **Curavias Backstage showcase** in Backstage > Story -
**keeping** the Digital feedback loop (Sprint 35) and the Solution design - IQ
operating model board, and **adding** the Frontier-Firm narrative sections (hero,
Success Framework, DevSecOps loop, review sessions, PO knowledge classes) - all
routing to the docked Product Owner Agent rail.

**Architecture:** A typed, framework-independent catalog defines five IQ layers
and two cross-cutting lanes (Governance, Security) with per-plane capabilities
and tiers. `SolutionDesignBoard` owns presentation and local selection only;
`SolutionDesignSection` is the Backstage adapter that maps a selected context
into the existing Copilot rail. The added narrative sections read a typed
`backstage-narrative-content.ts` model and reuse the same rail-routing pattern.
The board also renders without the shell at `/present/solution-design`.

**Tech Stack:** React 18, TypeScript 5.7, Fluent UI v9, React Router 6, i18next,
Vitest, Testing Library, Playwright, and axe-core.

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for delegation |
| **Previous Version** | 1.0.0 (Solution-design section only; extended to the full Backstage showcase) |
| **Sprint** | Sprint 36 - Curavias Backstage full showcase |
| **Issue** | [#540](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/540) |

**Design:**
[Sprint 36 design](../specs/2026-07-29-sprint-36-curavias-solution-design-backstage-design.md)

**Tracker:**
[#540](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/540)

---

## Delivery order and ownership

| Slice | Owner | Files owned | Dependency |
| ----- | ----- | ----------- | ---------- |
| WS-A | Visual subagent | `solution-design-model.ts`, `SolutionDesignBoard.tsx`, tests | none |
| WS-B | Integration subagent | `SolutionDesignSection.tsx`, `StoryTab.tsx`, `en.json`, `de.json`, integration E2E | WS-A contract |
| WS-C | Verification subagent | `SolutionDesignPresentationView.tsx`, `router.tsx`, Playwright visual/a11y | WS-A contract |
| WS-D | Governance subagent | `docs/SD.md`, `docs/GLOSSARY.md` | none (parallel) |
| WS-E | Narrative subagent | `backstage-narrative-content.ts` + B1/B2/B3/B5/B6 section components + six-lanes companion + i18n + narrative E2E | WS-B (StoryTab mount) |

WS-A lands first. WS-B and WS-C rebase on that commit and may run in parallel.
WS-D is independent. WS-E depends on WS-B (the StoryTab mount point) and reuses
the SD context-routing pattern. Subagents do not edit files outside their
ownership without returning to the orchestrator. Each slice is reviewed for spec
compliance and code quality before the next dependency is released.

## File structure

Create under
`apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/`:

* `solution-design-model.ts` - plane IDs, tiers, catalog, context + props types.
* `solution-design-model.test.ts` - catalog invariants and non-PHI checks.
* `SolutionDesignBoard.tsx` - visual, header/badge buttons, local state, callback.
* `SolutionDesignBoard.test.tsx` - selection + context-emit tests.
* `SolutionDesignSection.tsx` - Backstage-to-Copilot rail adapter.
* `SolutionDesignPresentationView.tsx` - unframed presentation composition.

Modify:

* `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/StoryTab.tsx` - mount
  the section after the feedback-loop section.
* `apps/hcc-app-fluent/src/shell/router.tsx` - add the standalone top-level route.
* `apps/hcc-app-fluent/src/i18n/en.json` and `de.json` - customer-facing copy.
* `apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts` - Backstage,
  presentation, responsive, and rail behavior.
* `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts` - scan the new surface.
* `docs/SD.md` and `docs/GLOSSARY.md` - WS-D model reconciliation.

## Task 1: Freeze the IQ-model catalog contract (WS-A)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/solution-design-model.test.ts`
* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/solution-design-model.ts`

* [ ] **Step 1: Write the failing catalog test**

```ts
import { describe, expect, it } from 'vitest';
import { IQ_PLANES, LAYER_IDS, LANE_IDS } from './solution-design-model';

describe('solution-design catalog', () => {
  it('defines five IQ layers and two cross-cutting lanes with unique ids', () => {
    expect(LAYER_IDS).toEqual(['work', 'process', 'foundry', 'fabric', 'devsecops']);
    expect(LANE_IDS).toEqual(['gov', 'sec']);
    const ids = IQ_PLANES.map((p) => p.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(ids).toHaveLength(7);
  });

  it('every plane has >= 1 MVP capability, valid tiers, and no PHI-shaped text', () => {
    for (const plane of IQ_PLANES) {
      const mvp = plane.capabilities.filter((c) => c.tier === 'mvp');
      expect(mvp.length).toBeGreaterThan(0);
      for (const c of plane.capabilities) {
        expect(['mvp', 'target']).toContain(c.tier);
      }
      expect(JSON.stringify(plane)).not.toMatch(/patient name|birth|mrn|ssn/i);
    }
  });
});
```

* [ ] **Step 2: Run the test and verify the contract is absent**

Run from `apps/hcc-app-fluent`:

```powershell
npx vitest run src/workspaces/backstage/tabs/story/solution-design/solution-design-model.test.ts
```

Expected: FAIL because `./solution-design-model` does not exist.

* [ ] **Step 3: Implement the typed catalog**

Define and export:

```ts
export const LAYER_IDS = ['work', 'process', 'foundry', 'fabric', 'devsecops'] as const;
export const LANE_IDS = ['gov', 'sec'] as const;

export type IqLayerId = (typeof LAYER_IDS)[number];
export type IqLaneId = (typeof LANE_IDS)[number];
export type IqPlaneId = IqLayerId | IqLaneId;
export type CapabilityTier = 'mvp' | 'target';

export interface Capability {
  id: string;
  labelKey: string;
  tier: CapabilityTier;
}

export interface IqPlane {
  id: IqPlaneId;
  kind: 'layer' | 'lane';
  nameKey: string;
  taglineKey: string;
  iconName: string;      // @fluentui/react-icons component name
  accent: string;        // brandkit hex
  accentText: string;    // AA-safe text hex on white
  capabilities: readonly Capability[];
}

export interface SolutionDesignContext {
  scope: IqPlaneId | 'model';
  kind: 'plane' | 'capability';
  capabilityId?: string;
  tier?: CapabilityTier;
  source: 'backstage-solution-design';
}

export interface SolutionDesignBoardProps {
  planes: readonly IqPlane[];
  onContextSelect?: (ctx: SolutionDesignContext) => void;
  presentationMode?: boolean;
}
```

Populate `IQ_PLANES` with the seven planes from design section 4, using the
color + icon map from design section 3:

* `work` green `#17B890`/`#12765F` icon `Board`; `process` teal `#1FA9D6`/`#176C8A`
  icon `Flow`; `foundry` blue `#365B7D`/`#365B7D` icon `Bot`; `fabric` teal
  `#1FA9D6`/`#176C8A` icon `Database`; `devsecops` slate `#6B7A88`/`#4A5A68` icon
  `BranchFork`; `gov` violet `#5A6CF0`/`#4A46C7` icon `ClipboardTaskList`; `sec`
  red `#E30613`/`#C70713` icon `ShieldKeyhole`.
* Capabilities exactly as in design section 4 (MVP + Target rows).

* [ ] **Step 4: Run the focused test**

Run the Step 2 command. Expected: PASS, 2 tests.

* [ ] **Step 5: Commit WS-A contract**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/solution-design-model.ts apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/solution-design-model.test.ts
git commit -m "feat(backstage): define solution-design IQ-model contract"
```

## Task 2: Build the SolutionDesignBoard component (WS-A)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignBoard.test.tsx`
* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignBoard.tsx`

* [ ] **Step 1: Write failing interaction tests**

```tsx
import { fireEvent, render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it, vi } from 'vitest';
import { SolutionDesignBoard } from './SolutionDesignBoard';
import { IQ_PLANES } from './solution-design-model';

const renderBoard = (onContextSelect = vi.fn()) => {
  render(
    <FluentProvider theme={webLightTheme}>
      <SolutionDesignBoard planes={IQ_PLANES} onContextSelect={onContextSelect} />
    </FluentProvider>,
  );
  return onContextSelect;
};

describe('SolutionDesignBoard', () => {
  it('emits a plane context when a plane header is activated', () => {
    const onSelect = renderBoard();
    fireEvent.click(screen.getByRole('button', { name: /foundry iq/i }));
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ scope: 'foundry', kind: 'plane', source: 'backstage-solution-design' }),
    );
  });

  it('emits a capability context with tier when a badge is activated', () => {
    const onSelect = renderBoard();
    fireEvent.click(screen.getByRole('button', { name: /copilot orchestrator/i }));
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ scope: 'foundry', kind: 'capability', tier: 'mvp' }),
    );
    expect(screen.getByRole('button', { name: /copilot orchestrator/i })).toHaveAttribute('aria-pressed', 'true');
  });
});
```

* [ ] **Step 2: Run the component test and observe failure**

```powershell
npx vitest run src/workspaces/backstage/tabs/story/solution-design/SolutionDesignBoard.test.tsx
```

Expected: FAIL because `SolutionDesignBoard.tsx` does not exist.

* [ ] **Step 3: Implement the board**

Use Fluent `makeStyles` + the mapped `@fluentui/react-icons` components. Implement:

* a three-column layout: Governance lane (left), five layer cards (center),
  Security lane (right), plus the golden-thread caption;
* each plane as a card with a colored left accent, a tinted icon tile, a header
  `<button>` (icon + name + tagline) and capability `<button>` badges;
* MVP badges filled/tinted in the plane accent with a `CheckmarkCircle` icon;
  Target badges dashed in the plane accent with a `Target` icon;
* a section header button (Curavias mark + title + description) that emits
  `{ scope: 'model', kind: 'plane' }`;
* `aria-pressed` on the active header/badge; the containing card raises;
* `onContextSelect` invoked once per activation with the typed context;
* initial selection: the `work` plane header;
* a narrow-width breakpoint that stacks lanes above/below the layer column;
* a labelled empty state when `planes.length === 0`;
* no Copilot or agent imports.

* [ ] **Step 4: Run WS-A tests and typecheck**

```powershell
npx vitest run src/workspaces/backstage/tabs/story/solution-design
npm run lint
```

Expected: all focused tests PASS and TypeScript exits 0.

* [ ] **Step 5: Commit the board**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design
git commit -m "feat(backstage): add Solution Design IQ operating-model board"
```

## Task 3: Integrate Backstage and Product Owner context (WS-B)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignSection.tsx`
* Modify: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/StoryTab.tsx`
* Modify: `apps/hcc-app-fluent/src/i18n/en.json`
* Modify: `apps/hcc-app-fluent/src/i18n/de.json`
* Create: `apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts`

* [ ] **Step 1: Write the failing Backstage E2E test**

```ts
import { expect, test } from '@playwright/test';

test('Backstage solution-design routes plane + badge context to the PO rail', async ({ page }) => {
  await page.goto('/backstage/story');
  await expect(page.getByTestId('solution-design-section')).toBeVisible();
  await expect(page.locator('[data-testid^="backstage-nav-"]')).toHaveCount(3);

  await page.getByRole('button', { name: /foundry iq/i }).first().click();
  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail).toContainText('product-owner-agent');

  await page.getByRole('button', { name: /copilot orchestrator/i }).click();
  await expect(rail).toContainText(/Copilot orchestrator/i);
  await expect(rail).toContainText(/MVP|Target/i);
  await expect(rail).toContainText(/source|citation|grounded/i);
});
```

* [ ] **Step 2: Run the focused test and verify failure**

```powershell
npx playwright test tests/e2e/solution-design.spec.ts
```

Expected: FAIL because `solution-design-section` is absent.

* [ ] **Step 3: Implement the Backstage adapter**

`SolutionDesignSection` imports `IQ_PLANES`, `SolutionDesignBoard`,
`useCopilotRail`, `ContextInsight`, and `GroundedReco`. On each context:

```ts
const insight: ContextInsight = {
  id: `solution-design-${ctx.scope}${ctx.capabilityId ? '-' + ctx.capabilityId : ''}`,
  label: labelForContext(ctx),
  context: { ...ctx },
};
```

Build a `GroundedReco` with `agentLabel: 'product-owner-agent'`, a `signal`
context chip, one concise advisory `read` (plane-level or capability-level with
its MVP/Target tier), `citations: ['docs/SD.md', 'docs/GLOSSARY.md', 'Curavias PRD']`,
snapshot provenance, and follow-ups (evidence, requirement, roadmap). Call
`rail.openWithReco(insight, reco)` from `onContextSelect`. If no mapping is
available, `console.warn` in development and preserve the current rail.

* [ ] **Step 4: Mount the section + copy**

Render `<SolutionDesignSection />` in `StoryTab.tsx` immediately after the
feedback-loop section and before the Copilot roster. Do not modify `NAV_ITEMS`
or `WIDGETS` in `BackstageView.tsx`.

Add English + German keys under `backstage.story.solutionDesign` for the title,
description, the seven plane names + taglines, all capability labels, the
MVP/Target labels, the golden-thread caption, and the empty state. English is the
runtime fallback.

* [ ] **Step 5: Re-run focused checks**

```powershell
npx playwright test tests/e2e/solution-design.spec.ts
npm run lint
```

Expected: the Backstage test PASSes, exactly three nav items remain, TypeScript
exits 0.

* [ ] **Step 6: Commit WS-B**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story apps/hcc-app-fluent/src/i18n/en.json apps/hcc-app-fluent/src/i18n/de.json apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts
git commit -m "feat(backstage): route solution-design context to PO Agent"
```

## Task 4: Add standalone presentation reuse (WS-C)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignPresentationView.tsx`
* Modify: `apps/hcc-app-fluent/src/shell/router.tsx`
* Modify: `apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts`

* [ ] **Step 1: Add the failing presentation-route test**

```ts
test('standalone route reuses the board without app-shell chrome', async ({ page }) => {
  await page.goto('/present/solution-design');
  await expect(page.getByTestId('solution-design-presentation')).toBeVisible();
  await expect(page.getByTestId('solution-design-board')).toBeVisible();
  await expect(page.getByRole('complementary', { name: /agent/i })).toHaveCount(0);
});
```

* [ ] **Step 2: Run the test and verify route failure**

Run the focused Playwright command from Task 3. Expected: the new test FAILs
because the wildcard redirects to `/start`.

* [ ] **Step 3: Implement the presentation view and route**

Render `SolutionDesignBoard` with `IQ_PLANES` and `presentationMode`. Include the
Curavias wordmark, title, and legend; do not mount `AppShell`, `AgentPlane`, or
duplicate the catalog. Add a top-level route before the `AppShell` route:

```tsx
{
  path: 'present/solution-design',
  element: <SolutionDesignPresentationView />,
},
```

* [ ] **Step 4: Verify presentation reuse**

```powershell
npx playwright test tests/e2e/solution-design.spec.ts
npm run build
```

Expected: all solution-design E2E tests PASS and the production build exits 0.

* [ ] **Step 5: Commit WS-C route**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignPresentationView.tsx apps/hcc-app-fluent/src/shell/router.tsx apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts
git commit -m "feat(backstage): add solution-design presentation route"
```

## Task 5: Responsive, visual, and accessibility gates (WS-C)

**Files:**

* Modify: `apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts`
* Modify: `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts`

* [ ] **Step 1: Add responsive checks**

Append tests that:

* set `1440 x 900`, open `/backstage/story`, and save
  `test-results/solution-design-desktop.png`;
* set `390 x 844`, assert each plane header and both lane headers are visible,
  assert `document.documentElement.scrollWidth === document.documentElement.clientWidth`,
  and save `test-results/solution-design-narrow.png`.

Use `toHaveScreenshot(...)` only after a first reviewed baseline is accepted;
before that, attach screenshots as PR evidence without committing snapshots.

* [ ] **Step 2: Extend the axe surface list**

Add `/present/solution-design` to `SURFACES` and do not exclude
`solution-design-section` or `solution-design-presentation` from axe. `/backstage/story`
is already scanned; ensure the new section is not excluded.

* [ ] **Step 3: Run focused browser verification**

```powershell
npx playwright test tests/e2e/solution-design.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

Expected: all tests PASS; no serious or critical WCAG 2.1 AA violation; desktop
and narrow screenshots show no clipped labels, overlap, or horizontal scroll.

* [ ] **Step 4: Run complete app gates**

```powershell
npm test
npm run lint
npm run build
npm run test:e2e
```

Expected: all commands exit 0. Record exact results + screenshot paths in the PR.

* [ ] **Step 5: Commit verification coverage**

```powershell
git add apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts apps/hcc-app-fluent/tests/e2e/a11y.spec.ts
git commit -m "test(backstage): verify solution-design UX and accessibility"
```

## Task 6: Governance reconciliation (WS-D)

**Files:**

* Modify: `docs/SD.md`
* Modify: `docs/GLOSSARY.md`

* [ ] **Step 1: Reconcile the SD model**

In `docs/SD.md` §2 (IQ-Layered Solution Design), update the model so **Process IQ
is a stacked layer** (Work -> Process -> Foundry -> Fabric -> DevSecOps) and
**Governance and Security are cross-cutting lanes** spanning every layer (replace
the single "Governance IQ" stacked layer + "Process IQ spine" framing). Keep every
existing heading anchor; add the lane framing additively. Update the capability
split table + per-layer subsections to match. This is a MINOR bump.

* [ ] **Step 2: Reconcile the glossary**

In `docs/GLOSSARY.md` §1.2, update the **Process IQ** entry (now a layer, not a
spine) and split **Governance IQ** into a **Governance lane** + a new **Security
lane** cross-cutting definition. MINOR bump.

* [ ] **Step 3: Bump versions + run doc gates**

Bump the `Version`/`Previous Version`/`Date` headers on both docs per
copilot-instructions section 9. Then:

```powershell
python scripts/lint/check_mojibake.py docs/SD.md docs/GLOSSARY.md
npx --yes markdownlint-cli2 "docs/SD.md" "docs/GLOSSARY.md"
```

Expected: no mojibake and 0 Markdown issues.

* [ ] **Step 4: Commit WS-D**

```powershell
git add docs/SD.md docs/GLOSSARY.md
git commit -m "docs(sd): reconcile IQ model - Process IQ layer + Governance/Security lanes"
```

## Task 7: Backstage narrative content + hero / Success Framework / PO classes (WS-E)

**Files:**

* Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/backstage-narrative-content.ts` (+ `.test.ts`)
* Create: `.../narrative/BackstageHero.tsx`, `.../narrative/SuccessFrameworkSection.tsx`, `.../narrative/PoKnowledgeClassesSection.tsx`
* Modify: `.../story/StoryTab.tsx`, `apps/hcc-app-fluent/src/i18n/en.json`, `de.json`

* [ ] **Step 1: Write the failing content test**

```ts
import { describe, expect, it } from 'vitest';
import { BACKSTAGE_NARRATIVE } from './backstage-narrative-content';

describe('backstage narrative content', () => {
  it('defines the narrative sections with i18n keys and no PHI', () => {
    expect(BACKSTAGE_NARRATIVE.map((s) => s.id)).toEqual(
      expect.arrayContaining(['hero', 'success-framework', 'devsecops-loop', 'review-sessions', 'po-classes']),
    );
    expect(JSON.stringify(BACKSTAGE_NARRATIVE)).not.toMatch(/patient name|birth|mrn/i);
  });
});
```

* [ ] **Step 2: Run + verify failure**

Run: `npx vitest run src/workspaces/backstage/tabs/story/narrative/backstage-narrative-content.test.ts` - FAIL (module missing).

* [ ] **Step 3: Implement the content model + three sections**

`backstage-narrative-content.ts` holds typed section descriptors + i18n keys (hero;
success-framework principles + numbers; po-classes A/B/C/D). Implement
`BackstageHero`, `SuccessFrameworkSection` (numbers labelled `as-built`), and
`PoKnowledgeClassesSection` (CTA opens the rail via `useCopilotRail`). Each root
carries `data-testid="backstage-<id>"`. Add en/de i18n under
`backstage.story.narrative.*` (English fallback).

* [ ] **Step 4: Mount in StoryTab (composition order)**

In `StoryTab.tsx` render, in order: `BackstageHero`, `SuccessFrameworkSection`,
(existing `DigitalFeedbackLoopSection`), (existing `SolutionDesignSection`), then
the Task 8 sections. Keep `NAV_ITEMS` / `WIDGETS` unchanged.

* [ ] **Step 5: Run + commit**

Run: `npx vitest run src/workspaces/backstage/tabs/story/narrative; npm run lint` - PASS.

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/StoryTab.tsx apps/hcc-app-fluent/src/i18n/en.json apps/hcc-app-fluent/src/i18n/de.json
git commit -m "feat(backstage): narrative content + hero, Success Framework, PO classes"
```

## Task 8: DevSecOps loop, review sessions, six-lanes companion (WS-E)

**Files:**

* Create: `.../narrative/DevSecOpsLoopSection.tsx`, `.../narrative/ReviewSessionsSection.tsx`
* Modify: `.../solution-design/SolutionDesignSection.tsx` (six-lanes companion), `.../story/StoryTab.tsx`, `apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts`, `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts`

* [ ] **Step 1: Write the failing narrative E2E test**

```ts
test('Backstage Story renders the full narrative composition', async ({ page }) => {
  await page.goto('/backstage/story');
  for (const id of ['hero', 'success-framework', 'devsecops-loop', 'review-sessions', 'po-classes']) {
    await expect(page.getByTestId(`backstage-${id}`)).toBeVisible();
  }
  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
  await expect(page.getByTestId('solution-design-section')).toBeVisible();
  await expect(page.locator('[data-testid^="backstage-nav-"]')).toHaveCount(3);
});
```

* [ ] **Step 2: Run + verify failure**

Run: `npx playwright test tests/e2e/solution-design.spec.ts` - FAIL (narrative sections absent).

* [ ] **Step 3: Implement DevSecOps loop + review sessions + six-lanes companion**

`DevSecOpsLoopSection` renders the DEV<->OPS loop as an accessible Fluent/SVG figure
with a text legend + HITL gate + DEV->SIT->PROD strip. `ReviewSessionsSection`
renders the 7-session table + practitioner grid; external LinkedIn links use
`target="_blank" rel="noopener"`. Add the compact six-lanes companion inside
`SolutionDesignSection` (mapping lanes to IQ layers) - not a standalone diagram.
Mount DevSecOps + review sessions + PO classes in `StoryTab` in composition order.

* [ ] **Step 4: Verify + a11y**

Ensure axe (`a11y.spec.ts`) covers the new sections with no exclusion. Run:

```powershell
npx playwright test tests/e2e/solution-design.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

Expected: PASS; no serious/critical WCAG 2.1 AA violation; exactly three Backstage
nav items.

* [ ] **Step 5: Commit**

```powershell
git add apps/hcc-app-fluent/src/workspaces/backstage/tabs/story apps/hcc-app-fluent/tests/e2e/solution-design.spec.ts apps/hcc-app-fluent/tests/e2e/a11y.spec.ts
git commit -m "feat(backstage): DevSecOps loop, review sessions, six-lanes companion"
```

## Task 9: Documentation and PR close-out

**Files:**

* Verify: `docs/superpowers/specs/2026-07-29-sprint-36-curavias-solution-design-backstage-design.md`
* Verify: `docs/superpowers/plans/2026-07-29-sprint-36-curavias-solution-design-backstage.md`

* [ ] **Step 1: Run document gates**

```powershell
python scripts/lint/check_mojibake.py docs/superpowers/specs/2026-07-29-sprint-36-curavias-solution-design-backstage-design.md docs/superpowers/plans/2026-07-29-sprint-36-curavias-solution-design-backstage.md
npx --yes markdownlint-cli2 "docs/superpowers/specs/2026-07-29-sprint-36-curavias-solution-design-backstage-design.md" "docs/superpowers/plans/2026-07-29-sprint-36-curavias-solution-design-backstage.md"
```

Expected: no mojibake and 0 Markdown issues.

* [ ] **Step 2: Confirm scope and contract boundaries**

```powershell
git diff --name-only origin/main...HEAD
rg "useCopilotRail|useConversation" apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/solution-design/SolutionDesignBoard.tsx
```

Expected: changed files are limited to the experience lane, the WS-D docs, and
Sprint 36 docs; the `rg` command returns no matches.

* [ ] **Step 3: Open the human-reviewed PR(s)**

Each workstream lands as its own squash PR linked to #540 and includes: the
requirements advanced (`FR-POA-002`, `FR-CX-006`, `FR-UX-001`, `FR-UX-004`,
`NFR-POA-001`, `NFR-POA-004`, `NFR-UX-001`..`NFR-UX-004`, `NFR-DOC-001`,
`FR-GOV-004`); lane
impact; no API/infra/MCP/PHI/deploy/delete impact; unit/lint/build/Playwright/
screenshot/axe evidence; residual risks. Never self-merge; a human reviews the
visual evidence and PO advisory/citation behavior first.

## Final acceptance checklist

* [ ] Full Backstage Story renders the 7-section composition in order; no 4th tab.
* [ ] Digital feedback loop (S35) + Solution design sections preserved and unbroken.
* [ ] Each narrative section routes to the docked PO rail; external links use `rel="noopener"`.
* [ ] Six-lanes companion maps into the Solution design section (one architecture diagram).
* [ ] Catalog has 5 layers + 2 lanes, unique IDs, valid tiers, no PHI.
* [ ] Section is inside Backstage Story; no fourth tab.
* [ ] Section header, plane headers, and badges route context to the PO rail.
* [ ] `SolutionDesignBoard` has no agent/runtime dependency.
* [ ] Desktop and narrow layouts have no overlap or horizontal scroll.
* [ ] Standalone `/present/solution-design` reuses the same board + catalog.
* [ ] `docs/SD.md` + `docs/GLOSSARY.md` reconciled to the new model, gate-clean.
* [ ] Unit, lint, build, Playwright, screenshot, and axe gates pass.
* [ ] Synthetic/no-PHI and advisory-only postures remain visible.
