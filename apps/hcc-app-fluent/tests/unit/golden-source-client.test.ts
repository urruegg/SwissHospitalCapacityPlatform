import { describe, it, expect } from 'vitest';
import { loadOccupancy } from '../../src/data/roleboard/golden-source-client';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

const scope: ScenarioScope = { hospital: 'usz', windowHours: 72, pinned: false };

describe('golden-source-client.loadOccupancy', () => {
  it('flags synthesized data as simulated provenance', async () => {
    const data = await loadOccupancy(scope, 'user');
    expect(data.provenance).toBe('simulated');
    expect(data.payload.siteDeltaBeds).toBe(-16);
    expect(data.payload.channels[0].occupancyPct).toBe(102);
  });

  it('pins the scenario window in demo mode', async () => {
    const data = await loadOccupancy(scope, 'demo');
    expect(data.scope.pinned).toBe(true);
    expect(data.scope.windowHours).toBe(72);
  });

  it('leaves the scope unpinned in user mode', async () => {
    const data = await loadOccupancy(scope, 'user');
    expect(data.scope.pinned).toBe(false);
  });
});
