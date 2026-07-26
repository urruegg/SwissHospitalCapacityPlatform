import type { ConversationTurn } from './AgentInvoker';

/**
 * Sprint 29 M1 — the conversation store.
 *
 * Fixes the cross-agent chat bleed (design Q2): instead of one shared turn
 * list, every (user x agent) thread is stored under its own key so switching
 * boards shows *that* agent's own conversation and never leaks turns across
 * agents. The key is derived by {@link conversationKey}, structured so it can
 * extend from `agent` (M1) to `userOid::agent` (M4) without touching callers.
 *
 * The store is a tiny external store consumed via `useSyncExternalStore` in
 * {@link useConversation}. Snapshots are referentially stable: unchanged slices
 * return the same object, so unrelated threads never trigger re-renders.
 */

export interface ConversationSlice {
  turns: ConversationTurn[];
  busy: boolean;
}

type Listener = () => void;

/** Shared, frozen empty slice so unseen keys return a stable reference. */
const EMPTY_SLICE: ConversationSlice = Object.freeze({ turns: [], busy: false });

class ConversationStore {
  private slices = new Map<string, ConversationSlice>();
  private listeners = new Set<Listener>();

  /** Current slice for a key; a stable empty slice when the thread is unseen. */
  getSlice(key: string): ConversationSlice {
    return this.slices.get(key) ?? EMPTY_SLICE;
  }

  appendTurn(key: string, turn: ConversationTurn): void {
    const cur = this.getSlice(key);
    this.commit(key, { ...cur, turns: [...cur.turns, turn] });
  }

  setBusy(key: string, busy: boolean): void {
    const cur = this.getSlice(key);
    if (cur.busy === busy) return;
    this.commit(key, { ...cur, busy });
  }

  /** Clear every thread — called on sign-out. */
  reset(): void {
    if (this.slices.size === 0) return;
    this.slices.clear();
    this.emit();
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private commit(key: string, slice: ConversationSlice): void {
    this.slices.set(key, slice);
    this.emit();
  }

  private emit(): void {
    for (const listener of this.listeners) listener();
  }
}

export const conversationStore = new ConversationStore();

/**
 * Derive the store key for a conversation thread. `agent` alone in M1; once a
 * signed-in user's `oid` is threaded through (M4) the key becomes per-user so
 * two users never share a thread on the same board-agent.
 */
export function conversationKey(agent: string, userOid?: string | null): string {
  return userOid ? `${userOid}::${agent}` : agent;
}

/** Reset all conversation threads (sign-out). */
export function resetConversations(): void {
  conversationStore.reset();
}
