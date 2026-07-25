import { describe, it, expect } from 'vitest';
import { crisisBoard } from '../../src/workspaces/main/boards/crisis/crisis-board';
import { GOLDEN_THREAD_SCOPE } from '../../src/journey/golden-thread';
import { certaintyToProbability, CERTAINTY_TO_PROBABILITY } from '../../src/data/roleboard/crisis-data';

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
    expect(data.payload.signals.length).toBeGreaterThanOrEqual(4);
    expect(data.payload.scenarios.length).toBeGreaterThanOrEqual(2);
  });

  it('maps Trust-A Certainty to integer probability (68/31/6)', () => {
    expect(CERTAINTY_TO_PROBABILITY.Likely).toBe(68);
    expect(CERTAINTY_TO_PROBABILITY.Possible).toBe(31);
    expect(CERTAINTY_TO_PROBABILITY.Unlikely).toBe(6);
    expect(certaintyToProbability('Likely')).toBe(68);
    expect(certaintyToProbability('Possible')).toBe(31);
    expect(certaintyToProbability('Unlikely')).toBe(6);
  });

  it('derives clickable insights only from non-filtered crisis scenarios', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = crisisBoard.insights(data);
    expect(insights.map((i) => i.id)).toContain('heatwave-surge');
    expect(insights[0].context).toHaveProperty('probability');
    expect(insights[0].context).toHaveProperty('bedImpact');
  });

  it('filtered signals do NOT produce armed insights', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const filteredSignalIds = new Set(
      data.payload.signals.filter((s) => s.filtered).map((s) => s.id),
    );
    const insights = crisisBoard.insights(data);
    for (const insight of insights) {
      const scenario = data.payload.scenarios.find((s) => s.id === insight.id);
      if (scenario?.triggerSignal) {
        expect(filteredSignalIds.has(scenario.triggerSignal)).toBe(false);
      }
    }
  });

  it('exclusion filter: a scenario whose triggerSignal is filtered is absent from insights', async () => {
    // Build a synthetic payload that adds a scenario wired to the filtered signal
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const syntheticPayload = {
      ...data.payload,
      scenarios: [
        ...data.payload.scenarios,
        {
          id: 'alertswiss-triggered',
          name: 'Alertswiss-triggered synthetic scenario',
          bedImpact: 3,
          isSpof: false,
          probability: 0,
          triggerSignal: 'alertswiss-heat-test', // this signal is filtered=true
        },
      ],
    };
    const syntheticData = { ...data, payload: syntheticPayload };
    const insights = crisisBoard.insights(syntheticData);
    const insightIds = insights.map((i) => i.id);
    // The synthetic scenario must be excluded because its triggerSignal is filtered
    expect(insightIds).not.toContain('alertswiss-triggered');
    // Non-filtered scenarios must still appear
    expect(insightIds).toContain('heatwave-surge');
    expect(insightIds).toContain('resp-virus-surge');
  });

  it('emits the top probability crisis scenario as its handoff output', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = crisisBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('csa-agent');
    expect(handoff.metrics.probability).toBe(68);
    expect(handoff.metrics.bedImpact).toBe(14);
    expect(handoff.headline).toContain('loop back to occupancy');
  });

  it('starts from crisis readiness and loops back to occupancy when no prior handoff is present', () => {
    expect(crisisBoard.fromHandoff(null)).toEqual({
      situation: 'Crisis readiness',
      loopBackToOoa: true,
    });
  });

  it('defaultReco delegates to payload.defaultReco', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = crisisBoard.defaultReco(data);
    expect(reco).toBe(data.payload.defaultReco);
    expect(reco.provenance).toBe('simulated');
  });

  it('recoFor resolves from recoById for a known insight id', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = crisisBoard.recoFor(
      { id: 'heatwave-surge', label: 'test', context: {} },
      data,
    );
    expect(reco).toBe(data.payload.recoById['heatwave-surge']);
    expect(reco.primaryCta?.requiresApproval).toBe(true);
  });

  it('recoFor falls back to defaultReco for an unknown insight id', async () => {
    const data = await crisisBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const fallback = crisisBoard.recoFor({ id: 'no-such-id', label: 'x', context: {} }, data);
    expect(fallback).toBe(data.payload.defaultReco);
  });
});
