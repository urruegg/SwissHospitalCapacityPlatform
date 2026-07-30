import { test, expect } from '@playwright/test';
import { NARROW_VIEWPORT_HEIGHT, NARROW_VIEWPORT_WIDTH } from './responsive';

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
  await expect(
    page
      .getByRole('contentinfo')
      .filter({ has: page.getByRole('button', { name: 'Refresh rate' }) }),
  ).toBeVisible();
  await expect(page.getByTestId('start-view')).toBeVisible();
});

test('navigating to Main renders a board', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Main' }).click();
  // Sprint 29 M2 — default lands on the first patient-journey board the role
  // can see (occupancy for the default Viewer), not a hard-coded bed-manager.
  await expect(page.getByTestId('board-occupancy')).toBeVisible();
});

test('keeps the shared header usable and scroll-contained on narrow Settings', async ({ page }) => {
  await page.setViewportSize({
    width: NARROW_VIEWPORT_WIDTH,
    height: NARROW_VIEWPORT_HEIGHT,
  });
  await page.goto('/settings');

  const header = page.getByRole('banner');
  await expect(header).toBeVisible();
  const layout = await header.evaluate((element) => {
    const styles = window.getComputedStyle(element);
    return {
      clientWidth: element.clientWidth,
      scrollWidth: element.scrollWidth,
      overflowX: styles.overflowX,
      documentOverflow:
        document.documentElement.scrollWidth - document.documentElement.clientWidth,
      bodyOverflow: document.body.scrollWidth - document.body.clientWidth,
    };
  });

  expect(layout.clientWidth).toBeLessThanOrEqual(NARROW_VIEWPORT_WIDTH);
  expect(layout.scrollWidth).toBeGreaterThan(layout.clientWidth);
  expect(layout.overflowX).toBe('auto');
  expect(layout.documentOverflow).toBeLessThanOrEqual(0);
  expect(layout.bodyOverflow).toBeLessThanOrEqual(0);

  await header.evaluate((element) => {
    element.scrollLeft = element.scrollWidth;
  });
  const userMenu = page.getByRole('button', { name: 'User menu' });
  await expect(userMenu).toBeInViewport();
  await userMenu.click();
  await expect(page.getByRole('menu')).toBeVisible();
});
