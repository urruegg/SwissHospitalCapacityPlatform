import { afterEach, describe, expect, it, vi } from 'vitest';
import type { ContextEnvelope } from '../../src/context/context-envelope';
import { FoundryThreadMap, foundryThreadsEnabled } from '../../src/copilot-drawer/foundry-thread-map';

const baseEnvelope: ContextEnvelope = {
  userOid: 'oid-1',
  heldRoles: ['HCC.BedManager'],
  activeRole: 'HCC.BedManager',
  hospitalScope: 'usz',
  dataSource: 'simulated',
  agent: 'ooa-agent',
  windowHours: 72,
};

describe('FoundryThreadMap', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('creates a distinct threadId per userOid and agent', () => {
    const map = new FoundryThreadMap();

    const ooa = map.getOrCreate(baseEnvelope);
    const csa = map.getOrCreate({ ...baseEnvelope, agent: 'csa-agent' });
    const otherUser = map.getOrCreate({ ...baseEnvelope, userOid: 'oid-2' });

    expect(csa.threadId).not.toBe(ooa.threadId);
    expect(otherUser.threadId).not.toBe(ooa.threadId);
  });

  it('seeds a thread once and reuses the original seed for the same userOid and agent', () => {
    const map = new FoundryThreadMap();
    const first = map.getOrCreate(baseEnvelope);
    const secondEnvelope: ContextEnvelope = { ...baseEnvelope, hospitalScope: 'aggregated' };

    const second = map.getOrCreate(secondEnvelope);

    expect(second.threadId).toBe(first.threadId);
    expect(second.seed).toEqual(baseEnvelope);
  });

  it('rejects an agent-less envelope', () => {
    const map = new FoundryThreadMap();

    expect(() => map.getOrCreate({ ...baseEnvelope, agent: null })).toThrow(/agent-scoped/);
  });

  it('does not store a failed mint or corrupt existing threads', () => {
    let failCsa = true;
    const map = new FoundryThreadMap((env) => {
      if (env.agent === 'csa-agent' && failCsa) throw new Error('mint failed');
      return `thread-${env.userOid}-${env.agent}`;
    });

    const ooa = map.getOrCreate(baseEnvelope);

    expect(() => map.getOrCreate({ ...baseEnvelope, agent: 'csa-agent' })).toThrow('mint failed');
    expect(map.get(baseEnvelope.userOid, 'csa-agent')).toBeUndefined();
    expect(map.get(baseEnvelope.userOid, 'ooa-agent')).toBe(ooa);
    expect(map.size()).toBe(1);

    failCsa = false;
    const csa = map.getOrCreate({ ...baseEnvelope, agent: 'csa-agent' });

    expect(csa.threadId).toBe('thread-oid-1-csa-agent');
    expect(map.size()).toBe(2);
  });

  it('reads the Foundry thread config gate from import.meta.env', () => {
    expect(foundryThreadsEnabled()).toBe(false);

    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');

    expect(foundryThreadsEnabled()).toBe(true);
  });

  it('resolve() mints once via the async minter and reuses it per (user x agent)', async () => {
    const map = new FoundryThreadMap();
    const mint = vi.fn(async (e: ContextEnvelope) => ({
      threadId: `thr-${e.userOid}-${e.agent}`,
      provenance: 'native',
    }));

    const first = await map.resolve(baseEnvelope, mint);
    const second = await map.resolve({ ...baseEnvelope, hospitalScope: 'aggregated' }, mint);

    expect(first.threadId).toBe('thr-oid-1-ooa-agent');
    expect(first.provenance).toBe('native');
    expect(second.threadId).toBe(first.threadId);
    expect(mint).toHaveBeenCalledTimes(1); // minted once, reused after
  });

  it('resolve() rejects an agent-less envelope', async () => {
    const map = new FoundryThreadMap();
    await expect(
      map.resolve({ ...baseEnvelope, agent: null }, async () => ({ threadId: 'x' })),
    ).rejects.toThrow(/agent-scoped/);
  });
});
