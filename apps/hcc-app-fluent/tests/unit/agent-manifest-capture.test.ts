import { afterEach, describe, expect, it, vi } from 'vitest';
import { invokeAgent, sendInteractionEvent } from '../../src/copilot-drawer/agent-manifest';

// Sprint 43 WS-6 — stand-in MSAL client so bearerHeader()'s default acquirer
// (src/data/iq-client.ts, lazily `import()`ed) resolves a token deterministically
// instead of hitting a real browser MSAL session.
vi.mock('../../src/auth/msal-provider', () => ({
  msalInstance: {
    getActiveAccount: vi.fn(() => ({ homeAccountId: 'test-account' })),
    getAllAccounts: vi.fn(() => [{ homeAccountId: 'test-account' }]),
    acquireTokenSilent: vi.fn().mockResolvedValue({ accessToken: 'test-token' }),
  },
}));

/**
 * Sprint 30 M2-app — the client threads a capture `interactionId` and can emit a
 * user-interaction event. In dev/CI the agent-host is unconfigured, so the mock
 * path synthesizes an `AIX-…` id (demoable control) and event emission no-ops
 * instead of calling `fetch` (advisory-only, no backend in CI).
 */
describe('agent-manifest interaction capture threading', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mock reply carries a synthesized AIX- interactionId', async () => {
    const reply = await invokeAgent('ooa-agent', 'Wie ist die Auslastung?');
    expect(reply.interactionId).toBeDefined();
    expect(reply.interactionId!).toMatch(/^AIX-[0-9a-f]+$/);
  });

  it('sendInteractionEvent no-ops (no fetch) when the agent-host is unconfigured', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    await expect(
      sendInteractionEvent('ooa-agent', 'AIX-abc', 'thumbs', 'up'),
    ).resolves.toBeUndefined();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

/**
 * Sprint 41 WS-FE — `product-owner-agent` routes to its own dedicated
 * po-agent-service (frozen `/answer` contract, docs/superpowers/specs/
 * 2026-07-25-sprint-28-po-agent-contracts.md §6) instead of the shared
 * agent-host, whenever `PO_AGENT_URL` is configured.
 */
describe('agent-manifest product-owner-agent routing (Sprint 41 WS-FE)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete (window as { __ENV__?: unknown }).__ENV__;
  });

  it('routes product-owner-agent to the PO agent service when PO_AGENT_URL is configured', async () => {
    (window as { __ENV__?: { PO_AGENT_URL?: string } }).__ENV__ = {
      PO_AGENT_URL: 'https://po.example.test',
    };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        agentLabel: 'product-owner-agent',
        contextChip: { subject: 'PO', tone: 'signal' },
        read: 'Grounded answer',
        levers: [],
        citations: ['docs/PRD.md#vision'],
        provenance: 'live',
        refused: false,
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const reply = await invokeAgent('product-owner-agent', 'What is the strategic value case?');

    expect(fetchMock).toHaveBeenCalledWith(
      'https://po.example.test/answer',
      expect.objectContaining({ method: 'POST' }),
    );
    expect(reply.answer).toBe('Grounded answer');
    expect(reply.citations).toEqual(['docs/PRD.md#vision']);
    expect(reply.refused).toBe(false);
    expect(reply.reco?.provenance).toBe('live');
    expect(reply.interactionId).toMatch(/^AIX-[0-9a-f]+$/);
  });

  it('falls back to the deterministic mock when PO_AGENT_URL is not configured', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const reply = await invokeAgent('product-owner-agent', 'Status?');

    expect(fetchMock).not.toHaveBeenCalled();
    expect(reply.reco).toBeDefined();
  });
});

/**
 * Sprint 43 WS-6 (Task 6 of the OBO self-service Fabric-grounding plan) —
 * invokeAgent forwards the OBO bearer end-to-end. The existing #424 M5 /
 * ADR-0057 `bearerHeader()` wiring in `iqAgentChat` (src/data/iq-client.ts)
 * already attaches `Authorization: Bearer <token>` whenever `AGENT_HOST_SCOPE`
 * is configured and MSAL silently acquires a token — no separate per-call
 * token-provider parameter on `invokeAgent` is needed or added.
 */
describe('agent-manifest OBO bearer forwarding (Sprint 43 WS-6)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete (window as { __ENV__?: unknown }).__ENV__;
  });

  it('forwards Authorization: Bearer <token> to the agent-host chat call when AGENT_HOST_SCOPE is configured', async () => {
    (window as { __ENV__?: { AGENT_HOST_URL?: string; AGENT_HOST_SCOPE?: string } }).__ENV__ = {
      AGENT_HOST_URL: 'https://host.example',
      AGENT_HOST_SCOPE: 'api://b7608e39-e23a-4576-8489-e092ba5f726b/access_as_user',
    };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ answer: 'ok', citations: [], refused: false, interactionId: 'AIX-1' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await invokeAgent('bmca-agent', 'a question');

    expect(fetchMock).toHaveBeenCalledWith(
      'https://host.example/agents/bmca-agent/chat',
      expect.objectContaining({ method: 'POST' }),
    );
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe('Bearer test-token');
  });

  it('forwards no Authorization header when AGENT_HOST_SCOPE is unset (byte-parity default)', async () => {
    (window as { __ENV__?: { AGENT_HOST_URL?: string } }).__ENV__ = {
      AGENT_HOST_URL: 'https://host.example',
    };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ answer: 'ok', citations: [], refused: false, interactionId: 'AIX-2' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await invokeAgent('bmca-agent', 'a question');

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBeUndefined();
  });
});
