import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Sprint 13 T1 — accessibility scan (WCAG 2.1 AA target, design spec §8).
 * Violations at serious/critical impact block merge.
 */
test('home shell has no serious/critical accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    // Fluent UI v9 injects tabster focus-management sentinel <i> nodes
    // (data-tabster-dummy) that axe flags as focusable content; they are
    // framework-internal and not real content, so exclude them.
    .exclude('[data-tabster-dummy]')
    .analyze();
  const blocking = results.violations.filter(
    (v) => v.impact === 'serious' || v.impact === 'critical',
  );
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
});
