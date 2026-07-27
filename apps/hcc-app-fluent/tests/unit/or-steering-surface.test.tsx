import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { OrSteeringBoard } from '../../src/workspaces/main/boards/or-steering/OrSteeringBoard';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';
import { invokeInsight } from '../../src/copilot-drawer/agent-manifest';
import { OR_STEERING_PINNED } from '../../src/data/roleboard/or-steering-data';

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
    <MemoryRouter initialEntries={['/main/or-steering']}>
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

describe('OrSteeringBoard surface', () => {
  it('renders deferable OR cases, banner, and a simulated badge', async () => {
    render(
      <Harness>
        <OrSteeringBoard />
      </Harness>,
    );

    // The schedule renders every elective case; specialties repeat across rows,
    // so assert the two golden-thread deferable cases by their unique case number.
    // (A case number may also appear in the live-stream tooltip, so allow >= 1.)
    for (const orCase of OR_STEERING_PINNED.cases.filter((c) => c.deferable)) {
      await waitFor(() => expect(screen.getAllByText(orCase.caseNo).length).toBeGreaterThanOrEqual(1));
    }
    expect(screen.getByText(/simulated data/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried from bmca-agent/i)).toBeInTheDocument();
  });

  it('opens the Copilot rail and invokes the orsa-agent with insight context', async () => {
    render(
      <Harness>
        <RailState />
        <OrSteeringBoard />
      </Harness>,
    );

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /OR-3301.*Defer Orthopedics case/i })).toBeInTheDocument(),
    );
    act(() => screen.getByRole('button', { name: /OR-3301.*Defer Orthopedics case/i }).click());

    await waitFor(() => expect(screen.getByTestId('rail-open').textContent).toBe('true'));
    expect(invokeInsight).toHaveBeenCalledWith('orsa-agent', {
      case: 'ortho-knee-tue',
      specialty: 'Orthopedics',
      slot: 'Tue 08:00',
      bedsImpact: 1,
    });
  });
});
