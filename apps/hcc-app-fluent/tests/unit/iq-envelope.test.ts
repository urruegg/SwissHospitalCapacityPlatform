import { describe, it, expect } from 'vitest';
import {
  loadOccupancy,
  loadDischarge,
  loadBedManager,
  loadOrSteering,
  loadStaffing,
  loadCrisis,
} from '../../src/data/roleboard/golden-source-client';
import { isGoldenSourceConfigured, isAgentHostConfigured } from '../../src/data/iq-client';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

/**
 * Sprint 27 — IQ data-access evidence-envelope contract.
 *
 * Every structured board read returns `{ provenance, citations, degraded }`.
 * In test (no `VITE_GOLDEN_SOURCE_URL`) the layer serves the simulated fixtures
 * with >= 1 `hcp:*` ontology citation and `degraded: false` (unconfigured is the
 * expected demo state, not a degradation).
 */
const scope: ScenarioScope = { hospital: 'aggregated', windowHours: 72, pinned: false };

describe('IQ data-access evidence envelope', () => {
  it('serves simulated fixtures with an evidence envelope when the golden source is unconfigured', async () => {
    expect(isGoldenSourceConfigured()).toBe(false);
    const data = await loadOccupancy(scope, 'demo');
    expect(data.provenance).toBe('simulated');
    expect(data.degraded).toBe(false);
    expect(data.citations?.length ?? 0).toBeGreaterThan(0);
    expect(data.citations?.some((c) => c.startsWith('hcp:'))).toBe(true);
  });

  it('every board loader carries >= 1 hcp:* ontology citation', async () => {
    const loaders = [loadOccupancy, loadDischarge, loadBedManager, loadOrSteering, loadStaffing, loadCrisis];
    for (const load of loaders) {
      const d = await load(scope, 'demo');
      expect(d.citations?.some((c) => c.startsWith('hcp:'))).toBe(true);
    }
  });

  it('agent host is unconfigured in test (deterministic mock path)', () => {
    expect(isAgentHostConfigured()).toBe(false);
  });
});
