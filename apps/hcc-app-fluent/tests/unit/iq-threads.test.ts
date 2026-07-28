import { afterEach, describe, expect, it, vi } from 'vitest';
import { iqMintThread, iqAgentChat } from '../../src/data/iq-client';
import type { ContextEnvelope } from '../../src/context/context-envelope';

/**
 * #424 M3 — the IQ gateway is the only permitted fetch site, so the live thread
 * mint (`POST /threads`) and thread-scoped chat (`threadId` + OBO/RLS identity
 * headers) live here. These assert the wire contract the agent-host expects.
 */
const env: ContextEnvelope = {
  userOid: 'oid-123',
  heldRoles: ['HCC.BedManager'],
  activeRole: 'HCC.BedManager',
  hospitalScope: 'usz',
  dataSource: 'live',
  agent: 'bmca-agent',
  windowHours: 72,
};

const identity = {
  'X-User-Oid': 'oid-123',
  'X-Hospital-Scope': 'usz',
  'X-Active-Role': 'HCC.BedManager',
};

describe('iqMintThread', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('POSTs to /agents/{name}/threads with scoped identity headers', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ threadId: 'thr-abc', provenance: 'native' }) });
    vi.stubGlobal('fetch', fetchMock);

    const mint = await iqMintThread('bmca-agent', env);

    expect(mint).toEqual({ threadId: 'thr-abc', provenance: 'native' });
    expect(fetchMock).toHaveBeenCalledWith(
      'https://host.example/agents/bmca-agent/threads',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining(identity),
      }),
    );
  });

  it('throws loud on a non-ok mint response', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 401 }));
    await expect(iqMintThread('bmca-agent', env)).rejects.toThrow(/thread mint failed: 401/);
  });
});

describe('iqAgentChat thread + identity threading', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('sends threadId in the body and identity headers when opts are supplied', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ answer: 'ok' }) });
    vi.stubGlobal('fetch', fetchMock);

    await iqAgentChat('bmca-agent', 'Frage', { threadId: 'thr-abc', env });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers).toEqual(expect.objectContaining({ 'content-type': 'application/json', ...identity }));
    expect(JSON.parse(init.body)).toEqual({ prompt: 'Frage', threadId: 'thr-abc' });
  });

  it('omits threadId and identity headers when no opts are supplied (back-compat)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ answer: 'ok' }) });
    vi.stubGlobal('fetch', fetchMock);

    await iqAgentChat('bmca-agent', 'Frage');

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers).toEqual({ 'content-type': 'application/json' });
    expect(JSON.parse(init.body)).toEqual({ prompt: 'Frage' });
  });
});
