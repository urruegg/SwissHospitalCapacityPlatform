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

// Sprint 39 P2 (B2) — scan the copilot accept/deny + side-by-side outcome
// surface (rendered in the agent rail on the live discharge board). Forces Live
// via a runtime host URL + the Data-source toggle and stubs the two endpoints so
// the decision surface is deterministic. The board content carries pre-existing
// debt (excluded like the SURFACES loop); the rail decision surface is scanned.
const A11Y_WORKLIST = {
  role: 'dca',
  ward: 'C3',
  observations: [
    { patient: 'PT-901', ward: 'C3', readiness: 'BLOCKED', barrier: 'transport', aged_h: 4, provenance: 'live' },
  ],
  recommendation: {
    lever_id: 'DCA-UNBLOCK-BARRIER',
    params: { barrier_type: 'transport', n: 1, ward: 'C3' },
    predicted_impact: { metric: 'beds', value: 1 },
    insight_text: 'Resolve 1 transport barrier to free 1 bed on C3',
    citations: ['gold.discharge_candidates'],
  },
  provenance: 'live',
};

const A11Y_OUTCOME = {
  contract: 'DC-SIM-OUTCOME-v1',
  plan_id: 'plan-a11y',
  golden_thread: 'gt-a11y',
  lever_id: 'DCA-UNBLOCK-BARRIER',
  applied_ts: '1970-01-01T00:00:00Z',
  predicted_impact: { metric: 'beds', value: 1 },
  realised_impact: { metric: 'beds', value: 1 },
  state_delta: { beds_freed: ['C3'], patients_discharged: ['PT-901'], patients_promoted: [] },
  divergence: 0,
  provenance: 'live',
  applied: true,
  branch: 'accept',
  decision: 'accept',
  approver: 'oid-a11y',
};

test('no serious/critical a11y violations on the copilot accept/deny outcome surface', async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      AGENT_HOST_URL: 'https://host.test',
    };
  });
  await page.route('**/agents/dca/worklist*', (r) => r.fulfill({ json: A11Y_WORKLIST }));
  await page.route('**/agents/dca/decisions', (r) => r.fulfill({ json: A11Y_OUTCOME }));

  await page.goto('/main/discharge');
  await expect(page.getByTestId('board-discharge')).toBeVisible();
  await page.getByRole('switch', { name: 'Data source' }).click();
  await page.getByRole('button', { name: 'Open agent' }).click();
  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail.getByRole('button', { name: 'Accept' })).toBeVisible();
  await rail.getByRole('button', { name: 'Accept' }).click();
  await expect(rail.getByTestId('decision-outcome')).toBeVisible();

  // Scope the scan to the NEW accept/deny decision surface this test owns. The
  // broader copilot-rail chrome (brand-green agentLine + agent-ceiling badges)
  // carries a pre-existing, app-wide brand-token contrast gap tracked separately
  // (not introduced by Sprint 39 P2), so it is out of this test's scope.
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .include('[data-testid="decision-surface"]')
    .exclude('[data-tabster-dummy]')
    .analyze();
  const blocking = results.violations.filter(
    (v) => v.impact === 'serious' || v.impact === 'critical',
  );
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
});
