import { describe, it, expect, vi, beforeEach } from 'vitest';
import { buildInsightPrompt, routeInsight } from '../../src/copilot-rail/InsightRouter';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import type { ContextInsight } from '../../src/journey/RoleBoard';

vi.mock('../../src/copilot-drawer/agent-manifest', () => ({
  invokeInsight: vi.fn().mockResolvedValue({ answer: 'ok', citations: [], refused: false }),
}));

const insight: ContextInsight = {
  id: 'med-a',
  label: 'Medicine A rising',
  context: { channel: 'med-a', occupancyPct: 102 },
};

describe('InsightRouter', () => {
  beforeEach(() => vi.clearAllMocks());

  it('builds a context-grounded prompt with no fabricated recommendation text', () => {
    const prompt = buildInsightPrompt(insight);
    expect(prompt).toContain('med-a');
    expect(prompt).toContain('102');
    expect(prompt).not.toContain('shift');
    expect(prompt).not.toContain('Betten');
  });

  it('opens the rail with the insight and invokes the role agent with the insight context', async () => {
    const openWithContext = vi.fn();
    await routeInsight(insight, { agent: 'ooa-agent', openWithContext });
    expect(openWithContext).toHaveBeenCalledWith(insight);
    expect(invokeInsight).toHaveBeenCalledWith('ooa-agent', insight.context);
  });
});
