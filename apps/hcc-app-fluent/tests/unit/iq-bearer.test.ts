import { afterEach, describe, expect, it, vi } from 'vitest';
import { bearerHeader } from '../../src/data/iq-client';

/**
 * #424 M5 — the IQ gateway attaches an MSAL bearer to identity-aware calls so the
 * agent-host can perform the on-behalf-of (OBO) exchange. Deny-by-default posture:
 * no scope configured (SIT default) → no bearer (byte-parity with M4); scope
 * configured but token unobtainable → no bearer (the server denies loudly when
 * OBO is on). Never a silent wide read.
 */
describe('bearerHeader', () => {
  afterEach(() => {
    delete (window as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('returns no header when no agent-host scope is configured (parity with M4)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_SCOPE', '');
    const acquire = vi.fn();
    await expect(bearerHeader(acquire)).resolves.toEqual({});
    expect(acquire).not.toHaveBeenCalled();
  });

  it('attaches Authorization: Bearer when a scope is configured and a token is acquired', async () => {
    vi.stubEnv('VITE_AGENT_HOST_SCOPE', 'api://host/.default');
    const acquire = vi.fn().mockResolvedValue('tok-abc');
    await expect(bearerHeader(acquire)).resolves.toEqual({ Authorization: 'Bearer tok-abc' });
    expect(acquire).toHaveBeenCalledWith('api://host/.default');
  });

  it('returns no header when the scope is configured but no token is available', async () => {
    vi.stubEnv('VITE_AGENT_HOST_SCOPE', 'api://host/.default');
    const acquire = vi.fn().mockResolvedValue(null);
    await expect(bearerHeader(acquire)).resolves.toEqual({});
  });
});

describe('bearerHeader wired into identity-aware calls', () => {
  afterEach(() => {
    delete (window as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('iqMintThread attaches no Authorization header when scope is unset (SIT default)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    vi.stubEnv('VITE_AGENT_HOST_SCOPE', '');
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ threadId: 't', provenance: 'native' }) });
    vi.stubGlobal('fetch', fetchMock);

    const { iqMintThread } = await import('../../src/data/iq-client');
    await iqMintThread('bmca-agent', {
      userOid: 'oid-1',
      heldRoles: ['HCC.Viewer'],
      activeRole: 'HCC.Viewer',
      hospitalScope: 'usz',
      dataSource: 'live',
      agent: 'bmca-agent',
      windowHours: 72,
    });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers).not.toHaveProperty('Authorization');
  });
});
