import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';
import type { GroundedReco } from '../../src/copilot-rail/reco';

function Probe() {
  const rail = useCopilotRail();
  return (
    <div>
      <span data-testid="open">{String(rail.open)}</span>
      <span data-testid="ctx">{rail.activeContext?.label ?? 'none'}</span>
      <button onClick={() => rail.openWithContext({ id: 'i1', label: 'Medicine A rising', context: {} })}>
        open
      </button>
      <button onClick={() => rail.close()}>close</button>
    </div>
  );
}

const reco: GroundedReco = {
  agentLabel: 'Occupancy Copilot',
  contextChip: { subject: 'Medicine A', tone: 'over' },
  read: 'r',
  levers: [],
  citations: [],
  provenance: 'simulated',
};

const liveReco: GroundedReco = {
  ...reco,
  contextChip: { subject: 'Medicine A (live)', tone: 'over' },
};

function RecoProbe() {
  const rail = useCopilotRail();
  return (
    <div>
      <span data-testid="open">{String(rail.open)}</span>
      <span data-testid="reco">{rail.activeReco?.contextChip.subject ?? 'none'}</span>
      <span data-testid="default">{rail.defaultReco?.contextChip.subject ?? 'none'}</span>
      <button onClick={() => rail.showDefault(reco)}>seed</button>
      <button onClick={() => rail.openWithReco({ id: 'med-a', label: 'Medicine A', context: {} }, reco)}>open</button>
      <button onClick={() => rail.backToDefault()}>back</button>
      <button onClick={() => rail.updateActiveReco(liveReco)}>update</button>
    </div>
  );
}

describe('copilot rail reco state', () => {
  it('opens with a reco and returns to the default view', () => {
    render(
      <CopilotRailProvider>
        <RecoProbe />
      </CopilotRailProvider>,
    );
    act(() => screen.getByText('seed').click());
    expect(screen.getByTestId('default').textContent).toBe('Medicine A');
    act(() => screen.getByText('open').click());
    expect(screen.getByTestId('open').textContent).toBe('true');
    expect(screen.getByTestId('reco').textContent).toBe('Medicine A');
    act(() => screen.getByText('back').click());
    expect(screen.getByTestId('reco').textContent).toBe('none');
    expect(screen.getByTestId('open').textContent).toBe('true');
  });

  it('updateActiveReco replaces the active reco in place without closing the rail', () => {
    render(
      <CopilotRailProvider>
        <RecoProbe />
      </CopilotRailProvider>,
    );
    act(() => screen.getByText('open').click());
    expect(screen.getByTestId('reco').textContent).toBe('Medicine A');
    act(() => screen.getByText('update').click());
    expect(screen.getByTestId('reco').textContent).toBe('Medicine A (live)');
    expect(screen.getByTestId('open').textContent).toBe('true');
  });

  it('updateActiveReco is a no-op when the rail has no active reco', () => {
    render(
      <CopilotRailProvider>
        <RecoProbe />
      </CopilotRailProvider>,
    );
    expect(screen.getByTestId('reco').textContent).toBe('none');
    act(() => screen.getByText('update').click());
    expect(screen.getByTestId('reco').textContent).toBe('none');
  });
});

describe('copilot rail context', () => {
  it('opens with the clicked insight context and closes', () => {
    render(
      <CopilotRailProvider>
        <Probe />
      </CopilotRailProvider>,
    );
    expect(screen.getByTestId('open').textContent).toBe('false');
    act(() => screen.getByText('open').click());
    expect(screen.getByTestId('open').textContent).toBe('true');
    expect(screen.getByTestId('ctx').textContent).toBe('Medicine A rising');
    act(() => screen.getByText('close').click());
    expect(screen.getByTestId('open').textContent).toBe('false');
  });
});
