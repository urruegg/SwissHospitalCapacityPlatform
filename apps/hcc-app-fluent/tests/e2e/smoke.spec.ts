import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T1 — Playwright smoke test.
 * Sprint 20 M9.3 — re-pointed at the route-driven five-plane shell after the
 * AppRail/TopBar/WorkspaceRouter shell was removed.
 * Sprint 35 — Backstage restructured: opens on the Digital Feedback Loop part
 * (`/backstage/feedback-loop`) after Story/Evidence/Roles were removed.
 *
 * Anonymous demo.guest shell: land on the Curavias shell → open the Backstage
 * Digital Feedback Loop part. MSAL sign-in is exercised in a follow-up once the
 * SIT app registration is wired (design spec §8); the smoke proves the shell
 * renders and routes.
 */
test('demo.guest lands on the Curavias shell and reaches the Backstage feedback loop', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toContainText('Curavias');

  // Navigate to the Backstage Digital Feedback Loop part (route-driven `/backstage/:widget?`).
  await page.goto('/backstage/feedback-loop');
  await expect(page.getByTestId('widget-feedback-loop')).toBeVisible();

  // Feedback loop content renders (advisory, synthetic, no PHI).
  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
});

test('BedManager board renders the parity surface (worklist)', async ({ page }) => {
  // Sprint 20 (parity) — the legacy whiteboard `data-card-type` cards were
  // replaced by the bmca board surface (BoardHeader + placement worklist +
  // barriers + KPIs + eventstream). Assert the parity surface.
  // Sprint 29 M2 — the role-first-eligible default is now occupancy, so open the
  // bed-manager parity surface via its explicit route rather than the Main tab.
  await page.goto('/main/bed-manager');
  await expect(page.getByTestId('board-bed-manager')).toBeVisible();
  // Placement worklist renders as a real table (not the removed whiteboard Canvas).
  await expect(page.getByRole('table').first()).toBeVisible();
});
