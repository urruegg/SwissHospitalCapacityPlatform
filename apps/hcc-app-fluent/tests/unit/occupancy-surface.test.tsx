import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { OccupancyBoard } from '../../src/workspaces/main/boards/occupancy/OccupancyBoard';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import { OCCUPANCY_PINNED } from '../../src/data/roleboard/occupancy-data';

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
    <MemoryRouter initialEntries={['/main/occupancy']}>
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

describe('OccupancyBoard surface', () => {
  it('renders trusted-data channels, banner, and a simulated badge', async () => {
    render(
      <Harness>
        <OccupancyBoard />
      </Harness>,
    );

    for (const channel of OCCUPANCY_PINNED.channels) {
      await waitFor(() => expect(screen.getByText(channel.label)).toBeInTheDocument());
      expect(screen.getByText(`${channel.occupancyPct}%`)).toBeInTheDocument();
    }
    expect(screen.getByText(/simulated/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried from ooa-agent/i)).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the ooa-agent with insight context', async () => {
    render(
      <Harness>
        <RailState />
        <OccupancyBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Medicine A rising/ })).toBeInTheDocument(),
    );
    act(() => screen.getByRole('button', { name: /Medicine A rising/ }).click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('ooa-agent', {
      channel: 'med-a',
      occupancyPct: 102,
      deltaBeds: -9,
    });
  });
});
