# Sprint 40 — Curavias Start-Pane Frontier-Showcase Fidelity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-06 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Design spec** | [`2026-08-06-sprint-40-start-frontier-fidelity-design.md`](../specs/2026-08-06-sprint-40-start-frontier-fidelity-design.md) |
| **Sprint backlog** | [`docs/sprints/sprint-40-curavias-start-frontier-fidelity.md`](../../sprints/sprint-40-curavias-start-frontier-fidelity.md) |

**Goal:** Bring the Curavias app Start pane (`/start`) to content + visual fidelity with
the Frontier-Showcase mockup, natively in Fluent v9 + the codified design system, using a
content-intake phase followed by a per-section visual verify loop.

**Architecture:** Extend the declarative Start content model + shared design-system recipes,
key the section eyebrows for i18n, then walk each of the eight Start sections through the
Sprint 27 local visual-verify loop (edit → hot-reload → re-snapshot → axe), one PR-sized
section group per milestone. Experience-lane only (`NFR-UX-004`).

**Tech Stack:** React 18 + Fluent UI v9, TypeScript, Vite, Vitest, Playwright + axe-core,
`react-i18next` (en/de/fr/it), the app design system (`src/theme/design-system`).

---

## Ground rules

- **TDD.** For every content-model / behaviour change: write the failing Vitest first, watch
  it fail, implement minimally, watch it pass, commit.
- **Visual work is inspection-driven, not guessed.** Phase 2 token/spacing edits are made
  against the live `http://localhost:5173/start` per the runbook. Steps below give the exact
  gap to close, the file to touch, and the gate that proves it — they do **not** pre-invent
  pixel values that can only be set with eyes on the rendered section.
- **Commands are run from the repo root** unless a step says otherwise. The app lives under
  `apps/hcc-app-fluent`; use the `npm --prefix apps/hcc-app-fluent run <script>` form.
- **Every doc edit** bumps its SemVer header (copilot-instructions §9) and passes
  `npx markdownlint-cli2` + `python scripts/lint/check_mojibake.py`.
- **Draft PR per milestone**, human-merged. The agent never self-merges and invokes no
  `deploy`/`delete` tool.
- **Conventional Commits** with the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.

Reference commands (verified against `apps/hcc-app-fluent/package.json`):

```bash
npm --prefix apps/hcc-app-fluent run dev        # vite dev server on :5173
npm --prefix apps/hcc-app-fluent run lint       # tsc --noEmit
npm --prefix apps/hcc-app-fluent run test        # vitest run
npm --prefix apps/hcc-app-fluent run test:a11y   # playwright axe (tests/e2e/a11y.spec.ts)
npm --prefix apps/hcc-app-fluent run build       # tsc -b && vite build
```

---

## File structure

Files created or modified in this sprint, by responsibility:

```text
apps/hcc-app-fluent/src/
  workspaces/start/
    StartView.tsx                       # MODIFY: key eyebrows via i18n; hero eyebrow at shell
    frontier/
      start-content.ts                  # MODIFY: + FRONTIER_AGENTS, DC_INSIGHT_BEATS,
                                        #   WORKED_EXAMPLE, BVA_TCO_ROWS, BVA_VALUE_LEVERS,
                                        #   BVA_SENSITIVITY, BVA_PROOF_CHIPS
      start-content.test.ts             # MODIFY: assertions for every new structure
      StartHero.tsx                     # MODIFY: promote to P14 eyebrow header; KPI-tile recipe
      WorkChartSection.tsx              # MODIFY: triad + principle mini-table recipe
      CioChallengerSection.tsx          # MODIFY: decision mini-table restyle
      HospitalsSection.tsx              # MODIFY: glyph cards + agent-roster strip
      PatientPathLauncher.tsx           # MODIFY: 5-stop beat strip + DC-INSIGHT + worked example
      NinetyDaySection.tsx              # MODIFY: phase device + live-in-PROD note
      BvaDecisionSection.tsx            # MODIFY: TCO/lever mini-tables + sensitivity + proof
      StaticNarrativeSections.test.tsx  # MODIFY: cover new static beats
      PatientPathLauncher.test.tsx      # MODIFY: cover DC-INSIGHT + worked example
      BvaDecisionSection.test.tsx       # MODIFY: cover TCO/lever/sensitivity/proof
      StartHero.test.tsx                # MODIFY: cover P14 eyebrow header
  theme/design-system/
    recipes.ts                          # MODIFY: + kpiTile, glyphCard, miniTable, beatStrip,
                                        #   workedExampleCallout, sensitivityBars, proofChip
    index.ts                            # MODIFY: re-export new recipes
  i18n/{en,de,fr,it}.json               # MODIFY: eyebrow keys + all new beat copy
docs/
  superpowers/artifacts/2026-08-06-start-content-parity-matrix.md   # CREATE (M1-A)
  brandkit/curavias-ux-patterns.md      # MODIFY (M6): Start conformance + close P12 follow-up
```

