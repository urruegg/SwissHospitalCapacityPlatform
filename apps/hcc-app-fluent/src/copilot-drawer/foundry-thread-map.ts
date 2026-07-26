import type { ContextEnvelope } from '../context/context-envelope';

export interface ThreadRecord {
  threadId: string;
  seed: ContextEnvelope;
}

export function foundryThreadsEnabled(): boolean {
  return (import.meta.env.VITE_FOUNDRY_THREADS_ENABLED ?? '') === 'true';
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
    const record: ThreadRecord = { threadId, seed: env };
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
