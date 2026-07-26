import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  loadOccupancy,
  loadDischarge,
  loadBedManager,
  loadOrSteering,
  loadStaffing,
  loadCrisis,
  setContextEnvelope,
} from '../../src/data/roleboard/golden-source-client';
import { isGoldenSourceConfigured, isAgentHostConfigured } from '../../src/data/iq-client';
import { setPreferredSource } from '../../src/data/data-source';
import type { ContextEnvelope } from '../../src/context/context-envelope';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

/**
 * Sprint 27 / Sprint 29 — IQ data-access contract.
 *
 * The Live/Simulated toggle + evidence envelope (provenance/citations/degraded,
 * Sprint 27) layered on the ContextEnvelope OBO/RLS propagation (ADR-0052).
 * In test (no `VITE_GOLDEN_SOURCE_URL`) the layer serves the simulated fixtures
 * with >= 1 `hcp:*` ontology citation; selecting `live` without a golden source
 * fails loud (`degraded: true`). When a golden source IS configured, live calls
 * require a `ContextEnvelope` and carry it as scoped headers.
 */
const scope: ScenarioScope = { hospital: 'aggregated', windowHours: 72, pinned: false };

describe('IQ data-access evidence envelope', () => {
  beforeEach(() => setPreferredSource('simulated'));
  afterEach(() => setPreferredSource('simulated'));

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

const liveScope: ScenarioScope = { hospital: 'usz', windowHours: 72, pinned: false };

const envelope: ContextEnvelope = {
  userOid: 'oid-123',
  heldRoles: ['HCC.BedManager'],
  activeRole: 'HCC.BedManager',
  hospitalScope: 'usz',
  dataSource: 'live',
  agent: 'ooa-agent',
  windowHours: 72,
};

const expectedHeaders = {
  'X-User-Oid': 'oid-123',
  'X-Hospital-Scope': 'usz',
  'X-Active-Role': 'HCC.BedManager',
};

describe('IQ ContextEnvelope propagation (OBO/RLS)', () => {
  // Live path requires the toggle to be `live` AND a golden source configured.
  beforeEach(() => setPreferredSource('live'));
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    setContextEnvelope(null);
    setPreferredSource('simulated');
  });

  it('rejects live IQ calls when no ContextEnvelope is set', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(null);
    await expect(loadOccupancy(liveScope, 'user')).rejects.toThrow(/ContextEnvelope/);
  });

  it('attaches scoped ContextEnvelope headers to occupancy live calls', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(envelope);
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ marker: 'occupancy' }) });
    vi.stubGlobal('fetch', fetchMock);

    const data = await loadOccupancy(liveScope, 'user');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/occupancy?'),
      expect.objectContaining({ headers: expect.objectContaining(expectedHeaders) }),
    );
    expect(data.provenance).toBe('live');
  });

  it('attaches scoped ContextEnvelope headers to crisis live calls', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(envelope);
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ marker: 'crisis' }) });
    vi.stubGlobal('fetch', fetchMock);

    const data = await loadCrisis(liveScope, 'user');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/crisis?'),
      expect.objectContaining({ headers: expect.objectContaining(expectedHeaders) }),
    );
    expect(data.provenance).toBe('live');
  });

  it('allows simulated IQ calls without a ContextEnvelope', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', '');
    setContextEnvelope(null);

    const data = await loadOccupancy(liveScope, 'user');

    expect(data.provenance).toBe('simulated');
  });
});
