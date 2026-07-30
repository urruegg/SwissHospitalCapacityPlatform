import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useConversation } from '../../src/copilot-drawer/useConversation';
import { conversationStore } from '../../src/copilot-drawer/conversation-store';
import { foundryThreadMap } from '../../src/copilot-drawer/foundry-thread-map';
import type { ContextEnvelope } from '../../src/context/context-envelope';

function envFor(agent: string, userOid = 'oid-1'): ContextEnvelope {
  return {
    userOid,
    heldRoles: ['HCC.BedManager'],
    activeRole: 'HCC.BedManager',
    hospitalScope: 'usz',
    dataSource: 'simulated',
    agent: agent as ContextEnvelope['agent'],
    windowHours: 72,
  };
}

beforeEach(() => {
  vi.restoreAllMocks();
  conversationStore.reset();
  foundryThreadMap.reset();
});

afterEach(() => {
  vi.unstubAllEnvs();
  foundryThreadMap.reset();
});

describe('useConversation — Foundry thread map wiring (send path)', () => {
  it('mints one Foundry thread per (user x agent) and reuses it across sends when threads are enabled', async () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');
    const { result } = renderHook(() =>
      useConversation('bmca-agent', 'oid-1', envFor('bmca-agent')),
    );

    await act(async () => {
      await result.current.send('Frage 1');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));
    await act(async () => {
      await result.current.send('Frage 2');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(4));

    // Two sends on the same (user x agent) reuse a single Foundry thread.
    expect(foundryThreadMap.size()).toBe(1);
    expect(foundryThreadMap.get('oid-1', 'bmca-agent')).toBeDefined();
  });

  it('mints a distinct thread for a different agent', async () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');
    const bmca = renderHook(() => useConversation('bmca-agent', 'oid-1', envFor('bmca-agent')));
    const ooa = renderHook(() => useConversation('ooa-agent', 'oid-1', envFor('ooa-agent')));

    await act(async () => {
      await bmca.result.current.send('B');
    });
    await act(async () => {
      await ooa.result.current.send('O');
    });

    expect(foundryThreadMap.size()).toBe(2);
  });

  it('does not touch the Foundry thread map when threads are disabled (default)', async () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', '');
    const { result } = renderHook(() =>
      useConversation('bmca-agent', 'oid-1', envFor('bmca-agent')),
    );
    await act(async () => {
      await result.current.send('Frage');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));

    expect(foundryThreadMap.size()).toBe(0);
  });

  it('does not touch the Foundry thread map when no envelope is provided', async () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');
    const { result } = renderHook(() => useConversation('bmca-agent', 'oid-1'));
    await act(async () => {
      await result.current.send('Frage');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));

    expect(foundryThreadMap.size()).toBe(0);
  });

  it('mints a live thread via the agent-host and threads it onto chat when a host is configured', async () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const calls: Array<{ url: string; body: unknown }> = [];
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => {
      const body = init.body ? JSON.parse(init.body as string) : undefined;
      calls.push({ url, body });
      if (url.endsWith('/threads')) {
        return { ok: true, json: async () => ({ threadId: 'thr-live-1', provenance: 'native' }) };
      }
      return {
        ok: true,
        json: async () => ({ answer: 'ok', citations: [], refused: false, interactionId: 'AIX-1' }),
      };
    });
    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() =>
      useConversation('bmca-agent', 'oid-1', envFor('bmca-agent')),
    );
    await act(async () => {
      await result.current.send('Frage 1');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(2));
    await act(async () => {
      await result.current.send('Frage 2');
    });
    await waitFor(() => expect(result.current.turns.length).toBe(4));

    // Minted exactly once (reused on the second send); both chats carry the threadId.
    const mintCalls = calls.filter((c) => c.url.endsWith('/threads'));
    const chatCalls = calls.filter((c) => c.url.endsWith('/chat'));
    expect(mintCalls).toHaveLength(1);
    expect(chatCalls).toHaveLength(2);
    expect(chatCalls.every((c) => (c.body as { threadId?: string }).threadId === 'thr-live-1')).toBe(true);
    expect(foundryThreadMap.get('oid-1', 'bmca-agent')?.provenance).toBe('native');
  });
});
