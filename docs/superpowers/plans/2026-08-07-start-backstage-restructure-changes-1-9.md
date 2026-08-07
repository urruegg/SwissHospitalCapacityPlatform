# START / BACKSTAGE Restructure (Changes 1–9) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the Curavias Start pane to 6 sections and move BVA + 90‑day into Backstage, on top of a shared spacing + colour‑coded‑title kit, so both planes match the marketing‑approved mockup with full en/de/fr/it coverage.

**Architecture:** Land the two lowest‑risk shared primitives first (a structured‑`titleParts` `SectionHeader` and an opt‑in full‑height `NarrativeShell`), then restructure Start (remove Why‑now; move BVA + 90‑day out), then register the two Backstage wrappers, then close the i18n gaps, then produce a doc‑only context‑ask backlog. Every step is test‑first: write/adjust the vitest assertion, watch it go red, implement, watch it go green, commit.

**Tech Stack:** React 18 + TypeScript, Fluent UI v9 (`@fluentui/react-components`, Griffel `makeStyles`), react‑i18next, Vitest + Testing Library, Playwright + `@axe-core/playwright` for visual + a11y verification.

**Governing spec:** [`docs/superpowers/specs/2026-08-07-start-backstage-restructure-changes-1-9-design.md`](../specs/2026-08-07-start-backstage-restructure-changes-1-9-design.md) (v1.1.0, decisions D1–D4 locked).

---

## Ground rules (read once, apply to every task)

- **Experience lane only.** Touch `apps/hcc-app-fluent/**` and this plan's docs. No infra/data/AI/agent files. Synthetic, no PHI.
- **Commit to local `main`.** Do NOT push, do NOT merge, do NOT touch Draft PR #562 or the worktree branch `sprint-40/start-frontier-fidelity`.
- **Commit mechanics (PS 5.1):** stage ONLY the files named in the task (never `git add -A`). For multi‑line messages write an ASCII temp file and `git commit -F`:

  ```powershell
  Set-Content -Encoding ascii "$env:TEMP\start-refine\commit-msg.txt" @'
  <subject>

  <body>

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  '@
  git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform commit -F "$env:TEMP\start-refine\commit-msg.txt"
  ```

  The pre‑commit hook writes to stderr and exits 1 **even on success** — confirm the commit by the `[main <sha>]` line, not the exit code.
- **Every command runs from the app dir** unless stated: `cd apps\hcc-app-fluent`.
- **Vitest/npm reports exit 1 even on success** — trust the `N passed` text, not the exit code.
- **Heading name matching quirk:** `getByRole('heading', { name })` concatenates inline spans with an inserted space, so regexes must tolerate boundary whitespace (`Firm\s*` style). This matters for every `titleParts` assertion.
- **Griffel quirk:** never use the all‑sides `borderColor`/`border-color` shorthand in `makeStyles` (use the `border: '1px solid #hex'` string or side longhands).
- **Doc gates before committing any `.md`:** `python scripts\lint\check_mojibake.py <file>` (exit 0) and `npx --yes markdownlint-cli2 "<file>"` (Summary: 0 errors; allow ~120s — `npx` resolution is slow).

---

## File Structure

### Create

- `apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.test.tsx` — new unit test for the `titleParts` API (change 7).
- `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.tsx` — Backstage wrapper reusing the Start BVA body (change 2).
- `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.test.tsx` — render test for the BVA wrapper.
- `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageNinetyDaySection.tsx` — Backstage wrapper reusing the Start 90‑day body (change 3).
- `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageNinetyDaySection.test.tsx` — render test for the 90‑day wrapper.
- `docs/superpowers/backlog/2026-08-07-po-context-ask-stories.md` — doc‑only context‑ask story backlog (change 9).

### Modify

- `apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.tsx` — add structured `titleParts` + `headingLevel` (change 7).
- `apps/hcc-app-fluent/src/workspaces/shared/narrative/NarrativeShell.tsx` — opt‑in full‑height + `100svh` + observable `data-full` (change 6).
- `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx` — drop 3 moved/removed sections; add header→body stack; wire `titleParts` (changes 1–4, 6, 7).
- `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts` — shrink `StartSectionId` + `START_SECTIONS` to 6 (changes 1–3).
- `apps/hcc-app-fluent/src/workspaces/backstage/BackstageSubNav.tsx` — add `bva` at `[0]` and `ninety-day` at end (changes 2, 3, 8).
- `apps/hcc-app-fluent/src/workspaces/backstage/BackstageView.tsx` — register the two wrapper renderers (changes 2, 3).
- `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx` — adopt `titleParts` accent clauses (change 7).
- `apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.tsx` — mockup copy alignment + a11y (change 4).
- `apps/hcc-app-fluent/src/i18n/{en,de,fr,it}.json` — Backstage BVA/90‑day header keys, patient‑journey copy, fr/it vision + challenger fills, gloss labels (changes 2–5, 7).
- Test files updated in place: `start-content.test.ts`, `StaticNarrativeSections.test.tsx`, `BvaDecisionSection.test.tsx`.

---

## Workstream B — shared kit first (lowest risk, both planes depend on it)

### Task 1: `SectionHeader` structured `titleParts` API (change 7)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.test.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.tsx`

- [ ] **Step 1: Write the failing test**

