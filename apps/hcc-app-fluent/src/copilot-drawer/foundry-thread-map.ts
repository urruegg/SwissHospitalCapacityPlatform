import type { ContextEnvelope } from '../context/context-envelope';
import { getFoundryThreadsEnabled } from '../config/runtime-config';

export interface ThreadRecord {
  threadId: string;
  seed: ContextEnvelope;
  /** Where the thread is persisted server-side (#424 M3): `native` | `foundry` | `simulated`. */
  provenance?: string;
}

export function foundryThreadsEnabled(): boolean {
  return getFoundryThreadsEnabled();
}

export function threadKey(userOid: string | null, agent: string): string {
  return `${userOid ?? 'anon'}::${agent}`;
}

export class FoundryThreadMap {
  private readonly records = new Map<string, ThreadRecord>();
  private readonly minter: (env: ContextEnvelope) => string;
  private counter = 0;

  constructor(minter?: (env: ContextEnvelope) => string) {
    this.minter = minter ?? ((env) => this.simulatedThreadId(env));
  }

  getOrCreate(env: ContextEnvelope): ThreadRecord {
    if (env.agent == null) {
      throw new Error('Foundry thread requires an agent-scoped ContextEnvelope');
    }

    const key = threadKey(env.userOid, env.agent);
    const existing = this.records.get(key);
    if (existing) return existing;

    const threadId = this.minter(env);
    const record: ThreadRecord = { threadId, seed: env, provenance: 'simulated' };
    this.records.set(key, record);
    return record;
  }

  /**
   * #424 M3 — resolve/reuse the live `(user x agent)` thread via an async minter
   * (the agent-host `POST /threads`). Cached per `(userOid x agent)` so a mint
   * happens once and later sends reuse it. A failed mint is not stored, so the
   * next send retries and no agent's thread is corrupted.
   */
  async resolve(
    env: ContextEnvelope,
    mint: (env: ContextEnvelope) => Promise<{ threadId: string; provenance?: string }>,
  ): Promise<ThreadRecord> {
    if (env.agent == null) {
      throw new Error('Foundry thread requires an agent-scoped ContextEnvelope');
    }
    const key = threadKey(env.userOid, env.agent);
    const existing = this.records.get(key);
    if (existing) return existing;

    const { threadId, provenance } = await mint(env);
    const record: ThreadRecord = { threadId, seed: env, provenance: provenance ?? 'native' };
    this.records.set(key, record);
    return record;
  }

  get(userOid: string | null, agent: string): ThreadRecord | undefined {
    return this.records.get(threadKey(userOid, agent));
  }

  reset(): void {
    this.records.clear();
  }

  size(): number {
    return this.records.size;
  }

  private simulatedThreadId(env: ContextEnvelope): string {
    return `sim-thread-${threadKey(env.userOid, env.agent!)}-${++this.counter}`;
  }
}

export const foundryThreadMap = new FoundryThreadMap();
