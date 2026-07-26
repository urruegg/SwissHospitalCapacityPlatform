import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useConversation } from '../../src/copilot-drawer/useConversation';
import {
  conversationStore,
  conversationKey,
  resetConversations,
} from '../../src/copilot-drawer/conversation-store';

beforeEach(() => {
  vi.restoreAllMocks();
  resetConversations();
});

describe('useConversation (per-(user x agent) scoping)', () => {
  it('keeps each agent thread isolated when the agent prop switches', async () => {
    const { result, rerender } = renderHook(({ agent }) => useConversation(agent), {
      initialProps: { agent: 'bmca-agent' },
    });

    await act(async () => {
      await result.current.send('Wie ist die Auslastung auf Station B?');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));

    // Switch to a different agent in the SAME hook instance (the bleed scenario).
    rerender({ agent: 'ooa-agent' });
    expect(result.current.turns.length).toBe(0);

    // Switching back shows the bed-manager thread again — nothing leaked.
    rerender({ agent: 'bmca-agent' });
    expect(result.current.turns.length).toBe(2);
    expect(result.current.turns[0].role).toBe('user');
  });

  it('does not leak turns across two separate hook instances', async () => {
    const bmca = renderHook(() => useConversation('bmca-agent'));
    const ooa = renderHook(() => useConversation('ooa-agent'));

    await act(async () => {
      await bmca.result.current.send('Frage an BMCA');
    });
    await waitFor(() => expect(bmca.result.current.turns.length).toBe(2));

    // The other agent's thread is untouched.
    expect(ooa.result.current.turns.length).toBe(0);
  });

  it('resets every thread on sign-out', async () => {
    const { result } = renderHook(() => useConversation('bmca-agent'));
    await act(async () => {
      await result.current.send('Frage');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));

    act(() => resetConversations());
    expect(result.current.turns.length).toBe(0);
  });

  it('scopes the store key by user when an oid is supplied (M4-ready)', () => {
    expect(conversationKey('bmca-agent')).toBe('bmca-agent');
    expect(conversationKey('bmca-agent', 'oid-1')).toBe('oid-1::bmca-agent');
    expect(conversationKey('bmca-agent', 'oid-1')).not.toBe(conversationKey('bmca-agent', 'oid-2'));
  });

  it('ignores empty prompts', async () => {
    const { result } = renderHook(() => useConversation('bmca-agent'));
    await act(async () => {
      await result.current.send('   ');
    });
    expect(result.current.turns.length).toBe(0);
  });

  it('starts with an empty, non-busy slice', () => {
    expect(conversationStore.getSlice('unseen-agent')).toEqual({ turns: [], busy: false });
  });
});
