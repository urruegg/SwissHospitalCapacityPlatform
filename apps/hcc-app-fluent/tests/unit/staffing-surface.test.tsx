import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { StaffingBoard } from '../../src/workspaces/main/boards/staffing/StaffingBoard';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import { STAFFING_PINNED } from '../../src/data/roleboard/staffing-data';

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
    <MemoryRouter initialEntries={['/main/staffing']}>
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

describe('StaffingBoard surface', () => {
  it('renders staff moves in the coverage table, banner, and a simulated badge', async () => {
    render(
      <Harness>
        <StaffingBoard />
      </Harness>,
    );

    // The coverage worklist renders every shift; role/unit values repeat across
    // rows, so assert each shift by its unique shift number.
    for (const move of STAFFING_PINNED.moves) {
      await waitFor(() => expect(screen.getByText(move.shiftNo)).toBeInTheDocument());
    }
    expect(screen.getByText(/simulated data/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried from orsa-agent/i)).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the sba-agent with insight context', async () => {
    render(
      <Harness>
        <RailState />
        <StaffingBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Shift RN ICU float -> Medicine A/ })).toBeInTheDocument(),
    );
    act(() => screen.getByRole('button', { name: /Shift RN ICU float -> Medicine A/ }).click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('sba-agent', {
      move: 'rn-icu-to-meda',
      fromUnit: 'ICU float',
      toUnit: 'Medicine A',
      role: 'RN',
      fte: 1,
    });
  });
});
