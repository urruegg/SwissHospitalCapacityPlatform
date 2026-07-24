import { describe, it, expect } from 'vitest';
import { STAFFING_PINNED, sortStaffingLevers } from '../../src/data/roleboard/staffing-data';

describe('STAFFING_PINNED model', () => {
  it('keeps the golden-thread numbers: bedsShort=1, surgeBedsEnabled=1, residualBeds=0', () => {
    expect(STAFFING_PINNED.bedsShort).toBe(1);
    expect(STAFFING_PINNED.surgeBedsEnabled).toBe(1);
    expect(STAFFING_PINNED.residualBeds).toBe(0);
  });

  it('residualBeds equals surgeBedsEnabled minus bedsShort (ring closed at 0)', () => {
    expect(STAFFING_PINNED.residualBeds).toBe(
      STAFFING_PINNED.surgeBedsEnabled - STAFFING_PINNED.bedsShort,
    );
  });

  it('has moves with id, fromUnit, toUnit, role, fte, bedsEnabled, shiftGap, recoId', () => {
    expect(STAFFING_PINNED.moves.length).toBeGreaterThanOrEqual(2);
    for (const m of STAFFING_PINNED.moves) {
      expect(m.id).toBeTruthy();
      expect(m.fromUnit).toBeTruthy();
      expect(m.toUnit).toBeTruthy();
      expect(m.role).toBeTruthy();
      expect(typeof m.fte).toBe('number');
      expect(typeof m.bedsEnabled).toBe('number');
      expect(m.shiftGap).toBeTruthy();
      expect(m.recoId).toBeTruthy();
    }
  });

  it('has levers sorted by bedsEnabled descending (pre-sorted in data)', () => {
    const values = STAFFING_PINNED.levers.map((l) => l.bedsEnabled);
    expect(values.length).toBeGreaterThanOrEqual(2);
    for (let i = 1; i < values.length; i++) {
      expect(values[i - 1]).toBeGreaterThanOrEqual(values[i]);
    }
  });

  it('stable tie-break: confirm-orsa ranks before escalate-csa (both bedsEnabled=0, c < e)', () => {
    const confirmIdx = STAFFING_PINNED.levers.findIndex((l) => l.id === 'confirm-orsa');
    const escalateIdx = STAFFING_PINNED.levers.findIndex((l) => l.id === 'escalate-csa');
    expect(confirmIdx).toBeGreaterThanOrEqual(0);
    expect(escalateIdx).toBeGreaterThanOrEqual(0);
    expect(confirmIdx).toBeLessThan(escalateIdx);
  });

  it('defaultReco has non-empty levers, a csa handoff CTA, gold citations, simulated provenance', () => {
    const { defaultReco } = STAFFING_PINNED;
    expect(defaultReco.levers.length).toBeGreaterThan(0);
    expect(defaultReco.primaryCta).toBeDefined();
    expect(defaultReco.primaryCta?.kind).toBe('handoff');
    expect(defaultReco.primaryCta?.target).toBe('csa-agent');
    expect(defaultReco.citations.some((c) => c.startsWith('gold.'))).toBe(true);
    expect(defaultReco.provenance).toBe('simulated');
  });

  it('defaultReco text states the site is balanced (residual 0)', () => {
    const text = STAFFING_PINNED.defaultReco.read.toLowerCase();
    expect(text).toContain('balance');
    expect(text).toContain('0');
  });

  it('has recoById entries for all moves with non-empty levers and simulated provenance', () => {
    for (const m of STAFFING_PINNED.moves) {
      const reco = STAFFING_PINNED.recoById[m.recoId];
      expect(reco).toBeDefined();
      expect(reco.levers.length).toBeGreaterThan(0);
      expect(reco.provenance).toBe('simulated');
      expect(reco.citations.some((c) => c.startsWith('gold.'))).toBe(true);
    }
  });

  it('includes a staffing-gap recoById entry with csa-agent handoff CTA', () => {
    const gapReco = STAFFING_PINNED.recoById['staffing-gap'];
    expect(gapReco).toBeDefined();
    expect(gapReco.primaryCta?.kind).toBe('handoff');
    expect(gapReco.primaryCta?.target).toBe('csa-agent');
  });

  it('includes an orsa-coverage recoById entry acknowledging ORSA deferrals', () => {
    const coverageReco = STAFFING_PINNED.recoById['orsa-coverage'];
    expect(coverageReco).toBeDefined();
    expect(coverageReco.levers.length).toBeGreaterThan(0);
    expect(coverageReco.provenance).toBe('simulated');
  });

  it('sortStaffingLevers returns a new array sorted by bedsEnabled desc, stable tie-break by id', () => {
    const unsorted = [...STAFFING_PINNED.levers].reverse();
    const sorted = sortStaffingLevers(unsorted);
    // Does not mutate input
    expect(unsorted).not.toEqual(sorted);
    // First element has the highest bedsEnabled
    expect(sorted[0].bedsEnabled).toBeGreaterThanOrEqual(sorted[1].bedsEnabled);
    // confirm-orsa < escalate-csa (both bedsEnabled=0, c < e)
    const confirmIdx = sorted.findIndex((l) => l.id === 'confirm-orsa');
    const escalateIdx = sorted.findIndex((l) => l.id === 'escalate-csa');
    expect(confirmIdx).toBeLessThan(escalateIdx);
  });
});