---

## Task 0 — M0: Confirm the local verify loop (enabler)

**Files:** none (environment bring-up only).

- [ ] **Step 1: Install app deps if needed**

Run: `npm --prefix apps/hcc-app-fluent install`
Expected: completes; `node_modules` present.

- [ ] **Step 2: Start the dev server**

Run: `npm --prefix apps/hcc-app-fluent run dev`
Expected: Vite serves on `http://localhost:5173`; `/start` renders the current narrative.

- [ ] **Step 3: Baseline gates are green before any change**

Run: `npm --prefix apps/hcc-app-fluent run lint`
Run: `npm --prefix apps/hcc-app-fluent run test`
Run: `npm --prefix apps/hcc-app-fluent run test:a11y`
Expected: all pass. If any fail on `main`, record the pre-existing failure in the PR and do
not attribute it to this sprint.

- [ ] **Step 4: Capture a `/start` baseline**

Using the shared-context read-only `playwright-mcp` browser on `http://localhost:5173/start`,
capture light + dark, desktop (≥ 1280) + narrow (≈ 768) snapshots. Store as the M2–M5
"before" reference. No commit (evidence is attached to PRs, not committed).

> **Exit:** dev server serves `/start`; baseline gates green (or pre-existing failures
> recorded); baseline snapshots captured.

---

## Task 1 — M1-A: Content-parity matrix artifact

**Files:**
- Create: `docs/superpowers/artifacts/2026-08-06-start-content-parity-matrix.md`

- [ ] **Step 1: Author the matrix from the design spec §5**

Create the file with the SemVer header block (copilot-instructions §9) and a table with
columns: `# | Mockup beat | Start section | Current status (✓/~/+) | Decision (keep/add/retire) | i18n keys needed`.
Copy the 19 beats from the design spec §5 verbatim, add the decision + i18n-key columns.
Record explicitly that `cio-why-now`'s seven-decision "Today vs Curavias" table is a **kept
app extension** of beats 5–6 (not an orphan to retire), restyle-only.

- [ ] **Step 2: Lint the matrix**

Run: `npx markdownlint-cli2 "docs/superpowers/artifacts/2026-08-06-start-content-parity-matrix.md"`
Run: `python scripts/lint/check_mojibake.py docs/superpowers/artifacts/2026-08-06-start-content-parity-matrix.md`
Expected: 0 errors; no mojibake.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/artifacts/2026-08-06-start-content-parity-matrix.md
git commit -m "docs(sprint-40): add Start content-parity matrix (M1-A)"
```

> **Exit:** every mockup beat has a section mapping + keep/add/retire decision + i18n-key list.
> This matrix is the acceptance reference for M1–M5.

---

## Task 2 — M1-B: Content model (TDD)

**Files:**
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts`
- Test: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.test.ts`

The existing model uses `readonly … as const satisfies readonly T[]` arrays keyed to i18n
keys under `start.frontier.*` (see `WORK_MODES`, `PATIENT_PATH_OPERATIONAL_STOPS`). Follow
that exact pattern for the new structures.

- [ ] **Step 1: Write the failing test for the agent roster**

Add to `start-content.test.ts`:

```ts
import {
  FRONTIER_AGENTS,
  DC_INSIGHT_BEATS,
  WORKED_EXAMPLE,
  BVA_TCO_ROWS,
  BVA_VALUE_LEVERS,
  BVA_SENSITIVITY,
  BVA_PROOF_CHIPS,
} from './start-content';

