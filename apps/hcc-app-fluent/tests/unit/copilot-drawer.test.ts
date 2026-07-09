import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAgentInvoker } from '../../src/copilot-drawer/AgentInvoker';

// No VITE_AGENT_HOST_URL configured in tests → deterministic grounded mock.
beforeEach(() => {
  vi.restoreAllMocks();
});

describe('useAgentInvoker (Copilot Drawer contract)', () => {
  it('produces a grounded reply with citations and no PHI', async () => {
    const { result } = renderHook(() => useAgentInvoker('bmca-agent'));

    await act(async () => {
      await result.current.send('Wie ist die Auslastung auf Station B?');
    });

    await waitFor(() => expect(result.current.turns.length).toBe(2));
    const [user, agent] = result.current.turns;
    expect(user.role).toBe('user');
    expect(agent.role).toBe('agent');
    expect(agent.citations?.length ?? 0).toBeGreaterThan(0);
    expect(agent.refused).toBe(false);
    // No PHI identifiers in the grounded reply.
    expect(agent.text.toLowerCase()).not.toMatch(/patient\s|ahv|geburtsdatum/);
  });

  it('ignores empty prompts', async () => {
    const { result } = renderHook(() => useAgentInvoker('bmca-agent'));
    await act(async () => {
      await result.current.send('   ');
    });
    expect(result.current.turns.length).toBe(0);
  });
});
