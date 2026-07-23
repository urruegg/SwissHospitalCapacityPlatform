import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { RoleProvider } from '../../src/context/role-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { OccupancyBoard } from '../../src/workspaces/main/boards/occupancy/OccupancyBoard';

vi.mock('../../src/copilot-drawer/agent-manifest', async (orig) => {
  const actual = await orig<typeof import('../../src/copilot-drawer/agent-manifest')>();
  return { ...actual, invokeInsight: vi.fn().mockResolvedValue({ answer: 'ok', citations: [], refused: false }) };
});

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function RecoProbe() {
  const { activeReco } = useCopilotRail();
  return <div data-testid="active-reco">{activeReco?.read ?? ''}</div>;
}

function renderBoard() {
  return render(
    <MemoryRouter initialEntries={['/main/occupancy']}>
      <FluentProvider theme={webLightTheme}>
        <ModeProvider>
          <CopilotRailProvider>
            <HospitalProvider claims={parseClaims(undefined)}>
              <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
                <OccupancyBoard />
                <RecoProbe />
              </RoleProvider>
            </HospitalProvider>
          </CopilotRailProvider>
        </ModeProvider>
      </FluentProvider>
    </MemoryRouter>,
  );
}

describe('OccupancyBoard surface', () => {
  it('renders header, ward table rows, and the capacity-flow streams', async () => {
    renderBoard();
    expect(await screen.findByText('Medicine A')).toBeInTheDocument();
    expect(screen.getByText('Surgery B')).toBeInTheDocument();
    expect(screen.getByText(/Emergency & Acute Medicine/i)).toBeInTheDocument();
    expect(screen.getByText(/simulated data/i)).toBeInTheDocument();
  });

  it('routes a ward-row click into a context reco', async () => {
    renderBoard();
    const row = await screen.findByRole('button', { name: /Medicine A/ });
    act(() => row.click());
    await waitFor(() =>
      expect(screen.getByTestId('active-reco').textContent).toMatch(/tips to 102%/i),
    );
  });
});