describe('frontier agent roster', () => {
  it('lists the seven runtime agents plus the PO advisory agent', () => {
    const ids = FRONTIER_AGENTS.map((a) => a.id);
    expect(ids).toEqual(['ooa', 'dca', 'bmca', 'csa', 'orsa', 'sba', 'data-quality', 'po']);
  });
  it('gives every agent a glyph and an i18n caption key', () => {
    for (const a of FRONTIER_AGENTS) {
      expect(a.glyph.length).toBeGreaterThan(0);
      expect(a.captionKey).toMatch(/^start\.frontier\.hospitals\.agents\./);
    }
  });
});
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `npm --prefix apps/hcc-app-fluent run test -- start-content`
Expected: FAIL — `FRONTIER_AGENTS` (and the other imports) not exported.

- [ ] **Step 3: Implement the roster structure**

Append to `start-content.ts`:

```ts
export type FrontierAgentId =
  | 'ooa' | 'dca' | 'bmca' | 'csa' | 'orsa' | 'sba' | 'data-quality' | 'po';

export interface FrontierAgent {
  id: FrontierAgentId;
  glyph: string;                 // short label glyph, e.g. 'OOA'
  captionKey: `start.frontier.hospitals.agents.${FrontierAgentId}`;
}

export const FRONTIER_AGENTS = [
  { id: 'ooa', glyph: 'OOA', captionKey: 'start.frontier.hospitals.agents.ooa' },
  { id: 'dca', glyph: 'DCA', captionKey: 'start.frontier.hospitals.agents.dca' },
  { id: 'bmca', glyph: 'BMCA', captionKey: 'start.frontier.hospitals.agents.bmca' },
  { id: 'csa', glyph: 'CSA', captionKey: 'start.frontier.hospitals.agents.csa' },
  { id: 'orsa', glyph: 'ORSA', captionKey: 'start.frontier.hospitals.agents.orsa' },
  { id: 'sba', glyph: 'SBA', captionKey: 'start.frontier.hospitals.agents.sba' },
  { id: 'data-quality', glyph: 'DQ', captionKey: 'start.frontier.hospitals.agents.data-quality' },
  { id: 'po', glyph: 'PO', captionKey: 'start.frontier.hospitals.agents.po' },
] as const satisfies readonly FrontierAgent[];
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `npm --prefix apps/hcc-app-fluent run test -- start-content`
Expected: the roster tests PASS (the other imports still fail — implemented in Step 5).

- [ ] **Step 5: Implement the remaining structures (DC-INSIGHT, worked example, BVA tables)**

Append to `start-content.ts`:

```ts
export type DcInsightStepId =
  | 'signal' | 'understanding' | 'recommendation' | 'action' | 'coordination';

export interface DcInsightBeat {
  id: DcInsightStepId;
  labelKey: `start.frontier.patientPath.dcInsight.${DcInsightStepId}.label`;
  bodyKey: `start.frontier.patientPath.dcInsight.${DcInsightStepId}.body`;
}

export const DC_INSIGHT_BEATS = [
  { id: 'signal', labelKey: 'start.frontier.patientPath.dcInsight.signal.label', bodyKey: 'start.frontier.patientPath.dcInsight.signal.body' },
  { id: 'understanding', labelKey: 'start.frontier.patientPath.dcInsight.understanding.label', bodyKey: 'start.frontier.patientPath.dcInsight.understanding.body' },
  { id: 'recommendation', labelKey: 'start.frontier.patientPath.dcInsight.recommendation.label', bodyKey: 'start.frontier.patientPath.dcInsight.recommendation.body' },
  { id: 'action', labelKey: 'start.frontier.patientPath.dcInsight.action.label', bodyKey: 'start.frontier.patientPath.dcInsight.action.body' },
  { id: 'coordination', labelKey: 'start.frontier.patientPath.dcInsight.coordination.label', bodyKey: 'start.frontier.patientPath.dcInsight.coordination.body' },
] as const satisfies readonly DcInsightBeat[];

export interface WorkedExample {
  beforeKey: 'start.frontier.patientPath.worked.before';   // '102%'
  afterKey: 'start.frontier.patientPath.worked.after';     // '94%'
  bodyKey: 'start.frontier.patientPath.worked.body';
  chipKeys: readonly [
    'start.frontier.patientPath.worked.chips.advisory',
    'start.frontier.patientPath.worked.chips.hitl',
    'start.frontier.patientPath.worked.chips.auditable',
  ];
}

