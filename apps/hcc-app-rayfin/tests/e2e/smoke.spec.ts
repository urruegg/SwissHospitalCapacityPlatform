import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T7 — Rayfin PoC placeholder smoke test.
 *
 * Mirrors the Fluent shell smoke (apps/hcc-app-fluent/tests/e2e/smoke.spec.ts):
 * the app renders a Helvion-branded banner. The Rayfin generator was not
 * evaluable in this environment, so this asserts only that the placeholder shell
 * builds and boots (see README + ADR-0023).
 */
test('rayfin placeholder shell renders the Helvion banner', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toContainText('Helvion');
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'not evaluable in scope',
  );
});
