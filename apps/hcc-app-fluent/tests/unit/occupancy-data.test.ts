import { describe, it, expect } from 'vitest';
import { OCCUPANCY_PINNED } from '../../src/data/roleboard/occupancy-data';

describe('OCCUPANCY_PINNED full-screen model', () => {
  it('keeps the golden-thread site totals', () => {
    expect(OCCUPANCY_PINNED.siteDeltaBeds).toBe(-16);
    expect(OCCUPANCY_PINNED.capacity.gapBeds).toBe(-16);
    expect(OCCUPANCY_PINNED.capacity.currentPct).toBe(81);
    expect(OCCUPANCY_PINNED.capacity.forecastPct).toBe(93);
  });

  it('has four wards each pointing at a reco', () => {
    const ids = OCCUPANCY_PINNED.wards.map((w) => w.id);
    expect(ids).toEqual(['med-a', 'icu', 'surg-b', 'cardio']);
    const medA = OCCUPANCY_PINNED.wards[0];
    expect(medA.nowPct).toBe(94);
    expect(medA.forecastPct).toBe(102);
    expect(medA.trend).toBe('rising');
    expect(medA.flag).toBe('over');
    expect(medA.recoId).toBe('med-a');
  });

  it('has six signal channels and four specialisation streams', () => {
    expect(OCCUPANCY_PINNED.channels).toHaveLength(6);
    expect(OCCUPANCY_PINNED.streams).toHaveLength(4);
    const emergency = OCCUPANCY_PINNED.streams[0];
    expect(emergency.recoId).toBe('med-a');
    expect(emergency.fedBy.length).toBeGreaterThan(0);
  });

  it('carries a default reco and one reco per clickable subject', () => {
    expect(OCCUPANCY_PINNED.defaultReco.contextChip.subject).toMatch(/pressure/i);
    for (const key of ['med-a', 'icu', 'surg-b', 'cardio', 'site-gap']) {
      expect(OCCUPANCY_PINNED.recoById[key]).toBeDefined();
      expect(OCCUPANCY_PINNED.recoById[key].levers.length).toBeGreaterThan(0);
      expect(OCCUPANCY_PINNED.recoById[key].provenance).toBe('simulated');
    }
    expect(OCCUPANCY_PINNED.recoById['med-a'].primaryCta?.target).toBe('dca-agent');
  });
});