export const WORKED_EXAMPLE = {
  beforeKey: 'start.frontier.patientPath.worked.before',
  afterKey: 'start.frontier.patientPath.worked.after',
  bodyKey: 'start.frontier.patientPath.worked.body',
  chipKeys: [
    'start.frontier.patientPath.worked.chips.advisory',
    'start.frontier.patientPath.worked.chips.hitl',
    'start.frontier.patientPath.worked.chips.auditable',
  ],
} as const satisfies WorkedExample;

export interface BvaTableRow {
  labelKey: string;
  valueKey: string;   // value strings are i18n-keyed so number formatting stays localisable
}

export const BVA_TCO_ROWS = [
  { labelKey: 'start.frontier.bva.tco.rom.label', valueKey: 'start.frontier.bva.tco.rom.value' },
  { labelKey: 'start.frontier.bva.tco.oneTime.label', valueKey: 'start.frontier.bva.tco.oneTime.value' },
  { labelKey: 'start.frontier.bva.tco.run.label', valueKey: 'start.frontier.bva.tco.run.value' },
  { labelKey: 'start.frontier.bva.tco.total.label', valueKey: 'start.frontier.bva.tco.total.value' },
  { labelKey: 'start.frontier.bva.tco.gross.label', valueKey: 'start.frontier.bva.tco.gross.value' },
] as const satisfies readonly BvaTableRow[];

export const BVA_VALUE_LEVERS = [
  { labelKey: 'start.frontier.bva.levers.los.label', valueKey: 'start.frontier.bva.levers.los.value' },
  { labelKey: 'start.frontier.bva.levers.deferred.label', valueKey: 'start.frontier.bva.levers.deferred.value' },
  { labelKey: 'start.frontier.bva.levers.agency.label', valueKey: 'start.frontier.bva.levers.agency.value' },
  { labelKey: 'start.frontier.bva.levers.throughput.label', valueKey: 'start.frontier.bva.levers.throughput.value' },
] as const satisfies readonly BvaTableRow[];

export type BvaScenarioId = 'conservative' | 'base' | 'upside';

export interface BvaSensitivityBar {
  id: BvaScenarioId;
  labelKey: `start.frontier.bva.sensitivity.${BvaScenarioId}.label`;
  valueKey: `start.frontier.bva.sensitivity.${BvaScenarioId}.value`;
}

export const BVA_SENSITIVITY = [
  { id: 'conservative', labelKey: 'start.frontier.bva.sensitivity.conservative.label', valueKey: 'start.frontier.bva.sensitivity.conservative.value' },
  { id: 'base', labelKey: 'start.frontier.bva.sensitivity.base.label', valueKey: 'start.frontier.bva.sensitivity.base.value' },
  { id: 'upside', labelKey: 'start.frontier.bva.sensitivity.upside.label', valueKey: 'start.frontier.bva.sensitivity.upside.value' },
] as const satisfies readonly BvaSensitivityBar[];

export const BVA_PROOF_CHIPS = [
  'start.frontier.bva.proof.ooaLive',
  'start.frontier.bva.proof.synthetic',
  'start.frontier.bva.proof.auditable',
] as const;
```

> **Grounding note:** the value strings (`*.value` keys) must be filled in M1-D from the
> mockup's already-grounded BVA figures (the mockup renders the `bva-evidence` numbers). Do
> **not** invent new figures; copy the mockup's values verbatim into `en.json`.

- [ ] **Step 6: Extend the test for the remaining structures**

Add to `start-content.test.ts`:

```ts
describe('frontier content structures', () => {
  it('has a five-step DC-INSIGHT pattern in canonical order', () => {
    expect(DC_INSIGHT_BEATS.map((b) => b.id)).toEqual([
      'signal', 'understanding', 'recommendation', 'action', 'coordination',
    ]);
  });
  it('has a worked example with three governance chips', () => {
    expect(WORKED_EXAMPLE.chipKeys).toHaveLength(3);
  });
  it('has BVA TCO, lever, sensitivity and proof content', () => {
    expect(BVA_TCO_ROWS.length).toBeGreaterThanOrEqual(5);
    expect(BVA_VALUE_LEVERS.length).toBeGreaterThanOrEqual(3);
    expect(BVA_SENSITIVITY.map((b) => b.id)).toEqual(['conservative', 'base', 'upside']);
    expect(BVA_PROOF_CHIPS.length).toBeGreaterThanOrEqual(3);
  });
});
```

- [ ] **Step 7: Run the full content-model test**

Run: `npm --prefix apps/hcc-app-fluent run test -- start-content`
Expected: PASS.

- [ ] **Step 8: Type-check + commit**

Run: `npm --prefix apps/hcc-app-fluent run lint`
Expected: PASS.

```bash
git add apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts \
        apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.test.ts
