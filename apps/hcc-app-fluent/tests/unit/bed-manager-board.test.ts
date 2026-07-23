import { describe, it, expect } from 'vitest';
import { bedManagerBoard } from '../../src/workspaces/main/boards/bed-manager/bed-manager-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';

describe('bedManagerBoard (RoleBoard contract)', () => {
  it('is backed by the bmca-agent with a write ceiling', () => {
    expect(bedManagerBoard.agent).toBe('bmca-agent');
    expect(bedManagerBoard.ceiling).toBe('write');
  });

  it('loads bed-manager data through the trusted-data layer', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.residualBeds).toBe(-3);
    expect(data.payload.bedsShort).toBe(7);
  });

  it('derives clickable insights from reallocations', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = bedManagerBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('surg-a-to-med-a');
    expect(insights[0].context).toHaveProperty('fromWard');
  });

  it('emits residual bed pressure as its handoff output', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = bedManagerBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('bmca-agent');
    expect(handoff.metrics.deltaBeds).toBe(-3);
  });

  it('starts from a bed reallocation context when no prior handoff exists', () => {
    expect(bedManagerBoard.fromHandoff(null)).toEqual({
      situation: 'Bed reallocation',
      loopBackToOoa: false,
    });
  });
});
