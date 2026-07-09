import { useState, useCallback } from 'react';
import { invokeAgent, type GroundedReply } from './agent-manifest';

export interface ConversationTurn {
  role: 'user' | 'agent';
  text: string;
  citations?: string[];
  refused?: boolean;
}

/**
 * Sprint 13 T6 — agent invoker hook.
 *
 * Owns the conversation turns and the call into the agent-host. Kept separate
 * from the Drawer view so it can be unit-tested without rendering Fluent.
 */
export function useAgentInvoker(agent: string) {
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [busy, setBusy] = useState(false);

  const send = useCallback(
    async (prompt: string) => {
      if (!prompt.trim()) return;
      setTurns((t) => [...t, { role: 'user', text: prompt }]);
      setBusy(true);
      try {
        const reply: GroundedReply = await invokeAgent(agent, prompt);
        setTurns((t) => [
          ...t,
          {
            role: 'agent',
            text: reply.answer,
            citations: reply.citations,
            refused: reply.refused,
          },
        ]);
      } finally {
        setBusy(false);
      }
    },
    [agent],
  );

  return { turns, busy, send };
}