git commit -m "feat(start): add frontier agent roster, DC-INSIGHT, worked example and BVA tables (M1-B)"
```

---

## Task 3 — M1-C: Design-system recipes

**Files:**
- Modify: `apps/hcc-app-fluent/src/theme/design-system/recipes.ts`
- Modify: `apps/hcc-app-fluent/src/theme/design-system/index.ts`

Read the existing `recipes.ts` first and follow its authoring convention (Griffel
`makeStyles` / token composition). Add recipes for each mockup device so no section writes
one-off CSS. Each recipe composes existing semantic tokens only (brand, neutral, RAG, focus)
— **no new brand colours** (design spec §9).

- [ ] **Step 1: Add the recipe hooks**

Add to `recipes.ts`, matching the file's existing export style, hooks for:
`useKpiTile` (label + figure + provenance caption), `useGlyphCard` (glyph + title + stat
lines), `useMiniTable` (compact 2–3 col table with header row + green-square row markers),
`useBeatStrip` (numbered step sequence), `useWorkedExampleCallout` (before → after + chips),
`useSensitivityBars` (horizontal bars vs the > 60 % governance target line), `useProofChip`
(reuse the trust-pill treatment). Re-export each from `index.ts`.

Structure each hook exactly like the current recipes in the file (return a `classes` object
from `makeStyles`); wire real token spacing (`tokens.spacingVertical*`, `tokens.spacingHorizontal*`),
type ramp, elevation, and `:hover`/`:focus-visible` states. Exact spacing/elevation values are
tuned in Phase 2 against the live render — start from the nearest existing recipe's values.

- [ ] **Step 2: Type-check**

Run: `npm --prefix apps/hcc-app-fluent run lint`
Expected: PASS (recipes compile; unused until sections consume them — acceptable at this step).

- [ ] **Step 3: Commit**

```bash
git add apps/hcc-app-fluent/src/theme/design-system/recipes.ts \
        apps/hcc-app-fluent/src/theme/design-system/index.ts
git commit -m "feat(design-system): add KPI-tile, glyph-card, mini-table, beat-strip, worked-example, sensitivity and proof-chip recipes (M1-C)"
```

---

## Task 4 — M1-D: i18n keys + eyebrow keying

**Files:**
- Modify: `apps/hcc-app-fluent/src/i18n/{en,de,fr,it}.json`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx`

- [ ] **Step 1: Add all new copy keys to en.json**

Add, under the existing `start.frontier.*` tree, real values for every key introduced in
Task 2 (agent captions, DC-INSIGHT labels/bodies, worked-example strings + chips, BVA
TCO/lever/sensitivity labels+values, proof chips) plus the section **eyebrow** keys:
`start.frontier.hero.eyebrow`, `start.frontier.workChart.eyebrow`,
`start.frontier.cioWhyNow.eyebrow`, `start.frontier.hospitals.eyebrow`,
`start.frontier.patientPath.eyebrow`, `start.frontier.ninetyDay.eyebrow`,
`start.frontier.bva.eyebrow`. Seed each eyebrow with the current English literal from
`SECTION_META` in `StartView.tsx` (e.g. work-chart → "The idea in one minute"). Copy BVA
figures verbatim from the mockup — no new numbers.

- [ ] **Step 2: Mirror the keys into de/fr/it with faithful translations**

