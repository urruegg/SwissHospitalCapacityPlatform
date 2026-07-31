import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
});

test('Backstage feedback loop routes domain context to the PO rail', async ({ page }) => {
  await page.goto('/backstage/feedback-loop');

  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
  await expect(page.locator('[data-testid^="backstage-nav-"]')).toHaveCount(7);

  await page.getByRole('button', { name: /empower care teams/i }).click();

  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail).toBeVisible();
  await expect(rail).toContainText('product-owner-agent');
  await expect(rail).toContainText(/skills|staffing|workload/i);
  await expect(rail.getByTestId('citations')).toContainText('docs/PRD.md#fr-poa-001');
});

test('standalone route reuses the loop without app-shell chrome', async ({ page }) => {
  await page.goto('/present/feedback-loop');

  await expect(page.getByTestId('feedback-loop-presentation')).toBeVisible();
  await expect(page.getByTestId('feedback-loop-canvas')).toBeVisible();
  await expect(page.getByRole('navigation', { name: /primary/i })).toHaveCount(0);
  await expect(page.getByRole('complementary', { name: /agent/i })).toHaveCount(0);
});

test('desktop feedback loop renders visual evidence without clipping', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/backstage/feedback-loop');

  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
  await expect(page.getByTestId('feedback-loop-canvas')).toBeVisible();
  await page.screenshot({ path: 'test-results/feedback-loop-desktop.png', fullPage: true });
});

test('narrow feedback loop remains readable without horizontal scroll', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/present/feedback-loop');

  await expect(page.locator('button[data-domain-id="care-ecosystem"]')).toBeVisible();
  await expect(page.locator('button[data-domain-id="command-center"]')).toBeVisible();
  await expect(page.locator('button[data-domain-id="frontier-workforce"]')).toBeVisible();
  await expect(page.locator('button[data-domain-id="care-innovation"]')).toBeVisible();
  await expect(page.getByTestId('feedback-loop-core')).toBeVisible();

  const documentWidth = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(documentWidth.scrollWidth).toBe(documentWidth.clientWidth);
  await page.screenshot({ path: 'test-results/feedback-loop-narrow.png', fullPage: true });
});

test('feedback loop honors reduced-motion preferences', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/backstage/feedback-loop');

  await expect(page.getByTestId('feedback-loop-canvas')).toHaveAttribute('data-reduced-motion', 'true');
});
