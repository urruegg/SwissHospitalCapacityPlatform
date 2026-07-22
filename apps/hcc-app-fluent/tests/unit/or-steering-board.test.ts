import { describe, it, expect } from 'vitest';
import { orSteeringBoard } from '../../src/workspaces/main/boards/or-steering/or-steering-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';

describe('orSteeringBoard (RoleBoard contract)', () => {
  it('is backed by the orsa-agent with a write ceiling', () => {
    expect(orSteeringBoard.agent).toBe('orsa-agent');
    expect(orSteeringBoard.ceiling).toBe('write');
  });

  it('loads OR steering data through the trusted-data layer', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.residualBeds).toBe(-1);
    expect(data.payload.bedsShort).toBe(3);
  });

  it('derives clickable insights from deferable OR cases', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = orSteeringBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('ortho-knee-tue');
    expect(insights[0].context).toHaveProperty('specialty');
    expect(insights[0].label).toContain(data.payload.cases[0].specialty);
  });

  it('emits the residual bed pressure as its handoff output', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = orSteeringBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('orsa-agent');
    expect(handoff.metrics.deltaBeds).toBe(-1);
  });

  it('starts from OR steering when no prior handoff is present', () => {
    expect(orSteeringBoard.fromHandoff(null)).toEqual({
      situation: 'OR steering',
      loopBackToOoa: false,
    });
  });
});