Add the identical key set to `de.json`, `fr.json`, `it.json` with faithful translations of
the English baseline (voice refinement is a `product-marketing-agent` follow-up per design
spec §10). Keep numeric `*.value` strings identical across locales unless a locale formats
numbers differently.

- [ ] **Step 3: Write the failing test that every locale has the new keys**

Add a Vitest (co-locate with existing i18n tests if present, else create
`apps/hcc-app-fluent/src/i18n/i18n-parity.test.ts`):

```ts
import en from './en.json';
import de from './de.json';
import fr from './fr.json';
import it from './it.json';

function keys(obj: unknown, prefix = ''): string[] {
  if (obj && typeof obj === 'object') {
    return Object.entries(obj as Record<string, unknown>).flatMap(([k, v]) =>
      keys(v, prefix ? `${prefix}.${k}` : k),
    );
  }
  return [prefix];
}

it('all locales expose the same key set', () => {
  const base = new Set(keys(en));
  for (const [name, loc] of [['de', de], ['fr', fr], ['it', it]] as const) {
    const got = new Set(keys(loc));
    const missing = [...base].filter((k) => !got.has(k));
    expect({ locale: name, missing }).toEqual({ locale: name, missing: [] });
  }
});
```

- [ ] **Step 4: Run it**

Run: `npm --prefix apps/hcc-app-fluent run test -- i18n`
Expected: PASS (fix any missing/extra keys until all four locales match).

- [ ] **Step 5: Key the section eyebrows in `StartView.tsx`**

Replace the inline-English `SECTION_META` eyebrow literals with i18n lookups. Change the
`SECTION_META` map so `eyebrow` holds the **key**, and resolve it with `t(...)` where the
header is rendered:

```ts
const SECTION_META: Record<StartSection['id'], { eyebrowKey: string; nav: string }> = {
  hero: { eyebrowKey: 'start.frontier.hero.eyebrow', nav: 'Value' },
  'work-chart': { eyebrowKey: 'start.frontier.workChart.eyebrow', nav: 'Operating model' },
  'cio-why-now': { eyebrowKey: 'start.frontier.cioWhyNow.eyebrow', nav: 'Why now' },
  hospitals: { eyebrowKey: 'start.frontier.hospitals.eyebrow', nav: 'Hospitals' },
  'patient-path': { eyebrowKey: 'start.frontier.patientPath.eyebrow', nav: 'Care path' },
  'ninety-day': { eyebrowKey: 'start.frontier.ninetyDay.eyebrow', nav: '90-day' },
  bva: { eyebrowKey: 'start.frontier.bva.eyebrow', nav: 'BVA' },
};
```

At the `SectionHeader` render site, pass `eyebrow={meta.eyebrowKey ? t(meta.eyebrowKey) : undefined}`.
Keep the `nav` labels as-is for this task (nav-label i18n is out of scope; tracked separately).

- [ ] **Step 6: Type-check, test, commit**

Run: `npm --prefix apps/hcc-app-fluent run lint`
Run: `npm --prefix apps/hcc-app-fluent run test`
Expected: PASS.

```bash
git add apps/hcc-app-fluent/src/i18n/*.json \
        apps/hcc-app-fluent/src/workspaces/start/StartView.tsx \
        apps/hcc-app-fluent/src/i18n/i18n-parity.test.ts
git commit -m "feat(start): key section eyebrows and localise frontier beats in en/de/fr/it (M1-D)"
```

> **M1 exit / open the M1 draft PR:** `tsc`, Vitest (content + i18n), and `build` green; the
> app renders every reconciled beat (visual polish still pending). Push and open a **draft** PR
> for M1 with the parity matrix, content-model, recipes, and i18n. List FR-UX-001/006 +
> NFR-UX-004 in the PR body.

---

## Tasks 5–8 — M2–M5: Per-section visual verify loop

Each of the following section-group tasks follows the **same six-step loop** against the live
dev server (design spec §7). The loop is identical; only the target section, its file, and its
specific gap differ. Do **one section group per draft PR**.

**The loop (run for each section in the group, in nav order):**

- [ ] **A. Capture before** — light + dark, desktop + narrow, via the shared read-only
  `playwright-mcp` browser on `http://localhost:5173/start` (scroll to the section).
