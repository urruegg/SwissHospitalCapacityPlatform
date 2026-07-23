import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { CsaView } from '../../src/workspaces/main/wizards/csa/CsaView';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';

vi.mock('../../src/copilot-drawer/Drawer', () => ({
  CopilotDrawer: () => null,
}));

vi.mock('../../src/copilot-drawer/agent-manifest', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../src/copilot-drawer/agent-manifest')>()),
  invokeInsight: vi.fn().mockResolvedValue({ answer: 'ok', citations: [], refused: false }),
}));

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

function Harness({ children }: { children: React.ReactNode }) {
  const claims = parseClaims(undefined);
  return (
    <MemoryRouter initialEntries={['/main/crisis']}>
      <ModeProvider>
        <CopilotRailProvider>
          <HospitalProvider claims={claims}>
            <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
              {children}
            </RoleProvider>
          </HospitalProvider>
        </CopilotRailProvider>
      </ModeProvider>
    </MemoryRouter>
  );
}

function RailState() {
  const rail = useCopilotRail();
  return <span data-testid="rail-open">{String(rail.open)}</span>;
}

describe('CsaView crisis RoleBoard surface', () => {
  it('renders Trust-A scenarios, loop-back banner, and preserves the existing wizard', async () => {
    render(
      <Harness>
        <CsaView />
      </Harness>,
    );

    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
    expect(screen.getByTestId('CsaWizard')).toBeInTheDocument();
    expect(await screen.findByText(/simulated/i)).toBeInTheDocument();
    expect(screen.getByTestId('loop-back')).toBeInTheDocument();
    expect(screen.getByText('Summer heatwave demand surge')).toBeInTheDocument();
    expect(screen.getByText('Respiratory virus surge')).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the csa-agent with scenario context', async () => {
    render(
      <Harness>
        <RailState />
        <CsaView />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Stress-test Summer heatwave demand surge/ })).toBeInTheDocument(),
    );
    act(() => screen.getByRole('button', { name: /Stress-test Summer heatwave demand surge/ }).click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('csa-agent', {
      scenario: 'heatwave-surge',
      probability: 0.8,
      bedDayImpact: 14,
    });
  });
});
