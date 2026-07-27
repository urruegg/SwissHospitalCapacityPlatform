import { resetConversations } from '../copilot-drawer/conversation-store';
import { foundryThreadMap } from '../copilot-drawer/foundry-thread-map';
import { setContextEnvelope } from '../data/roleboard/golden-source-client';

/**
 * Sprint 29 (#424 M1) — clear all per-user session context on sign-out.
 *
 * Resets every `(user x agent)` conversation thread, the Foundry thread map, and
 * the current IQ `ContextEnvelope` so a subsequent session never inherits a
 * prior user's context or data scope (ADR-0052: "resets cleanly on sign-out").
 */
export function resetSessionContext(): void {
  resetConversations();
  foundryThreadMap.reset();
  setContextEnvelope(null);
}
