import { describe, it, expect } from 'vitest';
import { crisisBoard } from '../../src/workspaces/main/boards/crisis/crisis-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';
import { certaintyToProbability } from '../../src/data/roleboard/crisis-data';

describe('crisisBoard (RoleBoard contract)', () => {
  it('is backed by the csa-agent with a deploy ceiling', () => {
    expect(crisisBoard.agent).toBe('csa-agent');
    expect(crisisBoard.ceiling).toBe('deploy');
  });

  it('loads crisis data through the trusted-data layer', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.scope.pinned).toBe(true);
    expect(data.payload.residualBeds).toBe(0);
    expect(data.payload.signals).toHaveLength(3);
    expect(data.payload.scenarios).toHaveLength(2);
  });

  it('maps Trust-A certainty from driving signals to scenario probability', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');

    for (const scenario of data.payload.scenarios) {
      const drivingSignal = data.payload.signals.find((signal) => signal.id === scenario.drivenBy[0]);
      expect(drivingSignal).toBeDefined();
      expect(scenario.probability).toBe(certaintyToProbability(drivingSignal!.certainty));
    }

    expect(data.payload.scenarios.find((s) => s.id === 'heatwave-surge')?.probability).toBe(0.8);
    expect(data.payload.scenarios.find((s) => s.id === 'resp-virus-surge')?.probability).toBe(0.5);
  });

  it('derives clickable insights from crisis scenarios', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = crisisBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('heatwave-surge');
    expect(insights[0].context).toHaveProperty('probability');
  });

  it('emits the top probability crisis scenario as its handoff output', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = crisisBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('csa-agent');
    expect(handoff.metrics.probability).toBe(0.8);
    expect(handoff.metrics.bedDayImpact).toBe(14);
    expect(handoff.headline).toContain('loop back to occupancy');
  });

  it('starts from crisis readiness and loops back to occupancy when no prior handoff is present', () => {
    expect(crisisBoard.fromHandoff(null)).toEqual({
      situation: 'Crisis readiness',
      loopBackToOoa: true,
    });
  });
});
