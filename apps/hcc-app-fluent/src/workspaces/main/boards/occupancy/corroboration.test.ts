import { describe, it, expect } from 'vitest';
import { corroborates } from './corroboration';

describe('web-signal corroboration (display-only, Sprint 44)', () => {
  it('flags a Trust-A signal corroborated by a Web IQ signal on same hazard + canton', () => {
    expect(
      corroborates(
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-A' },
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' },
      ),
    ).toBe(true);
  });

  it('does not corroborate across different cantons', () => {
    expect(
      corroborates(
        { hazardType: 'heat', cantons: ['BE'], trustClass: 'Trust-A' },
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' },
      ),
    ).toBe(false);
  });

  it('does not corroborate across different hazards', () => {
    expect(
      corroborates(
        { hazardType: 'flood', cantons: ['ZH'], trustClass: 'Trust-A' },
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' },
      ),
    ).toBe(false);
  });

  it('only a Trust-A signal can be corroborated by a Trust-B signal (not the reverse)', () => {
    expect(
      corroborates(
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' },
        { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-A' },
      ),
    ).toBe(false);
  });
});
