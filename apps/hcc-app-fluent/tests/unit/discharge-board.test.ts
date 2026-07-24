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

  it('all insight labels are distinct — no duplicate ward/candidate text', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = dischargeBoard.insights(data);
    const labels = insights.map((i) => i.label);
    const uniqueLabels = new Set(labels);
    expect(uniqueLabels.size).toBe(labels.length);
  });

  it('defaultReco has non-empty levers and a CTA', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = dischargeBoard.defaultReco(data);
    expect(reco.levers.length).toBeGreaterThan(0);
    expect(reco.primaryCta).toBeDefined();
    expect(reco.citations.length).toBeGreaterThan(0);
    expect(reco.provenance).toBe('simulated');
  });

  it('recoFor resolves a reco from the payload for a known insight id', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = dischargeBoard.recoFor(
      { id: 'med-a-spitex', label: 'test', context: {} },
      data,
    );
    expect(reco.levers.length).toBeGreaterThan(0);
  });

  it('recoFor falls back to defaultReco for an unknown insight id', async () => {
    const data = await dischargeBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const fallback = dischargeBoard.recoFor({ id: 'no-such-id', label: 'x', context: {} }, data);
    expect(fallback).toEqual(data.payload.defaultReco);
  });
});
