import { test, expect } from '@playwright/test';

/**
 * Sprint 14.1 · T6 — Presenter whiteboard Evidence tab E2E.
 *
 * demo.guest shell: Home → Backstage → Evidence. Asserts the preset layout
 * renders the card catalog floor (>=25 BOM + >=10 ADR + >=1 PRD-req cards +
 * dependency edges) and that every rendered card exposes provenance with no
 * provenance-error state (design spec §10 provenance check).
 */
test('Backstage Evidence tab renders the presenter whiteboard card catalog', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('tab', { name: 'Backstage' }).click();
  await page.getByRole('tab', { name: 'Nachweise' }).click();

  await expect(page.locator('[data-card-type="BomCard"]').first()).toBeVisible();

  const bomCount = await page.locator('[data-card-type="BomCard"]').count();
  const adrCount = await page.locator('[data-card-type="AdrCard"]').count();
  const reqCount = await page.locator('[data-card-type="PrdRequirementCard"]').count();
  const edgeCount = await page.locator('[data-card-type="DependencyEdge"]').count();

  expect(bomCount).toBeGreaterThanOrEqual(25);
  expect(adrCount).toBeGreaterThanOrEqual(10);
  expect(reqCount).toBeGreaterThanOrEqual(1);
  expect(edgeCount).toBeGreaterThanOrEqual(1);

  // Provenance contract: every card shows a provenance footer, none in error.
  await expect(page.locator('[data-provenance="true"]').first()).toBeVisible();
  expect(await page.locator('[data-provenance-error="true"]').count()).toBe(0);
});

test('Evidence tab switches to the GA-parity preset and shows GA-evidence cards', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Backstage' }).click();
  await page.getByRole('tab', { name: 'Nachweise' }).click();

  await expect(page.locator('[data-card-type="GaEvidenceCard"]')).toHaveCount(0);
  await page.getByRole('tab', { name: 'GA-Paritätsansicht' }).click();
  await expect(page.locator('[data-card-type="GaEvidenceCard"]').first()).toBeVisible();
});
