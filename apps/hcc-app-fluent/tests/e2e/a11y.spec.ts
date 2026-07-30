import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Sprint 13 T1 — accessibility scan (WCAG 2.1 AA target, design spec §8).
 * Violations at serious/critical impact block merge.
 */
test('home shell has no serious/critical accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    // Fluent UI v9 injects tabster focus-management sentinel <i> nodes
    // (data-tabster-dummy) that axe flags as focusable content; they are
    // framework-internal and not real content, so exclude them.
    .exclude('[data-tabster-dummy]')
    .analyze();
  const blocking = results.violations.filter(
    (v) => v.impact === 'serious' || v.impact === 'critical',
  );
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
});

// Sprint 20 M9.2 — extend the axe scan to each of the five shell surfaces.
//
// The new five-plane shell chrome (header, navigation, footer, agent rail) is
// asserted at WCAG 2.1 AA on every surface. On Main and Backstage the
// pre-existing Sprint 13/14 whiteboard board content (KpiCard / ScenarioCard /
// AgentPanel colour accents and the scrollable Canvas) carries its own
// accessibility debt that predates this shell redesign. That board content is
// excluded from the scan here — with its container testid — so the Sprint 20
// shell PR gates shell-chrome accessibility on all five surfaces without
// absorbing unrelated board-internal debt (tracked separately for a dedicated
// board a11y-remediation pass).
const SURFACES: { path: string; excludeBoard?: string }[] = [
  { path: '/start' },
  { path: '/main', excludeBoard: '[data-testid="board-occupancy"]' },
  { path: '/csa' },
  { path: '/backstage' },
  { path: '/settings' },
  // Sprint 27 — dev-only design-system gallery incl. the chat response
  // artefacts catalogue (A1–A14). Scanned so the artefact vocabulary stays AA.
  { path: '/brand' },
  { path: '/present/feedback-loop' },
];

for (const { path, excludeBoard } of SURFACES) {
  test(`no serious/critical a11y violations on ${path}`, async ({ page }) => {
    await page.goto(path);
    let builder = new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .exclude('[data-tabster-dummy]');
    if (excludeBoard) builder = builder.exclude(excludeBoard);
    const results = await builder.analyze();
    const blocking = results.violations.filter(
      (v) => v.impact === 'serious' || v.impact === 'critical',
    );
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
  });
}
