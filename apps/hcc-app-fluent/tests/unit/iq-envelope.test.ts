import { describe, it, expect, beforeEach } from 'vitest';
import {
  loadOccupancy,
  loadDischarge,
  loadBedManager,
  loadOrSteering,
  loadStaffing,
  loadCrisis,
} from '../../src/data/roleboard/golden-source-client';
import { isGoldenSourceConfigured, isAgentHostConfigured } from '../../src/data/iq-client';
import { setPreferredSource } from '../../src/data/data-source';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

/**
 * Sprint 27 — IQ data-access evidence-envelope contract.
 *
 * Every structured board read returns `{ provenance, citations, degraded }`.
 * In test (no `VITE_GOLDEN_SOURCE_URL`) the layer serves the simulated fixtures
 * with >= 1 `hcp:*` ontology citation and `degraded: false` (unconfigured is the
 * expected demo state, not a degradation). Selecting `live` when no golden source
 * is configured fails loud (`degraded: true`).
 */
const scope: ScenarioScope = { hospital: 'aggregated', windowHours: 72, pinned: false };

beforeEach(() => setPreferredSource('simulated'));

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

  it('fails loud (degraded) when live is selected but no golden source is configured', async () => {
    setPreferredSource('live');
    const data = await loadOccupancy(scope, 'demo');
    expect(data.provenance).toBe('simulated'); // no live source available locally
    expect(data.degraded).toBe(true); // fail loud, never silent
    expect(data.citations?.some((c) => c.startsWith('hcp:'))).toBe(true);
  });
});
