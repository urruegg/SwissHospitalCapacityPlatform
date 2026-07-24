import { describe, it, expect } from 'vitest';
import { loadSiteCapacitySummary } from '../../src/data/roleboard/golden-source-client';
import { loadOccupancy } from '../../src/data/roleboard/golden-source-client';
import { OCCUPANCY_PINNED, aggregateSiteCapacity } from '../../src/data/roleboard/occupancy-data';
import type { CapacitySummary } from '../../src/data/roleboard/occupancy-data';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

const scope: ScenarioScope = { hospital: 'usz', windowHours: 72, pinned: false };

describe('loadSiteCapacitySummary', () => {
  it('selects the ward with the highest forecastPct as peakWard', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'user');
    // OCCUPANCY_PINNED.wards: med-a forecastPct=102 (highest)
    expect(summary.peakWard).toBe('Medicine A');
    expect(summary.peakPct).toBe(102);
  });

  it('sets siteGapBeds equal to capacity.gapBeds', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'user');
    expect(summary.siteGapBeds).toBe(OCCUPANCY_PINNED.capacity.gapBeds);
    expect(summary.siteGapBeds).toBe(-16);
  });

  it('derives breachEtaHours by linear interpolation when peak ward crosses 100%', async () => {
    // Medicine A: nowPct=94, forecastPct=102, window=72
    // expected = round(72 * (100 - 94) / (102 - 94)) = round(72 * 6/8) = round(54) = 54
    const summary = await loadSiteCapacitySummary(scope, 'user');
    expect(summary.breachEtaHours).toBe(54);
  });

  it('sets provenance to simulated when no golden source URL is configured', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'user');
    expect(summary.provenance).toBe('simulated');
  });

  it('sets firstSurfacedBy to ooa-agent', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'user');
    expect(summary.firstSurfacedBy).toBe('ooa-agent');
  });

  it('includes a valid ISO-8601 asOf timestamp', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'user');
    expect(summary.asOf).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
  });

  /**
   * START/OOA source agreement: both loadSiteCapacitySummary and loadOccupancy
   * read the same golden source (OCCUPANCY_PINNED in Tier-1 mode). Verify the
   * figures match.
   */
  it('START and OOA read the same source — siteGapBeds matches capacity.gapBeds', async () => {
    const [summary, occupancy] = await Promise.all([
      loadSiteCapacitySummary(scope, 'user'),
      loadOccupancy(scope, 'user'),
    ]);
    expect(summary.siteGapBeds).toBe(occupancy.payload.capacity.gapBeds);
    expect(summary.peakPct).toBe(
      Math.max(...occupancy.payload.wards.map((w) => w.forecastPct)),
    );
  });

  it('pins the scope in demo mode', async () => {
    const summary = await loadSiteCapacitySummary(scope, 'demo');
    // provenance is still simulated (no golden source URL); just verify it resolves
    expect(summary.provenance).toBe('simulated');
    expect(summary.peakWard).toBeTruthy();
  });
});

describe('aggregateSiteCapacity — empty-wards guard (Fix 2)', () => {
  const stubCapacity: CapacitySummary = {
    currentBeds: 0, currentTotal: 10, currentPct: 0,
    forecastBeds: 0, forecastTotal: 10, forecastPct: 0,
    gapBeds: -5,
  };

  it('returns a safe fallback when wards array is empty', () => {
    const result = aggregateSiteCapacity([], stubCapacity, 72, 'live', '2026-07-23T20:00:00.000Z');
    expect(result.peakWard).toBe('—');
    expect(result.peakPct).toBe(0);
    expect(result.breachEtaHours).toBe(72);
  });

  it('still carries siteGapBeds from capacity.gapBeds on empty wards', () => {
    const result = aggregateSiteCapacity([], stubCapacity, 72, 'simulated', '2026-07-23T20:00:00.000Z');
    expect(result.siteGapBeds).toBe(-5);
  });

  it('still carries provenance and firstSurfacedBy on empty wards', () => {
    const result = aggregateSiteCapacity([], stubCapacity, 72, 'live', '2026-07-23T20:00:00.000Z');
    expect(result.provenance).toBe('live');
    expect(result.firstSurfacedBy).toBe('ooa-agent');
  });
});