- [ ] **B. Compare** — the live section against its mockup beat(s) (design spec §5) and the
  atom + pattern gates (style-guide §3): 8 pt grid, type ramp, elevation, motion, hover /
  pressed / focus, empty / loading / error states, dark-mode parity, P14 eyebrow, P17 rail.
- [ ] **C. Refactor** — edit only the section component + its recipe usage to close the gap.
  Consume the Task 3 recipes; set spacing/elevation/token values now, with eyes on the render.
- [ ] **D. Verify** — Vite hot-reloads; re-snapshot the section (after).
- [ ] **E. Extend tests** — update the section's Vitest so every new beat renders and every new
  interactive device exposes the correct role/name; run `npm --prefix apps/hcc-app-fluent run test -- <section>`.
- [ ] **F. axe** — `npm --prefix apps/hcc-app-fluent run test:a11y`; fix every violation.
- [ ] **G. Commit** the section, then attach before/after evidence to the PR.

### Task 5 — M2: `hero` + `work-chart`

**Files:** `StartHero.tsx`, `StartHero.test.tsx`, `WorkChartSection.tsx`,
`StaticNarrativeSections.test.tsx`.

- [ ] Run the loop for **`hero`**. Gap: promote to a **P14 eyebrow header**; confirm the KPI
  tiles use `useKpiTile`, trust pills and the `siteCapacity` squeeze card match the mockup's
  device spec. Test: assert the eyebrow renders and the three KPI tiles expose accessible
  names.
- [ ] Run the loop for **`work-chart`**. Gap: render Humans / Agents / On-demand as a
  device-consistent triad (glyph-card or KPI-tile recipe) **and** the 4-row "principle
  mapping" mini-table (`useMiniTable`). Test: assert the triad + all four principle rows render.
- [ ] Open the **M2 draft PR** with before/after evidence for both sections. PR body lists
  FR-UX-001/002/006 + NFR-UX-001/002/003/004.

### Task 6 — M3: `cio-why-now` + `hospitals`

**Files:** `CioChallengerSection.tsx`, `HospitalsSection.tsx`, `StaticNarrativeSections.test.tsx`.

- [ ] Run the loop for **`cio-why-now`**. Gap: restyle the seven-decision "Today vs Curavias"
  table to `useMiniTable`; keep it (kept app extension per the parity matrix). Test: assert all
  seven decision rows still render after restyle.
- [ ] Run the loop for **`hospitals`**. Gap: express CuraNova / Curalp / Vialta as `useGlyphCard`
  cards **and add** the seven-agent roster strip (beat 8) driven by `FRONTIER_AGENTS`. Test:
  assert three hospital cards + eight agent glyphs render with captions.
- [ ] Open the **M3 draft PR** with evidence.

### Task 7 — M4: `patient-path`

**Files:** `PatientPathLauncher.tsx`, `PatientPathLauncher.test.tsx`.

- [ ] Run the loop for **`patient-path`**. Gaps: (1) the 5-stop journey as a `useBeatStrip`
  device; (2) **add** the DC-INSIGHT beat strip (beat 10) driven by `DC_INSIGHT_BEATS`;
  (3) **add** the 102% → 94% worked-example callout (beat 11) driven by `WORKED_EXAMPLE` using
  `useWorkedExampleCallout`. Preserve the existing launcher CTA + P17 rail handoff. Test:
  assert the five stops, the five DC-INSIGHT beats, and the before/after worked example (with
  its three governance chips) render.
- [ ] Open the **M4 draft PR** with evidence.

### Task 8 — M5: `ninety-day` + `bva`

**Files:** `NinetyDaySection.tsx`, `BvaDecisionSection.tsx`, `BvaDecisionSection.test.tsx`,
`StaticNarrativeSections.test.tsx`.

- [ ] Run the loop for **`ninety-day`**. Gap: three-phase device parity (Frame & Ground /
  Build & Prove / Operate & Scale) + surface the "already live in PROD" note (beat 13). Test:
  assert the three phases + the live-in-PROD note render.
