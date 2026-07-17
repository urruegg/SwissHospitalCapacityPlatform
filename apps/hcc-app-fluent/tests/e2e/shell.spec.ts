import { test, expect } from '@playwright/test';

/**
 * Sprint 20 M9.1 — five-plane shell smoke.
 *
 * Proves the routed Header/Navigation/Main/Agent/Footer shell renders, that
 * Start is the default surface, and that navigating to Main mounts a board.
 * Language is forced to EN via localStorage so the nav labels are
 * deterministic regardless of the DE default (design spec §2.1).
 */
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
});

test('five-plane shell renders and Start is the default surface', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toBeVisible();
  await expect(page.getByRole('navigation', { name: 'Primary' })).toBeVisible();
  await expect(page.getByRole('contentinfo')).toBeVisible();
  await expect(page.getByTestId('start-view')).toBeVisible();
});

test('navigating to Main renders a board', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Main' }).click();
  await expect(page.getByTestId('board-bed-manager')).toBeVisible();
});
