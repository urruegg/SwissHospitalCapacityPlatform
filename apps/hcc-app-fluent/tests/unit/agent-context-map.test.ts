import { describe, it, expect } from 'vitest';
import { agentForRoute } from '../../src/shell/planes/agent-context-map';

describe('agent context map', () => {
  it('maps each surface to its default agent', () => {
    expect(agentForRoute('/start')).toBe('orchestrator');
    expect(agentForRoute('/main/bed-manager')).toBe('bmca-agent');
    expect(agentForRoute('/csa')).toBe('csa-agent');
    expect(agentForRoute('/backstage/evidence')).toBe('knowledge-agent');
    expect(agentForRoute('/settings')).toBe('orchestrator');
  });
});
