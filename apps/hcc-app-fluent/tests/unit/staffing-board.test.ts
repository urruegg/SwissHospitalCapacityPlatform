import { describe, it, expect } from 'vitest';
import { staffingBoard } from '../../src/workspaces/main/boards/staffing/staffing-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';

describe('staffingBoard (RoleBoard contract)', () => {
  it('is backed by the sba-agent with a write ceiling', () => {
    expect(staffingBoard.agent).toBe('sba-agent');
    expect(staffingBoard.ceiling).toBe('write');
  });

  it('loads staffing data through the trusted-data layer', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.residualBeds).toBe(0);
    expect(data.payload.bedsShort).toBe(1);
  });

  it('derives clickable insights from staff moves', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = staffingBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('rn-icu-to-meda');
    expect(insights[0].context).toHaveProperty('role');
  });

  it('emits the balanced residual bed pressure as its handoff output', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = staffingBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('sba-agent');
    expect(handoff.metrics.deltaBeds).toBe(0);
    expect(handoff.headline).toContain('balanced');
  });

  it('starts from staffing balance when no prior handoff is present', () => {
    expect(staffingBoard.fromHandoff(null)).toEqual({
      situation: 'Staffing balance',
      loopBackToOoa: false,
    });
  });
});
