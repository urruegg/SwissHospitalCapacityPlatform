import { test, expect } from '@playwright/test';

/**
 * Sprint 13 T6 / Sprint 20 (parity) — Copilot end-to-end contract (BMCA reference).
 *
 * The per-board overlay drawer ("BMCA fragen") was replaced by the inline-docked,
 * three-state Agent plane (`AgentPlane`). Opens the plane from the BedManager
 * board, sends a canonical prompt, and asserts a grounded reply with a citation
 * footer and no PHI. With no VITE_AGENT_HOST_URL configured the invoker uses the
 * deterministic grounded mock, so the wiring is demonstrable without a live
 * agent-host.
 */
test('Ask BMCA yields a grounded, PHI-free reply with citations', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Hauptbereich' }).click();

  // Dock the Agent plane open (collapsed 48px rail → open panel).
  await page.getByRole('button', { name: 'Agent öffnen' }).click();

  const prompt = page.getByLabel('Frage an den Agenten stellen…');
  await prompt.fill('Wie ist die Auslastung auf Station B?');
  await page.getByRole('button', { name: 'Senden' }).click();

  const conversation = page.getByTestId('conversation');
  await expect(conversation).toContainText('HITL-02');
  await expect(page.getByTestId('citations').first()).toContainText('gold.');

  // No PHI identifiers surface in the reply.
  await expect(conversation).not.toContainText(/AHV|Geburtsdatum/i);
});
