import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { CopilotRailProvider, useCopilotRail } from '../../src/copilot-rail/rail-context';

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
