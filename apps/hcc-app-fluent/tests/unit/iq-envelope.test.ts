import { afterEach, describe, expect, it, vi } from 'vitest';
import type { ContextEnvelope } from '../../src/context/context-envelope';
import {
  loadCrisis,
  loadOccupancy,
  setContextEnvelope,
} from '../../src/data/roleboard/golden-source-client';
import type { ScenarioScope } from '../../src/journey/RoleBoard';

const scope: ScenarioScope = { hospital: 'usz', windowHours: 72, pinned: false };

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

describe('IQ ContextEnvelope propagation', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    setContextEnvelope(null);
  });

  it('rejects live IQ calls when no ContextEnvelope is set', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(null);

    await expect(loadOccupancy(scope, 'user')).rejects.toThrow(/ContextEnvelope/);
  });

  it('attaches scoped ContextEnvelope headers to occupancy live calls', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(envelope);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ marker: 'occupancy' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const data = await loadOccupancy(scope, 'user');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/occupancy?'),
      expect.objectContaining({ headers: expect.objectContaining(expectedHeaders) }),
    );
    expect(data.provenance).toBe('live');
  });

  it('attaches scoped ContextEnvelope headers to crisis live calls', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://iq.example/gold');
    setContextEnvelope(envelope);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ marker: 'crisis' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const data = await loadCrisis(scope, 'user');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/crisis?'),
      expect.objectContaining({ headers: expect.objectContaining(expectedHeaders) }),
    );
    expect(data.provenance).toBe('live');
  });

  it('allows simulated IQ calls without a ContextEnvelope', async () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', '');
    setContextEnvelope(null);

    const data = await loadOccupancy(scope, 'user');

    expect(data.provenance).toBe('simulated');
  });
});
