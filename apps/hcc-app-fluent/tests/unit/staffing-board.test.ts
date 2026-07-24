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

  it('all insight ids are distinct — no duplicates from dedup filter', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = staffingBoard.insights(data);
    const ids = insights.map((i) => i.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('emits the balanced residual bed pressure as its handoff output', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const handoff = staffingBoard.toHandoff(data);
    expect(handoff.fromAgent).toBe('sba-agent');
    expect(handoff.metrics.deltaBeds).toBe(0);
    expect(handoff.headline).toContain('balanced');
  });

  it('starts with loopBackToOoa: true when no prior handoff is present (SBA closes the ring)', () => {
    expect(staffingBoard.fromHandoff(null)).toEqual({
      situation: 'Staffing balance',
      loopBackToOoa: true,
    });
  });

  it('defaultReco has non-empty levers and a CTA', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = staffingBoard.defaultReco(data);
    expect(reco.levers.length).toBeGreaterThan(0);
    expect(reco.primaryCta).toBeDefined();
    expect(reco.citations.length).toBeGreaterThan(0);
    expect(reco.provenance).toBe('simulated');
  });

  it('recoFor resolves a reco from the payload for a known insight id', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = staffingBoard.recoFor(
      { id: 'rn-icu-to-meda', label: 'test', context: {} },
      data,
    );
    expect(reco.levers.length).toBeGreaterThan(0);
  });

  it('recoFor falls back to defaultReco for an unknown insight id', async () => {
    const data = await staffingBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const fallback = staffingBoard.recoFor({ id: 'no-such-id', label: 'x', context: {} }, data);
    expect(fallback).toEqual(data.payload.defaultReco);
  });
});
