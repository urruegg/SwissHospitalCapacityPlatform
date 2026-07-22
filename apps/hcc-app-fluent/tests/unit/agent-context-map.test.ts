import { describe, it, expect } from 'vitest';
import { agentForRoute } from '../../src/shell/planes/agent-context-map';

describe('agent context map', () => {
  it('maps each MAIN board to its role agent', () => {
    expect(agentForRoute('/main/occupancy')).toBe('ooa-agent');
    expect(agentForRoute('/main/discharge')).toBe('dca-agent');
    expect(agentForRoute('/main/bed-manager')).toBe('bmca-agent');
    expect(agentForRoute('/main/or-steering')).toBe('orsa-agent');
    expect(agentForRoute('/main/staffing')).toBe('sba-agent');
    expect(agentForRoute('/main/crisis')).toBe('csa-agent');
  });

  it('falls through to knowledge/orchestrator for non-board surfaces', () => {
    expect(agentForRoute('/backstage/evidence')).toBe('knowledge-agent');
    expect(agentForRoute('/start')).toBe('orchestrator');
    expect(agentForRoute('/settings')).toBe('orchestrator');
    expect(agentForRoute('/main')).toBe('orchestrator');
  });
});
