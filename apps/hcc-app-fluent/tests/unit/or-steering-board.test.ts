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

  it('starts with loopBackToOoa: true when no prior handoff is present (ORSA loops back to OOA)', () => {
    expect(orSteeringBoard.fromHandoff(null)).toEqual({
      situation: 'OR steering',
      loopBackToOoa: true,
    });
  });

  it('all insight labels are distinct — no duplicate specialty text', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = orSteeringBoard.insights(data);
    const labels = insights.map((i) => i.label);
    const uniqueLabels = new Set(labels);
    expect(uniqueLabels.size).toBe(labels.length);
  });

  it('defaultReco has non-empty levers and a CTA', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = orSteeringBoard.defaultReco(data);
    expect(reco.levers.length).toBeGreaterThan(0);
    expect(reco.primaryCta).toBeDefined();
    expect(reco.citations.length).toBeGreaterThan(0);
    expect(reco.provenance).toBe('simulated');
  });

  it('recoFor resolves a reco from the payload for a known insight id', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = orSteeringBoard.recoFor(
      { id: 'ortho-knee-tue', label: 'test', context: {} },
      data,
    );
    expect(reco.levers.length).toBeGreaterThan(0);
  });

  it('recoFor falls back to defaultReco for an unknown insight id', async () => {
    const data = await orSteeringBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const fallback = orSteeringBoard.recoFor({ id: 'no-such-id', label: 'x', context: {} }, data);
    expect(fallback).toEqual(data.payload.defaultReco);
  });
});
