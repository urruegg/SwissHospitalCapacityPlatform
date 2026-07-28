import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { resetSessionContext } from '../../src/context/session-reset';
import { conversationStore } from '../../src/copilot-drawer/conversation-store';
import { foundryThreadMap } from '../../src/copilot-drawer/foundry-thread-map';
import {
  getContextEnvelope,
  setContextEnvelope,
} from '../../src/data/roleboard/golden-source-client';
import type { ContextEnvelope } from '../../src/context/context-envelope';

const envelope: ContextEnvelope = {
  userOid: 'oid-1',
  heldRoles: ['HCC.BedManager'],
  activeRole: 'HCC.BedManager',
  hospitalScope: 'usz',
  dataSource: 'simulated',
  agent: 'bmca-agent',
  windowHours: 72,
};

beforeEach(() => {
  foundryThreadMap.reset();
  conversationStore.reset();
  setContextEnvelope(null);
});

afterEach(() => {
  foundryThreadMap.reset();
  conversationStore.reset();
  setContextEnvelope(null);
});

describe('resetSessionContext (sign-out)', () => {
  it('clears conversations, the Foundry thread map, and the context envelope', () => {
    conversationStore.appendTurn('oid-1::bmca-agent', { role: 'user', text: 'Frage' });
    foundryThreadMap.getOrCreate(envelope);
    setContextEnvelope(envelope);

    expect(conversationStore.getSlice('oid-1::bmca-agent').turns.length).toBe(1);
    expect(foundryThreadMap.size()).toBe(1);
    expect(getContextEnvelope()).not.toBeNull();

    resetSessionContext();

    expect(conversationStore.getSlice('oid-1::bmca-agent').turns.length).toBe(0);
    expect(foundryThreadMap.size()).toBe(0);
    expect(getContextEnvelope()).toBeNull();
  });
});
