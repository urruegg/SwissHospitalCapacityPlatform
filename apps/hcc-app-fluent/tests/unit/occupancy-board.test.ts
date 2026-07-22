import { describe, it, expect } from 'vitest';
import { occupancyBoard } from '../../src/workspaces/main/boards/occupancy/occupancy-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';

describe('occupancyBoard (RoleBoard contract)', () => {
  it('is backed by the ooa-agent with a read ceiling', () => {
    expect(occupancyBoard.agent).toBe('ooa-agent');
    expect(occupancyBoard.ceiling).toBe('read');
  });

  it('loads occupancy data through the trusted-data layer', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.siteDeltaBeds).toBe(-16);
  });

  it('derives clickable insights from the loaded channels', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = occupancyBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('med-a');
    expect(insights[0].context).toHaveProperty('occupancyPct');
    expect(insights[0].label).toContain(data.payload.channels[0].label);
  });

  it('emits the site residual pressure as its handoff output', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = occupancyBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('ooa-agent');
    expect(handoff.metrics.deltaBeds).toBe(-16);
  });

  it('keeps loop-back inactive when receiving handoff on the occupancy board', () => {
    expect(occupancyBoard.fromHandoff(null)).toEqual({
      situation: '72h occupancy forecast',
      loopBackToOoa: false,
    });
  });
});
