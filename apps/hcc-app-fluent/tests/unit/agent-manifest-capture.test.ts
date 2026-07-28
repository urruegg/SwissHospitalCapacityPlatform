import { afterEach, describe, expect, it, vi } from 'vitest';
import { invokeAgent, sendInteractionEvent } from '../../src/copilot-drawer/agent-manifest';

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