Create `SectionHeader.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it } from 'vitest';
import { SectionHeader } from './SectionHeader';

function renderHeader(ui: React.ReactElement) {
  return render(<FluentProvider theme={webLightTheme}>{ui}</FluentProvider>);
}

describe('SectionHeader titleParts', () => {
  it('renders one heading whose accessible name concatenates all parts', () => {
    renderHeader(
      <SectionHeader
        id="demo"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        titleParts={[
          { text: 'Here is what it looks like ' },
          { text: 'solved.', tone: 'accent' },
        ]}
      />,
    );
    const heading = screen.getByRole('heading', {
      name: /Here is what it looks like\s*solved\./i,
    });
    expect(heading.tagName).toBe('H2');
  });

  it('marks the accent part with the accent class and no aria-hidden', () => {
    renderHeader(
      <SectionHeader
        id="demo2"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        titleParts={[
          { text: 'From the org chart to the ' },
          { text: 'work chart', tone: 'accent' },
        ]}
      />,
    );
    const accent = screen.getByText('work chart');
    expect(accent.getAttribute('aria-hidden')).toBeNull();
    expect(accent.getAttribute('data-tone')).toBe('accent');
  });

  it('falls back to the header string when titleParts is omitted', () => {
    renderHeader(
      <SectionHeader
        id="demo3"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        header="Plain heading"
      />,
    );
    expect(screen.getByRole('heading', { name: 'Plain heading' })).toBeInTheDocument();
  });

  it('honours headingLevel=1', () => {
    renderHeader(
      <SectionHeader
        id="demo4"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        headingLevel={1}
        titleParts={[{ text: 'Top-level' }]}
      />,
    );
    expect(screen.getByRole('heading', { level: 1, name: 'Top-level' })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps\hcc-app-fluent; npx vitest run src/workspaces/shared/narrative/SectionHeader.test.tsx`
Expected: FAIL — `titleParts` / `headingLevel` are not yet props; `data-tone` not rendered.

- [ ] **Step 3: Implement `titleParts` + `headingLevel` in `SectionHeader.tsx`**

Add to the props interface (keep `header` optional now that `titleParts` can supply the title):

```tsx
export interface SectionTitlePart {
  text: string;
  tone?: 'default' | 'accent';
}

interface SectionHeaderProps {
  id: string;
  header?: string;
  titleParts?: SectionTitlePart[];
  tagline: string;
  description: string;
  variant?: 'default' | 'eyebrow';
  headingLevel?: 1 | 2;
  tools?: React.ReactNode;
}
```

Add the accent style to `makeStyles` (solid‑colour fallback for forced‑colors; no all‑sides `borderColor`):

```tsx
  accent: {
    backgroundImage: 'linear-gradient(90deg, #365B7D, #17B890)',
    WebkitBackgroundClip: 'text',
    backgroundClip: 'text',
    color: 'transparent',
    '@media (forced-colors: active)': {
      color: 'LinkText',
      backgroundImage: 'none',
    },
  },
```

In the render, compute the heading tag and the title children. Replace the existing `<h2 … >{header}</h2>` in the eyebrow branch with:

```tsx
  const Heading = (headingLevel === 1 ? 'h1' : 'h2') as 'h1' | 'h2';
  const titleContent = titleParts
    ? titleParts.map((part, index) =>
        part.tone === 'accent' ? (
          <span key={index} className={styles.accent} data-tone="accent">
            {part.text}
          </span>
        ) : (
          <span key={index} data-tone="default">
            {part.text}
          </span>
        ),
      )
    : header;
```

```tsx
      <Heading id={`${id}-title`} className={styles.headerLg}>
        {titleContent}
      </Heading>
```

Ensure `headingLevel` and `titleParts` are destructured from props with sensible defaults (`headingLevel = 2`).

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run src/workspaces/shared/narrative/SectionHeader.test.tsx`
Expected: PASS (4/4).

- [ ] **Step 5: Type‑check**

Run: `npx tsc --noEmit`
Expected: clean (no errors).

- [ ] **Step 6: Commit**

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform add apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.tsx apps/hcc-app-fluent/src/workspaces/shared/narrative/SectionHeader.test.tsx
```

Commit subject: `feat(narrative): add structured titleParts + headingLevel to SectionHeader` (+ Co‑authored‑by trailer). Verify via the `[main <sha>]` line.

---

### Task 2: `NarrativeShell` opt‑in full‑height + `100svh` (change 6)

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/shared/narrative/NarrativeShell.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx` (add the shared header→body stack)

- [ ] **Step 1: Write the failing test (opt‑in observability)**

Add to `apps/hcc-app-fluent/src/workspaces/start/frontier/StaticNarrativeSections.test.tsx` a focused assertion near the existing structure block:

```tsx
  it('does not force full-height on ordinary Start sections', () => {
    renderStart();
    const hospitals = screen.getByTestId('start-hospitals');
    // The opt-in flag is observable via data-full; ordinary sections must not set it.
    expect(hospitals.closest('[data-full="true"]')).toBeNull();
  });
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/workspaces/start/frontier/StaticNarrativeSections.test.tsx -t "full-height"`
Expected: FAIL — no `data-full` attribute exists yet, and the current shell wraps every trailing section in the min‑height `sectionFull` class.

- [ ] **Step 3: Make full‑height opt‑in in `NarrativeShell.tsx`**

Add an optional flag to the section model interface:

```tsx
  full?: boolean;
