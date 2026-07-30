import { afterEach, describe, expect, it, vi } from 'vitest';
import { postInteractionEvent } from '../../src/data/iq-client';

/**
 * Sprint 30 M2-app — the IQ gateway posts a user-interaction event to the
 * agent-host capture endpoint (`POST /agents/{name}/interactions/{id}/events`).
 * `iq-client` is the ONLY module allowed to call `fetch` (ingress guard), so the
 * event POST lives here. Region-agnostic base URL from runtime-config.
 */
describe('postInteractionEvent', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('POSTs the event as JSON to the interactions events endpoint', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ ok: true }) });
    vi.stubGlobal('fetch', fetchMock);

    await postInteractionEvent('ooa-agent', 'AIX-abc123', { type: 'thumbs', value: 'up' });

    expect(fetchMock).toHaveBeenCalledWith(
      'https://host.example/agents/ooa-agent/interactions/AIX-abc123/events',
      expect.objectContaining({
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ type: 'thumbs', value: 'up' }),
      }),
    );
  });

  it('encodes the agent name and throws loud on a non-ok response', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 404 });
    vi.stubGlobal('fetch', fetchMock);

    await expect(
      postInteractionEvent('ooa agent', 'AIX-missing', { type: 'thumbs', value: 'down' }),
    ).rejects.toThrow(/404/);
    expect(fetchMock).toHaveBeenCalledWith(
      'https://host.example/agents/ooa%20agent/interactions/AIX-missing/events',
      expect.anything(),
    );
  });
});
