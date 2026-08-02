import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { ContextEnvelope } from '../../context/context-envelope';
import type { ScenarioScope } from '../../journey/RoleBoard';
import { setPreferredSource } from '../data-source';
import { loadOccupancy, setContextEnvelope } from './golden-source-client';

/**
 * Sprint A (NFR-AUTH-002) — a live golden read must fail loud but never hang.
 *
 * The anonymous Demo Guest carries an empty oid, so the agent-host `/golden/*`
 * returns 401. Boards render a loading state until their data promise resolves,
 * so an uncaught throw in the loader would stall them on "Wird geladen..."
 * forever. The loader must instead resolve with the fixture flagged
 * `degraded: true` (surfaced by `GroundingNotice`) — fail loud, never hang.
 */
describe('live golden read degrades instead of hanging (Sprint A, NFR-AUTH-002)', () => {
  const guestEnvelope: ContextEnvelope = {
    userOid: '',
    heldRoles: ['HCC.Viewer'],
    activeRole: 'HCC.Viewer',
    hospitalScope: 'aggregated',
    dataSource: 'live',
    agent: null,
    windowHours: 72,
  };
  const scope: ScenarioScope = { hospital: 'aggregated', windowHours: 72, pinned: false };

  beforeEach(() => {
    (window as unknown as { __ENV__: { GOLDEN_SOURCE_URL: string } }).__ENV__ = {
      GOLDEN_SOURCE_URL: 'https://agent-host.example/golden',
    };
    setPreferredSource('live');
    setContextEnvelope(guestEnvelope);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    setContextEnvelope(null);
    setPreferredSource('simulated');
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('returns the fixture flagged degraded (does not throw) on a 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 401 }));
    const data = await loadOccupancy(scope, 'user');
    expect(data.degraded).toBe(true);
    expect(data.provenance).toBe('simulated');
    expect(data.payload).toBeTruthy();
  });

  it('returns the fixture flagged degraded (does not throw) when the fetch rejects', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('network down'));
    const data = await loadOccupancy(scope, 'user');
    expect(data.degraded).toBe(true);
    expect(data.provenance).toBe('simulated');
    expect(data.payload).toBeTruthy();
  });
});
