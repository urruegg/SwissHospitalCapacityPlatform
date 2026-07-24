import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { BedManagerBoard } from '../../src/workspaces/main/boards/bed-manager/BedManagerBoard';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import { BEDMANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';

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
    <MemoryRouter initialEntries={['/main/bed-manager']}>
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

describe('BedManagerBoard surface (parity)', () => {
  it('renders the board root with data-testid and HandoffBanner', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    // Wait for board section to appear (data loaded)
    expect(await screen.findByTestId('board-bed-manager')).toBeInTheDocument();
    // Wait for "Carried from dca-agent" — this requires both data and prev to resolve
    expect(await screen.findByText(/Carried from dca-agent/i)).toBeInTheDocument();
    // Provenance badge — synchronous once board rendered
    expect(screen.getAllByText(/simulated/i)[0]).toBeInTheDocument();
  });

  it('renders placement requests with patient IDs and priority badges', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    for (const p of BEDMANAGER_PINNED.placements) {
      await waitFor(() =>
        expect(screen.getByText(p.patientId)).toBeInTheDocument(),
      );
    }
    expect(screen.getAllByText('HIGH')[0]).toBeInTheDocument();
    expect(screen.getByText('MED')).toBeInTheDocument();
    expect(screen.getByText('LOW')).toBeInTheDocument();
  });

  it('renders placement barriers sorted by bedImpact', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByText('Ward capacity overflow')).toBeInTheDocument(),
    );
    expect(screen.getByText('Bed cleaning backlog')).toBeInTheDocument();
  });

  it('renders the admissions eventstream with admit and discharge badges', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() => expect(screen.getAllByText('admit')[0]).toBeInTheDocument());
    expect(screen.getAllByText('discharge')[0]).toBeInTheDocument();
  });

  it('renders the Power BI embed card (capacity-dashboard)', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByText('capacity-dashboard')).toBeInTheDocument(),
    );
    expect(
      screen.getByText(/Power BI Embed.*Direct Lake.*RLS/i),
    ).toBeInTheDocument();
  });

  it('has NO duplicate "Bettenmanagement" Title2 heading and no whiteboard Canvas', async () => {
    const { container } = render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() => expect(screen.getByTestId('board-bed-manager')).toBeInTheDocument());
    // Only one board root element
    expect(container.querySelectorAll('[data-testid="board-bed-manager"]')).toHaveLength(1);
    // No per-board overlay CopilotDrawer "Ask BMCA" button
    expect(screen.queryByRole('button', { name: /Ask BMCA/i })).toBeNull();
  });

  it('opens the Copilot rail when a placement request row is clicked', async () => {
    render(
      <Harness>
        <RailState />
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /Move PT-4001 from Surgery A to ICU/i }),
      ).toBeInTheDocument(),
    );
    act(() =>
      screen.getByRole('button', { name: /Move PT-4001 from Surgery A to ICU/i }).click(),
    );

    await waitFor(() =>
      expect(screen.getByTestId('rail-open').textContent).toBe('true'),
    );
    expect(invokeInsight).toHaveBeenCalledWith('bmca-agent', {
      placement: 'place-pt-4001',
      patientId: 'PT-4001',
      fromWard: 'Surgery A',
      toWard: 'ICU',
    });
  });
});
