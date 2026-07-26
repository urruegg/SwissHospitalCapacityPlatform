import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T1 — Playwright smoke test.
 * Sprint 20 M9.3 — re-pointed at the route-driven five-plane shell after the
 * AppRail/TopBar/WorkspaceRouter shell was removed. The Backstage roles widget
 * is reached directly via `/backstage/roles`.
 *
 * Anonymous demo.guest shell: land on the Curavias shell → open the Backstage
 * Roles widget. MSAL sign-in is exercised in a follow-up once the SIT app
 * registration is wired (design spec §8); the smoke proves the shell renders
 * and routes.
 */
test('demo.guest lands on the Curavias shell and reaches the Backstage roles widget', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toContainText('Curavias');

  // Navigate to the Backstage roles widget (route-driven `/backstage/:widget?`).
  await page.goto('/backstage/roles');
  await expect(page.getByTestId('widget-roles')).toBeVisible();

  // Roles widget content renders (read-only Entra app roles).
  await expect(page.getByRole('table')).toBeVisible();
});

test('BedManager board renders the parity surface (worklist)', async ({ page }) => {
  // Sprint 20 (parity) — the legacy whiteboard `data-card-type` cards were
  // replaced by the bmca board surface (BoardHeader + placement worklist +
  // barriers + KPIs + eventstream). Assert the parity surface.
  await page.goto('/');
  await page.getByRole('tab', { name: 'Hauptbereich' }).click();
  await expect(page.getByTestId('board-bed-manager')).toBeVisible();
  // Placement worklist renders as a real table (not the removed whiteboard Canvas).
  await expect(page.getByRole('table').first()).toBeVisible();
});