```

In the full‑section render branch, gate the `sectionFull` class on the flag and expose it:

```tsx
        <section
          key={section.key}
          id={section.key}
          data-full={section.full ? 'true' : undefined}
          className={mergeClasses(styles.section, section.full ? styles.sectionFull : undefined)}
        >
          {section.render()}
        </section>
```

In `makeStyles`, replace `100vh` with `100svh` in both `sectionFull` and `leadGroup`, and drop the min‑height from the default `section` style so short sections size to content:

```tsx
  sectionFull: {
    minHeight: 'calc(100svh - 150px)',
  },
  leadGroup: {
    minHeight: 'calc(100svh - 120px)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
```

Keep the `sections` container gap at `tokens.spacingVerticalXXL` (24px) for the section‑to‑section rhythm.

- [ ] **Step 4: Add the shared header→body stack in `StartView.tsx`**

Add a style and apply it to the per‑section wrapper so the eyebrow/title/lead group and the body get a token gap (24px desktop). In the `makeStyles` block:

```tsx
  sectionStack: {
    display: 'flex',
    flexDirection: 'column',
    rowGap: tokens.spacingVerticalXXL,
  },
```

Apply it to the `<section data-start-section>` wrapper:

```tsx
      <section
        key={id}
        data-start-section={id}
        data-testid={`start-${id}`}
        className={styles.sectionStack}
      >
```

(If `styles`/`tokens` are not already imported in `StartView.tsx`, add `import { makeStyles, tokens } from '@fluentui/react-components';` and a `useStyles` hook.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `npx vitest run src/workspaces/start/frontier/StaticNarrativeSections.test.tsx`
Expected: PASS (the new full‑height test green; existing structure tests unaffected).
Run: `npx tsc --noEmit`
Expected: clean.

- [ ] **Step 6: Commit**

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform add apps/hcc-app-fluent/src/workspaces/shared/narrative/NarrativeShell.tsx apps/hcc-app-fluent/src/workspaces/start/StartView.tsx apps/hcc-app-fluent/src/workspaces/start/frontier/StaticNarrativeSections.test.tsx
```

Subject: `refactor(narrative): make full-height opt-in, use 100svh, add token header/body gap`.

---

### Task 3: Roll out colour‑coded `titleParts` across both planes (change 7)

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx`

Use the exact emphasis clauses from spec §3.7 (accent = the clause named per title).

- [ ] **Step 1: Extend the Start section metadata with an optional accent clause**

In `StartView.tsx`, the `SECTION_META` record entries currently carry `eyebrowKey`, `titleKey`, `descriptionKey`. Add an optional `accentKey?: string` (i18n key for the accent clause) per section that needs colour‑coding. Then in the render, when `accentKey` is present, split the resolved title into a prefix + accent using the resolved accent string, and pass `titleParts` instead of `header`:

```tsx
  const title = t(meta.titleKey);
  const accent = meta.accentKey ? t(meta.accentKey) : undefined;
  const titleParts =
    accent && title.includes(accent)
      ? [
          { text: title.slice(0, title.indexOf(accent)) },
          { text: accent, tone: 'accent' as const },
          { text: title.slice(title.indexOf(accent) + accent.length) },
        ].filter((part) => part.text.length > 0)
      : undefined;
```

```tsx
        <SectionHeader
          id={id}
          variant="eyebrow"
          tagline={t(meta.eyebrowKey)}
          {...(titleParts ? { titleParts } : { header: title })}
          description={t(meta.descriptionKey)}
        />
```

Add `accentKey` values for the Start titles per spec §3.7 (e.g. challenger accent = the closing question clause, vision accent = `cura + via`, work‑chart accent = `work chart`, hospitals accent = `Frontier Firm`, patient‑path accent = `humans and agents together`). Introduce the accent i18n keys in Task order alongside — see Step 3.

- [ ] **Step 2: Write the failing assertion**

In `StaticNarrativeSections.test.tsx`, assert one representative accent renders as an accent span (not a separate heading):

```tsx
  it('colour-codes the work-chart accent clause within a single heading', () => {
    renderStart();
    const heading = screen.getByRole('heading', { name: /From the org chart to the\s*work chart/i });
    expect(within(heading).getByText('work chart').getAttribute('data-tone')).toBe('accent');
  });
```

Run: `npx vitest run src/workspaces/start/frontier/StaticNarrativeSections.test.tsx -t "colour-codes"`
Expected: FAIL until Step 3 adds the accent key + wiring.

- [ ] **Step 3: Add accent i18n keys (en/de/fr/it) and wire the Backstage headers**

For each colour‑coded title add a sibling `accent` key next to the existing title key in all four locale files, e.g. under `start.frontier.workChart`:

```json
"accent": "work chart"
```

The accent string MUST be a verbatim substring of the localized title in every locale (so the `title.includes(accent)` split works). In `BackstageNarrativeSections.tsx`, convert each `<SectionHeader … header={t('…header')} … />` to pass `titleParts` built from a new `…accent` key using the same split helper (extract a small local `toTitleParts(title, accent)` function to avoid duplication). Cover the Backstage emphasis clauses from spec §3.7 (success = `We became one.`, po‑classes = `hard questions`, devsecops = `built & shipped`, reviews = `real people`).

- [ ] **Step 4: Run tests + type‑check**

Run: `npx vitest run src/workspaces/start/frontier/StaticNarrativeSections.test.tsx`
Run: `npx vitest run src/workspaces/backstage`
Run: `npx tsc --noEmit`
Expected: all green / clean.

- [ ] **Step 5: Mojibake gate on the locale files**

Run: `python scripts\lint\check_mojibake.py apps\hcc-app-fluent\src\i18n\en.json apps\hcc-app-fluent\src\i18n\de.json apps\hcc-app-fluent\src\i18n\fr.json apps\hcc-app-fluent\src\i18n\it.json`
Expected: exit 0.

- [ ] **Step 6: Commit**

Stage `StartView.tsx`, `BackstageNarrativeSections.tsx`, the 4 locale files, and `StaticNarrativeSections.test.tsx`.
Subject: `feat(narrative): colour-code section title keywords via titleParts across Start + Backstage`.

---

## Workstream A — Start restructure (changes 1–4)

### Task 4: Remove Why‑now from the Start registry (change 1, D3)

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.test.ts`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/StaticNarrativeSections.test.tsx`

> D3: remove only — add nothing to other sections. Keep `CioChallengerSection.tsx`, `CIO_DECISIONS`, and the `cioWhyNow.*` i18n as reversible dead data.

- [ ] **Step 1: Update the order tests (RED‑first) — drop `cio-why-now`**

In `start-content.test.ts`, change the `START_SECTIONS` id assertion to the target 6 (also dropping `ninety-day` + `bva`, handled in Tasks 5–6; do the full shrink now so the test is authored once):

```ts
    expect(START_SECTIONS.map((section) => section.id)).toEqual([
      'hero',
      'challenger',
      'vision',
      'work-chart',
      'hospitals',
      'patient-path',
    ]);
```

In `StaticNarrativeSections.test.tsx`, update the rendered‑order array (currently 9 entries) to the same 6, remove the `start-nav-cio-why-now` de‑nav assertion, and change the section‑contains loop to `['work-chart', 'hospitals']`.

- [ ] **Step 2: Run to verify red**

Run: `npx vitest run src/workspaces/start/frontier/start-content.test.ts src/workspaces/start/frontier/StaticNarrativeSections.test.tsx`
Expected: FAIL (code still lists 9 sections).

- [ ] **Step 3: Remove `cio-why-now` from the registry**

In `start-content.ts`: delete `'cio-why-now'` from the `StartSectionId` union and delete its row from `START_SECTIONS`.
In `StartView.tsx`: delete the `cio-why-now` entry from `SECTION_META` and its `case 'cio-why-now':` from `sectionBody()`; remove the now‑unused `CioChallengerSection` import.

- [ ] **Step 4: Run to verify green + type‑check**

Run: `npx vitest run src/workspaces/start/frontier/start-content.test.ts src/workspaces/start/frontier/StaticNarrativeSections.test.tsx`
Run: `npx tsc --noEmit`
Expected: the order assertions pass for the removal; Tasks 5–6 will make the remaining 6‑item expectation fully green once BVA + 90‑day are moved. (If Task 5/6 are executed in the same session, expect green now; if not, the 6‑item array is the final target and the code still lists `ninety-day`/`bva` — so run this task together with Tasks 5–6 before asserting full green. See sequencing note below.)

> **Sequencing note:** Tasks 4, 5, and 6 all edit the same `START_SECTIONS` order assertion. Execute them back‑to‑back, and only run the full order assertion green after Task 6. Within each task, the code edit for that task's section is the unit of work; the shared test is authored once in Task 4.

- [ ] **Step 5: Commit**

Stage the 2 code files + 2 test files.
Subject: `refactor(start): remove Why-now section from the Start registry (keep data as reversible)`.

---

### Task 5: Move BVA into Backstage as the first part (change 2, D4)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.tsx`
- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.test.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageSubNav.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageView.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.test.tsx`
- Modify: `apps/hcc-app-fluent/src/i18n/{en,de,fr,it}.json`

> D4: keep the real data‑bound BVA figures (212% / CHF 4.2M). Reuse `BvaDecisionSection.tsx` unchanged; only wrap it with a Backstage header. Its `scrollToSection('ninety-day')` (line 439) resolves within Backstage after Task 6.

- [ ] **Step 1: Write the wrapper render test (RED‑first)**

Create `BackstageBvaSection.test.tsx`:

```tsx
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import * as goldenSourceClient from '../../../../../data/goldenSourceClient';
import { BackstageBvaSection } from './BackstageBvaSection';

describe('BackstageBvaSection', () => {
  it('renders a Backstage header above the reused BVA decision body', () => {
    vi.spyOn(goldenSourceClient, 'loadSiteCapacitySummary').mockImplementation(
      () => new Promise(() => {}),
    );
    render(
      <FluentProvider theme={webLightTheme}>
        <MemoryRouter>
          <BackstageBvaSection />
        </MemoryRouter>
      </FluentProvider>,
    );
    const section = screen.getByTestId('backstage-bva-section');
    expect(within(section).getByTestId('bva-decision-section')).toBeInTheDocument();
    expect(within(section).getByRole('heading', { name: /BVA on ourselves/i })).toBeInTheDocument();
  });
});
```

(Adjust the `goldenSourceClient` import path to the real module used by `BvaDecisionSection.test.tsx` — copy it verbatim from that file's mock import.)

- [ ] **Step 2: Run to verify red**

Run: `npx vitest run src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.test.tsx`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Create the wrapper**

`BackstageBvaSection.tsx`:

```tsx
import { useTranslation } from 'react-i18next';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import { BvaDecisionSection } from '../../../../start/frontier/BvaDecisionSection';

export function BackstageBvaSection() {
  const { t } = useTranslation();
  const title = t('backstage.story.bva.title', 'We ran a BVA on ourselves before writing a line of code');
  const accent = t('backstage.story.bva.accent', 'BVA on ourselves');
  const parts = title.includes(accent)
    ? [
        { text: title.slice(0, title.indexOf(accent)) },
        { text: accent, tone: 'accent' as const },
        { text: title.slice(title.indexOf(accent) + accent.length) },
      ].filter((part) => part.text.length > 0)
    : [{ text: title }];

  return (
    <section data-testid="backstage-bva-section" aria-labelledby="bva-title">
      <SectionHeader
        id="bva"
        variant="eyebrow"
        tagline={t('backstage.story.bva.eyebrow', 'Backstage \u00b7 the business case')}
        titleParts={parts}
        description={t('backstage.story.bva.lead', 'Before a line of code, Curavias ran a business value assessment on itself \u2014 the same discipline it brings to a hospital.')}
      />
      <BvaDecisionSection />
    </section>
  );
}
```

- [ ] **Step 4: Add the i18n keys (en/de/fr/it)**

Add a `backstage.story.bva` block (`eyebrow`, `title`, `accent`, `lead`) to all four locale files, with `accent` a verbatim substring of `title` in each locale.

- [ ] **Step 5: Register in Backstage nav + renderers**

In `BackstageSubNav.tsx`, add `'bva'` as the FIRST entry of `BACKSTAGE_PARTS` (with its nav label key). In `BackstageView.tsx`, add to the `RENDERERS` map: `bva: () => <BackstageBvaSection />` and import it.

- [ ] **Step 6: Remove BVA from the Start registry**

In `start-content.ts`: remove `'bva'` from `StartSectionId` + its `START_SECTIONS` row. In `StartView.tsx`: remove the `bva` `SECTION_META` entry + `case 'bva':` + the `BvaDecisionSection` import (Start no longer renders it directly).

- [ ] **Step 7: Update `BvaDecisionSection.test.tsx` order test**

The test at lines ~186–212 renders `<StartView />` and asserts `start-bva` in the order. Replace its `expect(sectionIds).toEqual([...])` with the target 6‑id Start order (no `start-bva`, no `start-ninety-day`, no `start-cio-why-now`):

```ts
    expect(sectionIds).toEqual([
      'start-hero',
      'start-challenger',
      'start-vision',
      'start-work-chart',
      'start-hospitals',
      'start-patient-path',
    ]);
```

Remove the now‑invalid `start-bva` presence assertions from that specific test (the KPI‑binding tests earlier in the file that render `<BvaDecisionSection />` directly stay untouched — the component is unchanged).

- [ ] **Step 8: Run tests + type‑check + mojibake**

Run: `npx vitest run src/workspaces/backstage/tabs/story/moved/BackstageBvaSection.test.tsx src/workspaces/start/frontier/BvaDecisionSection.test.tsx src/workspaces/backstage`
Run: `npx tsc --noEmit`
Run: `python scripts\lint\check_mojibake.py apps\hcc-app-fluent\src\i18n\en.json apps\hcc-app-fluent\src\i18n\de.json apps\hcc-app-fluent\src\i18n\fr.json apps\hcc-app-fluent\src\i18n\it.json`
Expected: green / clean / exit 0.

- [ ] **Step 9: Commit**

Stage the 2 new wrapper files, `BackstageSubNav.tsx`, `BackstageView.tsx`, `start-content.ts`, `StartView.tsx`, `BvaDecisionSection.test.tsx`, and the 4 locale files.
Subject: `feat(backstage): move BVA from Start into Backstage as the first part`.

---

### Task 6: Move 90‑day into Backstage as the last part (change 3, D2)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageNinetyDaySection.tsx`
- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/moved/BackstageNinetyDaySection.test.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageSubNav.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageView.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx`
- Modify: `apps/hcc-app-fluent/src/i18n/{en,de,fr,it}.json`

> D2: 90‑day goes at the END of `BACKSTAGE_PARTS`. Carry the PROD disclaimer (already in `NinetyDaySection.tsx`).

- [ ] **Step 1: Write the wrapper render test (RED‑first)**

Create `BackstageNinetyDaySection.test.tsx`:

```tsx
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { BackstageNinetyDaySection } from './BackstageNinetyDaySection';

describe('BackstageNinetyDaySection', () => {
  it('renders a Backstage header above the reused 90-day body with its PROD disclaimer', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <MemoryRouter>
          <BackstageNinetyDaySection />
        </MemoryRouter>
      </FluentProvider>,
    );
    const section = screen.getByTestId('backstage-ninety-day-section');
    expect(within(section).getByRole('heading', { name: /90 days/i })).toBeInTheDocument();
    expect(within(section).getByText(/live in PROD Switzerland North/i)).toBeInTheDocument();
  });
});
```

(Confirm the disclaimer substring against `start.frontier.ninetyDay.disclaimer` in `en.json`; adjust the regex to a stable phrase from that string.)

- [ ] **Step 2: Run to verify red**

Run: `npx vitest run src/workspaces/backstage/tabs/story/moved/BackstageNinetyDaySection.test.tsx`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Create the wrapper**

`BackstageNinetyDaySection.tsx`:

```tsx
import { useTranslation } from 'react-i18next';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import { NinetyDaySection } from '../../../../start/frontier/NinetyDaySection';

