import { describe, it, expect } from 'vitest';
import { chipBadgeColor, impactBadgeColor, type GroundedReco } from '../../src/copilot-rail/reco';

describe('reco contract', () => {
  it('maps chip tones to Fluent Badge colors', () => {
    expect(chipBadgeColor('over')).toBe('danger');
    expect(chipBadgeColor('watch')).toBe('warning');
    expect(chipBadgeColor('ok')).toBe('success');
    expect(chipBadgeColor('blocked')).toBe('severe');
    expect(chipBadgeColor('pending')).toBe('informative');
    expect(chipBadgeColor('ranked')).toBe('brand');
    expect(chipBadgeColor('signal')).toBe('important');
  });

  it('maps impact tones to Fluent Badge colors with a subtle default', () => {
    expect(impactBadgeColor('beds')).toBe('success');
    expect(impactBadgeColor('routing')).toBe('brand');
    expect(impactBadgeColor(undefined)).toBe('subtle');
  });

  it('accepts a fully-formed reco', () => {
    const reco: GroundedReco = {
      agentLabel: 'Occupancy Copilot',
      contextChip: { subject: 'Medicine A', qualifiers: ['forecast'], status: '102%', tone: 'over' },
      read: 'Medicine A tips to 102% within 72h.',
      levers: [{ text: 'Expedite 6 discharges', impact: { label: '-6 beds', tone: 'beds' } }],
      primaryCta: { label: 'Open discharge worklist', kind: 'handoff', target: 'dca-agent' },
      projection: '102% -> 94%',
      citations: ['gold.fact_capacity_baseline'],
      provenance: 'simulated',
    };
    expect(reco.levers).toHaveLength(1);
    expect(reco.refused).toBeUndefined();
  });
});
