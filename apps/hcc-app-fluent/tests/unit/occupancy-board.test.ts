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

  it('derives clickable insights for every ward, stream, and the site gap', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const insights = occupancyBoard.insights(data);
    const ids = insights.map((i) => i.id);
    expect(ids).toContain('med-a');
    expect(ids).toContain('surg-b');
    expect(ids).toContain('cardio');
    expect(ids).toContain('site-gap');
  });

  it('exposes a proactive default reco and resolves a reco per insight', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    expect(occupancyBoard.defaultReco(data).contextChip.tone).toBe('signal');
    const medA = data.payload.wards[0];
    const reco = occupancyBoard.recoFor(
      { id: medA.recoId, label: medA.label, context: {} },
      data,
    );
    expect(reco.contextChip.subject).toBe('Medicine A');
  });

  it('falls back to the site-gap reco for an unknown insight', async () => {
    const data = await occupancyBoard.load(GOLDEN_THREAD_SCOPE, 'demo');
    const reco = occupancyBoard.recoFor({ id: 'nope', label: 'x', context: {} }, data);
    expect(reco.contextChip.subject).toBe('Site capacity');
  });

  it('exposes ask-about prompts for the rail', () => {
    expect(occupancyBoard.askAbout.length).toBeGreaterThanOrEqual(3);
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
