import { test, expect } from '@playwright/test';
import {
  forceEnglish,
  ensureAgentPanelOpen,
  askFirstSuggestedQuestion,
  captureAnswerEvidence,
} from './helpers/live-agent';

/**
 * Sprint 43 WS-5 -- IQ-layer verification across every board-bound agent
 * (bmca/dca already covered in click-to-answer.spec.ts; PO agent in
 * po-agent-baseline.spec.ts). For each board: open the agent panel, ask
 * the board's own first suggested question, and capture whether the
 * answer is grounded (real citations) or an honestly-disclosed degraded
 * state -- never a silent fabrication. Evidence (question + full answer
 * text + citation/degradation signals) is attached to the HTML report for
 * every run via `testInfo.attach`.
 */

test.beforeEach(async ({ page }) => {
  await forceEnglish(page);
});

const BOARDS: Array<{ route: string; agent: string; tab: string }> = [
  { route: '/main/occupancy', agent: 'ooa-agent', tab: 'Occupancy' },
  { route: '/main/or-steering', agent: 'orsa-agent', tab: 'OR steering' },
  { route: '/main/staffing', agent: 'sba-agent', tab: 'Staffing' },
  { route: '/main/crisis', agent: 'csa-agent', tab: 'Scenario' },
];

for (const board of BOARDS) {
  test(`${board.agent}: asks its first suggested question and gets a real, non-fabricated answer`, async ({
    page,
  }, testInfo) => {
    await page.goto(board.route);
    await expect(page.getByRole('tab', { name: board.tab, selected: true })).toBeVisible();

    const rail = await ensureAgentPanelOpen(page);
    await expect(rail).toContainText(board.agent);

    const question = await askFirstSuggestedQuestion(page);
    const evidence = await captureAnswerEvidence(page, question);

    await testInfo.attach(`${board.agent}-evidence`, {
      body: JSON.stringify(evidence, null, 2),
      contentType: 'application/json',
    });
    await page.screenshot({ path: `test-results/ws5-${board.agent}.png`, fullPage: true });

    // Never a silent fabrication: either the answer is grounded (real
    // citations) or it must honestly disclose the degraded state.
    expect(
      evidence.hasCitations || evidence.looksHonestlyDegraded,
      `Expected ${board.agent} to either cite real sources or honestly disclose missing grounding. Got:\n${evidence.answerText}`,
    ).toBe(true);
    expect(evidence.hasRefusedBadge).toBe(false);
    expect(evidence.answerText.length).toBeGreaterThan(20);
  });
}
