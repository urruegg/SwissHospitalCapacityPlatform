import { describe, it, expect } from 'vitest';
import { OR_STEERING_PINNED } from '../../src/data/roleboard/or-steering-data';

describe('OR_STEERING_PINNED model', () => {
  it('keeps the golden-thread numbers: bedsShort=3, casesDeferred=2, bedsFreed=2, residualBeds=-1', () => {
    expect(OR_STEERING_PINNED.bedsShort).toBe(3);
    expect(OR_STEERING_PINNED.casesDeferred).toBe(2);
    expect(OR_STEERING_PINNED.bedsFreed).toBe(2);
    expect(OR_STEERING_PINNED.residualBeds).toBe(-1);
  });

  it('has cases with specialty, slot, bedsImpact, deferable, bedsProtected, recoId', () => {
    expect(OR_STEERING_PINNED.cases.length).toBeGreaterThanOrEqual(2);
    for (const c of OR_STEERING_PINNED.cases) {
      expect(c.specialty).toBeTruthy();
      expect(c.slot).toBeTruthy();
      expect(typeof c.bedsImpact).toBe('number');
      expect(typeof c.deferable).toBe('boolean');
      expect(typeof c.bedsProtected).toBe('number');
      expect(c.recoId).toBeTruthy();
    }
  });

  it('includes at least one deferable and one non-deferable case', () => {
    const flags = OR_STEERING_PINNED.cases.map((c) => c.deferable);
    expect(flags).toContain(true);
    expect(flags).toContain(false);
  });

  it('has levers sorted by bedsProtected descending (pre-sorted in data)', () => {
    const values = OR_STEERING_PINNED.levers.map((l) => l.bedsProtected);
    expect(values.length).toBeGreaterThanOrEqual(2);
    for (let i = 1; i < values.length; i++) {
      expect(values[i - 1]).toBeGreaterThanOrEqual(values[i]);
    }
  });

  it('is pre-sorted with a stable id tie-break within equal bedsProtected (mockup rank 1..5)', () => {
    const ids = OR_STEERING_PINNED.levers.map((l) => l.id);
    expect(ids).toEqual(['defer-ortho', 'reslot-thu', 'defer-general', 'redirect-urology', 'proceed-oncology']);
  });

  it('has a defaultReco with non-empty levers, a handoff CTA to sba-agent, gold citations, simulated provenance', () => {
    const { defaultReco } = OR_STEERING_PINNED;
    expect(defaultReco.levers.length).toBeGreaterThan(0);
    expect(defaultReco.primaryCta).toBeDefined();
    expect(defaultReco.primaryCta?.kind).toBe('handoff');
    expect(defaultReco.primaryCta?.target).toBe('sba-agent');
    expect(defaultReco.citations).toContain('gold.or_schedule');
    expect(defaultReco.provenance).toBe('simulated');
  });

  it('has recoById entries for all deferable cases with non-empty levers and simulated provenance', () => {
    const deferable = OR_STEERING_PINNED.cases.filter((c) => c.deferable);
    expect(deferable.length).toBeGreaterThan(0);
    for (const c of deferable) {
      const reco = OR_STEERING_PINNED.recoById[c.recoId];
      expect(reco).toBeDefined();
      expect(reco.levers.length).toBeGreaterThan(0);
      expect(reco.provenance).toBe('simulated');
      expect(reco.citations.some((ci) => ci.startsWith('gold.'))).toBe(true);
    }
  });

  it('residualBeds equals bedsFreed minus bedsShort', () => {
    const { bedsFreed, bedsShort, residualBeds } = OR_STEERING_PINNED;
    expect(residualBeds).toBe(bedsFreed - bedsShort);
  });

  it('casesDeferred matches the count of deferable cases in the list', () => {
    const deferableCount = OR_STEERING_PINNED.cases.filter((c) => c.deferable).length;
    expect(OR_STEERING_PINNED.casesDeferred).toBe(deferableCount);
  });
});
