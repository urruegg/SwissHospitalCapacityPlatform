import { describe, it, expect } from 'vitest';
import { dischargeBoard } from '../../src/workspaces/main/boards/discharge/discharge-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';

describe('dischargeBoard (RoleBoard contract)', () => {
  it('is backed by the dca-agent with a write ceiling', () => {
    expect(dischargeBoard.agent).toBe('dca-agent');
    expect(dischargeBoard.ceiling).toBe('write');
  });

  it('loads discharge data through the trusted-data layer', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.residualBeds).toBe(-7);
    expect(data.payload.bedsNeeded).toBe(16);
  });

  it('derives clickable insights from expeditable discharge candidates', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = dischargeBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('med-a-spitex');
    expect(insights[0].context).toHaveProperty('ward');
    expect(insights[0].label).toContain(data.payload.candidates[0].ward);
  });

  it('emits the residual bed pressure as its handoff output', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = dischargeBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('dca-agent');
    expect(handoff.metrics.deltaBeds).toBe(-7);
  });

  it('starts from discharge readiness when no prior handoff is present', () => {
    expect(dischargeBoard.fromHandoff(null)).toEqual({
      situation: 'Discharge readiness',
      loopBackToOoa: false,
    });
  });
});
