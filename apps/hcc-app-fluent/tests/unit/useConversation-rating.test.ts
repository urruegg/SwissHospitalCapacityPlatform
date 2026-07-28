import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';

const { sendSpy } = vi.hoisted(() => ({ sendSpy: vi.fn().mockResolvedValue(undefined) }));
vi.mock('../../src/copilot-drawer/agent-manifest', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../src/copilot-drawer/agent-manifest')>();
  return { ...actual, sendInteractionEvent: sendSpy };
});

import { useConversation } from '../../src/copilot-drawer/useConversation';
import { resetConversations } from '../../src/copilot-drawer/conversation-store';

/**
 * Sprint 30 M2-app — the conversation hook threads the capture `interactionId`
 * onto each agent turn and exposes `rate()` to emit a thumbs user-event for the
 * exact turn (routed through `sendInteractionEvent`).
 */
describe('useConversation rating', () => {
  beforeEach(() => {
    sendSpy.mockClear();
    resetConversations();
  });
  afterEach(() => resetConversations());

  it('carries interactionId on the agent turn and rate() emits a thumbs event for it', async () => {
    const { result } = renderHook(() => useConversation('ooa-agent'));

    await act(async () => {
      await result.current.send('Wie ist die Auslastung?');
    });

    await waitFor(() => expect(result.current.turns.length).toBe(2));
    const agentTurn = result.current.turns[1];
    expect(agentTurn.role).toBe('agent');
    expect(agentTurn.interactionId).toMatch(/^AIX-[0-9a-f]+$/);

    await act(async () => {
      await result.current.rate(agentTurn.interactionId!, 'up');
    });

    expect(sendSpy).toHaveBeenCalledWith('ooa-agent', agentTurn.interactionId, 'thumbs', 'up');
  });
});
