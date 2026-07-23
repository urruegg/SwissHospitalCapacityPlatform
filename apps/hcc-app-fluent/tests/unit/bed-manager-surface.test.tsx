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

vi.mock('../../src/copilot-drawer/Drawer', () => ({
  CopilotDrawer: () => null,
}));

vi.mock('../../src/whiteboard/Canvas', () => ({
  Canvas: () => null,
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

describe('BedManagerBoard surface', () => {
  it('renders the handoff banner and preserves the Ask BMCA action', async () => {
    render(
      <Harness>
        <BedManagerBoard />
      </Harness>,
    );

    expect(screen.getByRole('button', { name: /Ask BMCA/ })).toBeInTheDocument();
    expect(await screen.findByText(/simulated/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried from ooa-agent/i)).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the bmca-agent with reallocation context', async () => {
    render(
      <Harness>
        <RailState />
        <BedManagerBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Shift 2 beds Surgery A -> Medicine A/ })).toBeInTheDocument(),
    );
    act(() => screen.getByRole('button', { name: /Shift 2 beds Surgery A -> Medicine A/ }).click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('bmca-agent', {
      reallocation: 'surg-a-to-med-a',
      fromWard: 'Surgery A',
      toWard: 'Medicine A',
      beds: 2,
    });
  });
});
