import { type Page, type Locator, expect } from '@playwright/test';

/**
 * Sprint 43 WS-5 -- shared helpers for the live (real SIT deployment)
 * IQ-layer verification suite. One place to fix a locator/assertion once
 * it drifts, instead of six near-duplicate specs (see
 * memories/repo/playwright-live-suite-gotchas.md for why this exists).
 */

/** The app defaults to German without this -- every spec must call it. */
export async function forceEnglish(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
}

export function agentRail(page: Page): Locator {
  return page.getByRole('complementary', { name: /agent/i });
}

/** Opens the agent panel via the FAB if it isn't already open (idempotent). */
export async function ensureAgentPanelOpen(page: Page): Promise<Locator> {
  const rail = agentRail(page);
  const fab = page.getByRole('button', { name: 'Open agent' });
  if (await fab.isVisible().catch(() => false)) {
    await fab.click();
  }
  await expect(rail).toBeVisible();
  return rail;
}

/**
 * Clicks the first "Ask about" suggestion chip (only rendered pre-turn,
 * per-board locale-safe questions from `RoleBoard.askAbout`) -- avoids
 * needing to know/type each agent's exact placeholder/button text.
 */
export async function askFirstSuggestedQuestion(page: Page): Promise<string> {
  const chips = page.locator('[aria-label="Ask about"] button');
  await expect(chips.first()).toBeVisible({ timeout: 10_000 });
  const question = (await chips.first().innerText()).trim();
  await chips.first().click();
  return question;
}

export interface AnswerEvidence {
  question: string;
  answerText: string;
  hasCitations: boolean;
  hasRefusedBadge: boolean;
  /** Heuristic: text reads as an honest "I don't have grounding" disclosure. */
  looksHonestlyDegraded: boolean;
}

// Evidence-driven (not speculative): every phrase below was observed verbatim
// or near-verbatim in a real live reply from orsa/sba/dca/ooa/csa-agent during
// Sprint 43 WS-5 verification (2026-08-09), while WS-2's real Fabric grounding
// is blocked pending a Fabric Administrator action (see design doc §2.2/§7).
// Kept intentionally broad (word-boundary-safe alternations, not exact
// phrases) because a live GPT-5 reply varies its wording every call -- an
// over-narrow regex produces false "fabrication" failures on genuinely
// honest answers (e.g. "do not have access" vs "don't have access" tripped
// an earlier, narrower version of this pattern). A failure here should
// always be triaged against the attached evidence, not trusted blindly.
const DEGRADED_PATTERN =
  /no grounding|\bgrounding\b|do.?n.?t (currently )?have access|do not (currently )?have access|advisory[ (–-]|not (currently )?grounded|\bsimulated\b|\bdegraded\b|need(s)? (a |to )?grounded?|doesn.t have .*(data|snapshot)|synthetic simulation|order.of.magnitude|can.t (tell|determine|list)|session doesn.t have|before I can|confirm the|once (you|i) (confirm|have|share)|please (share|confirm|provide)|I need (to|access)/i;

/**
 * Waits for a fresh agent reply to render, then extracts the evidence
 * needed to judge grounding honesty: real citations (grounded), OR an
 * explicit disclosure that no grounding data was available (honest
 * degradation) -- either is a pass. A confident-sounding answer with
 * neither signal is a fabrication risk and should be flagged for review.
 */
export async function captureAnswerEvidence(page: Page, question: string): Promise<AnswerEvidence> {
  const conversation = page.getByTestId('conversation');
  await expect(conversation).toBeVisible({ timeout: 60_000 });
  // The conversation renders the echoed question immediately; wait for it
  // to grow past that (the real, network-bound agent reply arriving) before
  // reading -- a live GPT-5 call can take up to ~30s (confirmed via raw
  // HTTP: ooa-agent measured 22.8s for a cold-ish call).
  await expect
    .poll(async () => (await conversation.innerText()).length, { timeout: 60_000, intervals: [500, 1000, 2000] })
    .toBeGreaterThan(question.length + 20);
  const answerText = (await conversation.innerText()).trim();
  const hasCitations = await conversation.getByTestId('citations').first().isVisible().catch(() => false);
  const hasRefusedBadge = /\brefused\b/i.test(answerText);
  return {
    question,
    answerText,
    hasCitations,
    hasRefusedBadge,
    looksHonestlyDegraded: DEGRADED_PATTERN.test(answerText),
  };
}
