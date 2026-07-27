import { useCallback, useSyncExternalStore } from 'react';
import { invokeAgent, sendInteractionEvent, type GroundedReply } from './agent-manifest';
import type { ConversationTurn } from './AgentInvoker';
import { conversationStore, conversationKey } from './conversation-store';
import { foundryThreadMap, foundryThreadsEnabled } from './foundry-thread-map';
import type { ContextEnvelope } from '../context/context-envelope';

/**
 * Sprint 29 M1 — per-(user x agent) conversation hook.
 *
 * Drop-in replacement for `useAgentInvoker(agent)` that reads and writes the
 * shared {@link conversationStore} keyed by `(userOid, agent)`. Because the turn
 * list lives in the store (not local component state), switching the `agent`
 * argument surfaces *that* agent's own thread instead of leaking the previous
 * agent's turns (design Q2). `userOid` is optional in M1 and becomes the primary
 * scoping key in M4.
 *
 * #424 M1 — when an agent-scoped `env` is supplied and live Foundry threads are
 * enabled (`VITE_FOUNDRY_THREADS_ENABLED`), each send resolves/reuses this
 * `(user x agent)` Foundry thread via {@link foundryThreadMap}. The `threadId`
 * is handed to the agent-host in the live-thread milestone (#424 M3); here it
 * seeds the map so the wiring — and its reset on sign-out — is exercised.
 */
export function useConversation(
  agent: string,
  userOid?: string | null,
  env?: ContextEnvelope | null,
) {
  const key = conversationKey(agent, userOid);

  const slice = useSyncExternalStore(
    (listener) => conversationStore.subscribe(listener),
    () => conversationStore.getSlice(key),
    () => conversationStore.getSlice(key),
  );

  const send = useCallback(
    async (prompt: string) => {
      if (!prompt.trim()) return;
      // #424 M1 — resolve/reuse the live Foundry thread for this (user x agent)
      // when threads are enabled. The record's threadId is passed to the
      // agent-host in #424 M3; here it seeds the map (reset on sign-out).
      if (env && env.agent != null && foundryThreadsEnabled()) {
        foundryThreadMap.getOrCreate(env);
      }
      conversationStore.appendTurn(key, { role: 'user', text: prompt });
      conversationStore.setBusy(key, true);
      try {
        const reply: GroundedReply = await invokeAgent(agent, prompt);
        const turn: ConversationTurn = {
          role: 'agent',
          text: reply.answer,
          citations: reply.citations,
          refused: reply.refused,
          interactionId: reply.interactionId,
        };
        conversationStore.appendTurn(key, turn);
      } finally {
        conversationStore.setBusy(key, false);
      }
    },
    [key, agent, env],
  );

  /**
   * Sprint 30 M2 — emit a thumbs user-event for a captured turn. Best-effort and
   * advisory-only: routes through `sendInteractionEvent`, which no-ops without a
   * live agent-host and never throws into the UI.
   */
  const rate = useCallback(
    async (interactionId: string, value: 'up' | 'down') => {
      await sendInteractionEvent(agent, interactionId, 'thumbs', value);
    },
    [agent],
  );

  return { turns: slice.turns, busy: slice.busy, send, rate };
}
