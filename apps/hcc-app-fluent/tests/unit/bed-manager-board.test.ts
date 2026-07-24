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

  it('derives clickable insights from placements and barriers', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = bedManagerBoard.insights(data);
    // Placement insights
    expect(insights.some((i) => i.context['placement'] === 'place-pt-4001')).toBe(true);
    // Barrier insights
    expect(insights.some((i) => i.context['barrier'] === 'ward-overflow')).toBe(true);
    // Gap insight
    expect(insights.some((i) => i.id === 'placement-gap')).toBe(true);
  });

  it('all insight labels are distinct — no duplicate ids', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = bedManagerBoard.insights(data);
    const ids = insights.map((i) => i.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('defaultReco has non-empty levers, a handoff CTA, and gold citations', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = bedManagerBoard.defaultReco(data);
    expect(reco.levers.length).toBeGreaterThan(0);
    expect(reco.primaryCta).toBeDefined();
    expect(reco.citations.some((c) => c.startsWith('gold.'))).toBe(true);
    expect(reco.provenance).toBe('simulated');
  });

  it('HITL move reco has requiresApproval: true on its primaryCta', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const hitlReco = data.payload.recoById['move-pt-4003-hitl'];
    expect(hitlReco).toBeDefined();
    expect(hitlReco.primaryCta?.requiresApproval).toBe(true);
  });

  it('refused reco exists with refused: true (blocked move awaiting approval)', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const refusedReco = data.payload.recoById['move-pt-4004-refused'];
    expect(refusedReco).toBeDefined();
    expect(refusedReco.refused).toBe(true);
  });

  it('recoFor resolves a placement reco for a known insight id', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = bedManagerBoard.recoFor(
      { id: 'move-pt-4001', label: 'test', context: {} },
      data,
    );
    expect(reco.levers.length).toBeGreaterThan(0);
  });

  it('recoFor falls back to defaultReco for an unknown insight id', async () => {
    const data = await bedManagerBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const fallback = bedManagerBoard.recoFor({ id: 'no-such-id', label: 'x', context: {} }, data);
    expect(fallback).toEqual(data.payload.defaultReco);
  });

  it('emits residual bed pressure -3 as its handoff output', async () => {
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
