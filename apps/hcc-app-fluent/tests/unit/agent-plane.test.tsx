import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { AgentPlane } from '../../src/shell/planes/AgentPlane';
import { RoleProvider } from '../../src/context/role-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import type { GroundedReco } from '../../src/copilot-rail/reco';

// Sprint 20 M7 — assert the English affordance copy deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

const reco: GroundedReco = {
  agentLabel: 'Occupancy Copilot',
  contextChip: { subject: 'Medicine A', status: 'OVER', tone: 'over' },
  read: 'Medicine A tips to 102% within 72h.',
  levers: [{ text: 'Expedite 6 discharges', impact: { label: '-6 beds', tone: 'beds' } }],
  primaryCta: { label: 'Open discharge worklist', kind: 'handoff', target: 'dca-agent' },
  citations: [],
  provenance: 'simulated',
};

function Seeder() {
  const rail = useCopilotRail();
  return (
    <button onClick={() => rail.openWithReco({ id: 'med-a', label: 'Medicine A', context: {} }, reco)}>
      seed-reco
    </button>
  );
}

function renderAgent(roles: string[], path = '/csa') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz">
        <CopilotRailProvider>
          <AgentPlane />
        </CopilotRailProvider>
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('AgentPlane', () => {
  it('starts collapsed (icon only) and opens on toggle', () => {
    renderAgent(['HCC.RegionalCrisisLead']);
    const toggle = screen.getByRole('button', { name: /open agent/i });
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument();
    act(() => toggle.click());
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });

  it('shows the action ceiling badge derived from the active role', () => {
    renderAgent(['HCC.Viewer']);
    act(() => screen.getByRole('button', { name: /open agent/i }).click());
    expect(screen.getByText(/read/i)).toBeInTheDocument();
  });

  it('renders a context reco with a back button when one is active', () => {
    render(
      <MemoryRouter initialEntries={['/main/occupancy']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <CopilotRailProvider>
            <Seeder />
            <AgentPlane />
          </CopilotRailProvider>
        </RoleProvider>
      </MemoryRouter>,
    );
    act(() => screen.getByText('seed-reco').click());
    expect(screen.getByText('Medicine A tips to 102% within 72h.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /back to summary/i })).toBeInTheDocument();
  });
});