- [ ] Run the loop for **`bva`**. Gaps: KPI tiles (`useKpiTile`) + TCO and value-lever
  mini-tables (`useMiniTable`, from `BVA_TCO_ROWS` / `BVA_VALUE_LEVERS`) + **add** the
  sensitivity bars (beat 17, `useSensitivityBars` from `BVA_SENSITIVITY`) + proof chips
  (`BVA_PROOF_CHIPS`, `useProofChip`) + the "Ask the PO Agent about the BVA" P17 rail CTA.
  Test: assert the four KPI tiles, both mini-tables, three sensitivity bars, and the proof
  chips render, and the rail CTA opens the PO rail. **Every figure must match the mockup —
  no invented numbers.**
- [ ] Open the **M5 draft PR** with evidence.

---

## Task 9 — M6: Conformance close-out

**Files:**
- Modify: `docs/brandkit/curavias-ux-patterns.md`

- [ ] **Step 1: Full-page sweep**

Run: `npm --prefix apps/hcc-app-fluent run test:a11y`
Then capture the full `/start` in light + dark, desktop + narrow. Expected: axe clean; no
dark-mode contrast regressions.

- [ ] **Step 2: Update the brandkit Start conformance table**

In `curavias-ux-patterns.md`, update the "Start narrative surface" conformance table so Start
shows full P13–P17 conformance, mark the hero as a P14 eyebrow header, and **close the P12
eyebrow follow-up note** (eyebrows are now i18n-keyed). Bump the doc SemVer header (MINOR —
additive conformance update) and update **Previous Version**.

- [ ] **Step 3: Lint the doc**

Run: `npx markdownlint-cli2 "docs/brandkit/curavias-ux-patterns.md"`
Run: `python scripts/lint/check_mojibake.py docs/brandkit/curavias-ux-patterns.md`
Expected: 0 errors; no mojibake.

- [ ] **Step 4: Final full gate + commit**

Run: `npm --prefix apps/hcc-app-fluent run lint`
Run: `npm --prefix apps/hcc-app-fluent run test`
Run: `npm --prefix apps/hcc-app-fluent run build`
Expected: all PASS.

```bash
git add docs/brandkit/curavias-ux-patterns.md
git commit -m "docs(brandkit): mark Start P13-P17 conformant and close the P12 eyebrow follow-up (M6)"
```

- [ ] **Step 5: Open the M6 draft PR** with the full-page before/after sweep. PR body lists
  FR-UX-002/006 + NFR-UX-001.

> **Sprint DoD (design spec §17):** parity matrix complete; all eight sections render their
> reconciled beats with reused recipes; hero is a P14 header; P17 handoff consistent; brandkit
> shows P13–P17 + P12 closed; eyebrows + new copy keyed in en/de/fr/it with no mojibake;
> per-section axe AA + evidence; `tsc`/Vitest/`build` green; every stream a human-merged draft
> PR; no self-merge; no deploy/delete.

---

## Self-review

**Spec coverage** — every design-spec section maps to a task: §5 parity → Task 1; §6 Phase 1
→ Tasks 2–4; §7 Phase 2 loop → Tasks 5–8; §8 gap register → the per-section gaps in Tasks 5–8;
§9 recipes → Task 3; §10 i18n → Task 4; §11 milestones M0–M6 → Tasks 0–9; §13 testing → the
test/axe steps in every task; §16 traceability → PR-body FR/NFR lists per milestone; §17 DoD →
the M6 close-out block.

**Type consistency** — identifier names are used identically across tasks: `FRONTIER_AGENTS`,
`DC_INSIGHT_BEATS`, `WORKED_EXAMPLE`, `BVA_TCO_ROWS`, `BVA_VALUE_LEVERS`, `BVA_SENSITIVITY`,
`BVA_PROOF_CHIPS` (Task 2) are the exact names consumed in Tasks 5–8; the recipe hook names
`useKpiTile` / `useGlyphCard` / `useMiniTable` / `useBeatStrip` / `useWorkedExampleCallout` /
`useSensitivityBars` / `useProofChip` (Task 3) are the exact names referenced in Tasks 5–8;
`SECTION_META.eyebrowKey` (Task 4) matches its render-site usage.

**Placeholder scan** — no "TBD"/"implement later". Where exact spacing/elevation/pixel values
can only be set against the live render, the plan says so explicitly and pins the concrete
acceptance gate (mockup beat + atom/pattern checklist + axe) instead of inventing values — a
deliberate, honest choice for an inspection-driven visual sprint, not a placeholder.
