import { describe, expect, it } from 'vitest';
import { ds } from '../../src/theme/design-system';

describe('design-system tokens', () => {
  it('exposes an 8pt-derived space scale', () => {
    expect(ds.space.xs).toBe('4px');
    expect(ds.space.s).toBe('8px');
    expect(ds.space.m).toBe('12px');
    expect(ds.space.l).toBe('16px');
    expect(ds.space.xl).toBe('24px');
    expect(ds.space.xxl).toBe('32px');
  });

  it('exposes radii, elevation, motion, focus', () => {
    expect(ds.radii.card).toBeDefined();
    expect(ds.elevation.card).toBeDefined();
    expect(ds.motion.durationNormal).toBeDefined();
    expect(ds.focus.ringWidth).toBe('2px');
  });
});
