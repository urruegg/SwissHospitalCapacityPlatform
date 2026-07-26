import { useCallback, useSyncExternalStore } from 'react';
import { invokeAgent, type GroundedReply } from './agent-manifest';
import type { ConversationTurn } from './AgentInvoker';
import { conversationStore, conversationKey } from './conversation-store';

/**
 * Sprint 29 M1 — per-(user x agent) conversation hook.
 *
 * Drop-in replacement for `useAgentInvoker(agent)` that reads and writes the
 * shared {@link conversationStore} keyed by `(userOid, agent)`. Because the turn
 * list lives in the store (not local component state), switching the `agent`
 * argument surfaces *that* agent's own thread instead of leaking the previous
 * agent's turns (design Q2). `userOid` is optional in M1 and becomes the primary
 * scoping key in M4.
 */
export function useConversation(agent: string, userOid?: string | null) {
  const key = conversationKey(agent, userOid);

  const slice = useSyncExternalStore(
    (listener) => conversationStore.subscribe(listener),
    () => conversationStore.getSlice(key),
    () => conversationStore.getSlice(key),
  );

  const send = useCallback(
    async (prompt: string) => {
      if (!prompt.trim()) return;
      conversationStore.appendTurn(key, { role: 'user', text: prompt });
      conversationStore.setBusy(key, true);
      try {
        const reply: GroundedReply = await invokeAgent(agent, prompt);
        const turn: ConversationTurn = {
          role: 'agent',
          text: reply.answer,
          citations: reply.citations,
          refused: reply.refused,
        };
        conversationStore.appendTurn(key, turn);
      } finally {
        conversationStore.setBusy(key, false);
      }
    },
    [key, agent],
  );

  return { turns: slice.turns, busy: slice.busy, send };
}
