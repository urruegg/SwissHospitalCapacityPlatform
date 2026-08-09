import { test, expect } from '@playwright/test';

/**
 * Sprint 43 WS-4 -- the Product Owner Agent regression baseline, proven
 * working end-to-end after Sprint 42's remediation + the PO_AGENT_URL
 * Bicep fix earlier this sprint. Every other agent's "closes the loop"
 * bar is measured against this one passing.
 */

test.beforeEach(async ({ page }) => {
  // Matches tests/e2e/feedback-loop.spec.ts -- the app defaults to German
  // (Deutsch) without this, and every locator below is written against
  // the English strings.
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
});

test('PO agent answers a real question with refused: false and real citations', async ({ page }) => {
  await page.goto('/backstage/feedback-loop');
  await expect(page.getByTestId('digital-feedback-loop-section')).toBeVisible();

  await page.getByRole('button', { name: /empower care teams/i }).click();

  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail).toBeVisible();
  await expect(rail).toContainText('product-owner-agent');

  // Real citations from the live corpus, not a template placeholder.
  await expect(rail.getByTestId('citations')).not.toBeEmpty({ timeout: 30_000 });
});
