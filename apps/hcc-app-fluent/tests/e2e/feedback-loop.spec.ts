import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
});

test('Backstage feedback loop routes domain context to the PO rail', async ({ page }) => {
  await page.goto('/backstage/story');

  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();
  await expect(page.locator('[data-testid^="backstage-nav-"]')).toHaveCount(4);

  await page.getByRole('button', { name: /empower care teams/i }).click();

  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail).toBeVisible();
  await expect(rail).toContainText('product-owner-agent');
  await expect(rail).toContainText(/skills|staffing|workload/i);
  await expect(rail.getByTestId('citations')).toContainText('docs/PRD.md#fr-poa-001');
});