export function BackstageNinetyDaySection() {
  const { t } = useTranslation();
  const title = t('backstage.story.ninetyDay.title', 'Your first frontier: capacity forecast in 90 days');
  const accent = t('backstage.story.ninetyDay.accent', '90 days');
  const parts = title.includes(accent)
    ? [
        { text: title.slice(0, title.indexOf(accent)) },
        { text: accent, tone: 'accent' as const },
        { text: title.slice(title.indexOf(accent) + accent.length) },
      ].filter((part) => part.text.length > 0)
    : [{ text: title }];

  return (
    <section data-testid="backstage-ninety-day-section" aria-labelledby="ninety-day-title">
      <SectionHeader
        id="ninety-day"
        variant="eyebrow"
        tagline={t('backstage.story.ninetyDay.eyebrow', 'Backstage \u00b7 the first frontier')}
        titleParts={parts}
        description={t('backstage.story.ninetyDay.lead', 'The repeatable path a new provider follows \u2014 from aligned decisions to a governed, live forecast.')}
      />
      <NinetyDaySection />
    </section>
  );
}
```

- [ ] **Step 4: Add the i18n keys (en/de/fr/it)**

Add `backstage.story.ninetyDay` (`eyebrow`, `title`, `accent`, `lead`) to all four locale files, `accent` a verbatim substring of `title`.

- [ ] **Step 5: Register at the END of Backstage nav + renderers**

In `BackstageSubNav.tsx`, append `'ninety-day'` as the LAST entry of `BACKSTAGE_PARTS`. In `BackstageView.tsx`, add `'ninety-day': () => <BackstageNinetyDaySection />` to `RENDERERS` and import it.

- [ ] **Step 6: Remove 90‑day from the Start registry**

In `start-content.ts`: remove `'ninety-day'` from `StartSectionId` + `START_SECTIONS`. In `StartView.tsx`: remove `ninety-day` from `SECTION_META`, its `case`, and the `NinetyDaySection` import.

- [ ] **Step 7: Verify the BVA→90‑day cross‑link still resolves**

`BvaDecisionSection.tsx:439` calls `scrollToSection('ninety-day')`. Confirm the Backstage part key is exactly `'ninety-day'` so the anchor id matches. Add an assertion in `BackstageBvaSection.test.tsx` is optional; a manual Playwright click check is covered in Task 11.

- [ ] **Step 8: Run the full Start order assertion green + type‑check + mojibake**

Run: `npx vitest run src/workspaces/start src/workspaces/backstage`
Expected: the 6‑item `START_SECTIONS` order (authored in Task 4) now passes fully; Backstage now lists `bva … ninety-day`.
Run: `npx tsc --noEmit` → clean.
Run mojibake on the 4 locale files → exit 0.

- [ ] **Step 9: Commit**

Stage the 2 new wrapper files, `BackstageSubNav.tsx`, `BackstageView.tsx`, `start-content.ts`, `StartView.tsx`, and the 4 locale files.
Subject: `feat(backstage): move 90-day roadmap from Start to the end of Backstage`.

---

### Task 7: Patient‑journey copy alignment + a11y (change 4)

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.tsx` (copy only)
- Modify: `apps/hcc-app-fluent/src/i18n/{en,de,fr,it}.json` (only if a copy string is missing/changed)
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.test.tsx`

> Adopt the mockup eyebrow/title/lead/worked‑example COPY only. KEEP the patient‑flow visual, the DC‑INSIGHT worked example structure, `/main/*` routing, `rail.openWithReco`, and the current `<ol>/<li>` a11y.

- [ ] **Step 1: Diff the mockup copy vs the live strings**

Open `docs/superpowers/ideas/Curavias-Frontier-Showcase.html` patient‑journey block and compare against `start.frontier.patientPath.*` + `start.frontier.nav.carePath` in `en.json`. The Start title already reads `One patient, one flow — humans and agents together`; confirm the eyebrow ("Key visual 2 · Patient journey") and lead match the mockup, and note any DC‑INSIGHT wording drift.

- [ ] **Step 2: Write/adjust the failing copy assertion**

In `PatientPathLauncher.test.tsx`, add an assertion locking the mockup eyebrow + lead phrasing (use the exact approved strings):

```tsx
  it('uses the mockup patient-journey eyebrow and lead copy', () => {
    renderLauncher();
    expect(screen.getByText(/Key visual 2/i)).toBeInTheDocument();
    expect(screen.getByText(/One patient, one flow/i)).toBeInTheDocument();
  });
```

Run: `npx vitest run src/workspaces/start/frontier/PatientPathLauncher.test.tsx -t "mockup patient-journey"`
Expected: FAIL if the eyebrow/lead strings differ from the mockup.

- [ ] **Step 3: Align the copy**

Update only the affected `start.frontier.patientPath.*` (and, if the section eyebrow is sourced from `SECTION_META`, the corresponding `nav`/eyebrow key) in all four locale files to the approved mockup wording. Do not change the visual, routing, or the DC‑INSIGHT structure.

- [ ] **Step 4: a11y verification**

Run the axe harness against the patient‑path section on the live dev server (see Task 11 harness). Confirm: the journey has an accessible name (`journeyLabel`), the flow is keyboard reachable, and on a narrow viewport the visual scrolls horizontally without clipping. Record 0 serious/critical.

- [ ] **Step 5: Run tests + type‑check + mojibake**

Run: `npx vitest run src/workspaces/start/frontier/PatientPathLauncher.test.tsx`
Run: `npx tsc --noEmit`
Run mojibake on the 4 locale files.
Expected: green / clean / exit 0.

- [ ] **Step 6: Commit**

Stage `PatientPathLauncher.tsx` (if changed), the 4 locale files, and the test.
Subject: `feat(start): align patient-journey copy to the mockup (visual + routing unchanged)`.

---

## Workstream C — Backstage integration verification (change 8, D1)

### Task 8: Verify Backstage sub‑nav with the two new parts (D1 = no six‑lane section)

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/BackstageSubNav.tsx` (only if a nav‑label i18n key is missing)
- Modify: a Backstage nav test (existing `DigitalFeedbackLoop.test.tsx` sits nearby; add a small `BackstageSubNav` order test if none exists)

> D1: keep the existing Frontier Architecture (`solution-design`) as‑is; do NOT add a six‑lane section. Net‑new Backstage parts = BVA + 90‑day only (delivered in Tasks 5–6). This task is verification + nav hygiene.

- [ ] **Step 1: Write the nav‑order assertion (RED if labels/keys missing)**

Add a test asserting `BACKSTAGE_PARTS` starts with `bva` and ends with `ninety-day`, and that every part has a localized nav label in en + de:

```tsx
  it('orders Backstage parts bva … ninety-day with localized labels', () => {
    expect(BACKSTAGE_PARTS[0]).toBe('bva');
    expect(BACKSTAGE_PARTS[BACKSTAGE_PARTS.length - 1]).toBe('ninety-day');
  });
```

- [ ] **Step 2: Run to verify**

Run: `npx vitest run src/workspaces/backstage`
Expected: PASS after Tasks 5–6; if a nav label key is missing it will surface as an untranslated fallback — add the missing `backstage` nav label keys in en/de/fr/it.

- [ ] **Step 3: Sub‑nav overflow + keyboard check (manual, documented)**

On the live dev server, confirm the Backstage sub‑nav (now 8 parts) does not clip on a 1024px viewport, wraps or scrolls gracefully, and remains arrow‑key navigable. Record the result in the commit body.

- [ ] **Step 4: Commit (only if files changed)**

Stage the nav test (+ any locale label additions).
Subject: `test(backstage): verify sub-nav order + labels after BVA/90-day moves`.

---

## Change 5 — i18n coverage sweep

### Task 9: Fill fr/it gaps + gloss labels + missing‑key guard

**Files:**

- Modify: `apps/hcc-app-fluent/src/i18n/{fr,it}.json` (vision + challenger prose; gloss labels in all four as needed)
- Create/Modify: an i18n coverage test under `apps/hcc-app-fluent/src/i18n/` (e.g. `i18n-coverage.test.ts`)

> Fill the flagged fr/it gaps: `nav.vision` + the whole `start.frontier.vision` block, and the `challenger` deep‑narrative prose. Keep the verbatim‑quote + English‑gloss governance pattern; add visible gloss labels ("Original quote" / "English gloss").

- [ ] **Step 1: Write the missing‑key guard test (RED‑first)**

Create `apps/hcc-app-fluent/src/i18n/i18n-coverage.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import en from './en.json';
import de from './de.json';
import fr from './fr.json';
import it from './it.json';

function keys(obj: unknown, prefix = ''): string[] {
  if (obj === null || typeof obj !== 'object') return [prefix];
  return Object.entries(obj as Record<string, unknown>).flatMap(([k, v]) =>
    keys(v, prefix ? `${prefix}.${k}` : k),
  );
}

const START_AND_BACKSTAGE = (all: string[]) =>
  all.filter((k) => k.startsWith('start.frontier.') || k.startsWith('backstage.story.'));

describe('i18n coverage for START + BACKSTAGE', () => {
  const enKeys = new Set(START_AND_BACKSTAGE(keys(en)));
  it.each([
    ['de', de],
    ['fr', fr],
    ['it', it],
  ])('%s has no missing START/BACKSTAGE keys vs en', (_name, locale) => {
    const localeKeys = new Set(START_AND_BACKSTAGE(keys(locale)));
    const missing = [...enKeys].filter((k) => !localeKeys.has(k));
    expect(missing).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify red**

Run: `npx vitest run src/i18n/i18n-coverage.test.ts`
Expected: FAIL — fr/it are missing the vision + challenger keys (and any brand keys intentionally omitted). For brand copy that is intentionally identical across locales (the bilingual `{primary,echo}` pattern), either add the identical value or scope the guard to exclude those specific keys with a documented allow‑list constant at the top of the test.

- [ ] **Step 3: Fill the gaps**

Add the missing `nav.vision`, `start.frontier.vision.*`, and `start.frontier.challenger.*` prose to `fr.json` and `it.json`. Translate chrome; for verbatim dated review quotes keep the original language and add the English gloss with the visible label keys (`start.frontier.challenger.glossOriginalLabel` = "Original quote", `…glossEnglishLabel` = "English gloss") in all four locales. Where the design intentionally keeps a value identical across locales, add it verbatim or list it in the test's allow‑list.

- [ ] **Step 4: Run to verify green + mojibake**

Run: `npx vitest run src/i18n/i18n-coverage.test.ts`
Run: `python scripts\lint\check_mojibake.py apps\hcc-app-fluent\src\i18n\fr.json apps\hcc-app-fluent\src\i18n\it.json apps\hcc-app-fluent\src\i18n\en.json apps\hcc-app-fluent\src\i18n\de.json`
Expected: PASS / exit 0.

- [ ] **Step 5: Commit**

Stage `fr.json`, `it.json`, en/de (if gloss labels added), and the new coverage test.
Subject: `feat(i18n): fill fr/it vision + challenger coverage and add START/BACKSTAGE key guard`.

---

## Change 9 — context‑ask story backlog (DOC ONLY, separate sprint)

### Task 10: Write the PO context‑ask story backlog

**Files:**

- Create: `docs/superpowers/backlog/2026-08-07-po-context-ask-stories.md`

> Doc only — do NOT implement any context‑ask wiring in code this sprint. Transcribe the 30‑ask inventory from spec §3.9, one story per ask, each tagged with its knowledge class (A retrieveCorpus / B liveProof / C costAnswer / D ontologyQuery) and the section it belongs to.

- [ ] **Step 1: Create the backlog doc with the SemVer header**

Author the file with the standard doc header (Version 1.0.0, Date 2026‑08‑07, Author Urs Rüegg, Status Draft, Previous Version none) and a table: `Story ID | Section | Context ask | Knowledge class | Grounding source (doc vs PROD evidence) | Acceptance note`. Fill every row from spec §3.9 (30 asks). Add a short intro paragraph stating this is a backlog for a future PO‑agent validation sprint, advisory‑only, no code in this sprint.

- [ ] **Step 2: Doc gates**

Run: `python scripts\lint\check_mojibake.py docs\superpowers\backlog\2026-08-07-po-context-ask-stories.md`
Run: `npx --yes markdownlint-cli2 "docs/superpowers/backlog/2026-08-07-po-context-ask-stories.md"`
Expected: exit 0 / Summary: 0 errors.

- [ ] **Step 3: Commit**

Stage the backlog doc.
Subject: `docs(backlog): add PO context-ask story inventory (30 asks, doc-only)`.

---

## Final verification

### Task 11: Full‑suite + a11y + visual conformance pass

- [ ] **Step 1: Full Start + Backstage test suites**

Run: `cd apps\hcc-app-fluent; npx vitest run src/workspaces/start src/workspaces/backstage src/workspaces/shared/narrative src/i18n`
Expected: all `N passed`.

- [ ] **Step 2: Type‑check**

Run: `npx tsc --noEmit`
Expected: clean.

- [ ] **Step 3: axe AA on every changed section (en + de)**

Use the Sprint 27 axe harness (`%TEMP%\start-refine\axe-section.js`) against `localhost:5173/start` and `/backstage` for: hero, challenger, vision, work‑chart, hospitals, patient‑path (Start) and bva, success‑framework, ninety‑day (Backstage). Expected: 0 serious/critical each, both locales.

- [ ] **Step 4: Visual conformance vs mockup**

Screenshot each restructured section (en + de) via the `shot.js` harness. Confirm: Start = 6 sections in order; BVA + 90‑day now render under Backstage (BVA first, 90‑day last); colour‑coded title keyword renders on both planes; section spacing is even (no oversized gaps). Confirm the BVA→90‑day in‑page link scrolls within Backstage.

- [ ] **Step 5: Update session tracking + plan.md**

Record the shipped commits and mark the changes 1–9 complete (except change 9 = backlog doc only) in `plan.md` and the SQL `c19` table.

- [ ] **Step 6: Final commit (docs/tracking only, if any)**

Stage only `plan.md`‑adjacent doc artifacts (session‑state `plan.md` is not in the repo; no commit needed for it). No app‑code changes in this task.

---

## Self‑review (run after drafting, before execution)

- **Spec coverage:** change 1 → Task 4; change 2 → Task 5; change 3 → Task 6; change 4 → Task 7; change 5 → Task 9; change 6 → Task 2; change 7 → Tasks 1 + 3; change 8 → Task 8 (D1 = no six‑lane); change 9 → Task 10. Verification → Task 11. All nine covered.
- **Decisions:** D1 (keep Frontier Architecture, no six‑lane) → Task 8; D2 (90‑day at end) → Task 6 Step 5; D3 (remove Why‑now, add nothing) → Task 4; D4 (keep real BVA figures) → Task 5 (reuse `BvaDecisionSection` unchanged).
- **Type consistency:** the accent‑split helper (`title.includes(accent)` → prefix/accent/suffix `titleParts`) is identical in Tasks 3, 5, 6; `tone: 'accent' as const` is used consistently; wrapper names `BackstageBvaSection` / `BackstageNinetyDaySection` are stable across create + register + test tasks; the `data-tone`/`data-full` observable attributes are the testable contract (avoids brittle Griffel class assertions).
- **Sequencing risk:** the shared `START_SECTIONS` 6‑item order assertion is authored once in Task 4 and only fully green after Task 6 — the sequencing note flags this so an engineer running tasks out of order is not surprised.
- **Placeholder scan:** no TBD/TODO; every code step shows complete code; every command has an expected result.
