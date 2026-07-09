import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T6 — Copilot Drawer end-to-end contract (BMCA reference).
 *
 * Opens the drawer from the BedManager board, sends a canonical prompt, and
 * asserts a grounded reply with a citation footer and no PHI. With no
 * VITE_AGENT_HOST_URL configured the drawer uses the deterministic grounded
 * mock, so the wiring is demonstrable without a live agent-host.
 */
test('Ask BMCA yields a grounded, PHI-free reply with citations', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Hauptbereich' }).click();

  await page.getByRole('button', { name: 'BMCA fragen' }).click();
  const prompt = page.getByLabel('Frage an den Agenten stellen…');
  await prompt.fill('Wie ist die Auslastung auf Station B?');
  await page.getByRole('button', { name: 'Senden' }).click();

  const conversation = page.getByTestId('conversation');
  await expect(conversation).toContainText('HITL-02');
  await expect(page.getByTestId('citations').first()).toContainText('gold.');

  // No PHI identifiers surface in the reply.
  await expect(conversation).not.toContainText(/AHV|Geburtsdatum/i);
});
