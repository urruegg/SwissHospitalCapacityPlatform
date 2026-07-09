import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T1 — Playwright smoke test.
 *
 * Anonymous demo.guest shell: land on Home → open Backstage → Roles tab.
 * MSAL sign-in is exercised in a follow-up once the SIT app registration is
 * wired (design spec §8); the smoke proves the shell renders and routes.
 */
test('demo.guest lands on Home and reaches the Backstage Roles tab', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toContainText('Helvion');

  // Navigate to Backstage via the app rail.
  await page.getByRole('tab', { name: 'Backstage' }).click();
  await expect(page.getByRole('main')).toHaveAttribute('data-workspace', 'backstage');

  // Roles tab content renders (read-only Entra app roles).
  await expect(page.getByRole('table')).toBeVisible();
});

test('BedManager whiteboard renders all 6 card types', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Hauptbereich' }).click();
  for (const type of [
    'PowerBITile',
    'AgentPanel',
    'KpiCard',
    'LiveStreamCard',
    'ResponsibleCard',
    'ScenarioCard',
  ]) {
    await expect(page.locator(`[data-card-type="${type}"]`).first()).toBeVisible();
  }
});
