import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { DischargeBoard } from '../../src/workspaces/main/boards/discharge/DischargeBoard';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import { DISCHARGE_PINNED } from '../../src/data/roleboard/discharge-data';

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
    <MemoryRouter initialEntries={['/main/discharge']}>
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

describe('DischargeBoard surface', () => {
  it('renders discharge candidates, banner, and a simulated badge', async () => {
    render(
      <Harness>
        <DischargeBoard />
      </Harness>,
    );

    // The worklist renders every candidate; wards/barriers repeat across rows,
    // so assert each candidate by its unique anonymised patient id.
    for (const candidate of DISCHARGE_PINNED.candidates) {
      await waitFor(() => expect(screen.getAllByText(candidate.patientId)[0]).toBeInTheDocument());
    }
    expect(screen.getByText(/simulated data/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried from ooa-agent/i)).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the dca-agent with insight context', async () => {
    render(
      <Harness>
        <RailState />
        <DischargeBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getAllByRole('button', { name: /Expedite Medicine A discharge/ })[0]).toBeInTheDocument(),
    );
    act(() => screen.getAllByRole('button', { name: /Expedite Medicine A discharge/ })[0].click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('dca-agent', {
      candidate: 'med-a-spitex',
      ward: 'Medicine A',
      blocker: '',
      bedsFreeable: 4,
    });
  });
});
