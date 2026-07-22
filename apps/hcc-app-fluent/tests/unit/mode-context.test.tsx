import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { ModeProvider, useMode } from '../../src/context/mode-context';

function Probe() {
  const { mode, setMode } = useMode();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <button onClick={() => setMode('user')}>go-user</button>
    </div>
  );
}

describe('mode-context', () => {
  beforeEach(() => localStorage.clear());

  it('defaults to demo mode', () => {
    render(
      <ModeProvider>
        <Probe />
      </ModeProvider>,
    );
    expect(screen.getByTestId('mode').textContent).toBe('demo');
  });

  it('switches and persists the mode', () => {
    render(
      <ModeProvider>
        <Probe />
      </ModeProvider>,
    );
    act(() => screen.getByText('go-user').click());
    expect(screen.getByTestId('mode').textContent).toBe('user');
    expect(localStorage.getItem('hcc.mode')).toBe('user');
  });

  it('rehydrates the persisted mode', () => {
    localStorage.setItem('hcc.mode', 'user');
    render(
      <ModeProvider>
        <Probe />
      </ModeProvider>,
    );
    expect(screen.getByTestId('mode').textContent).toBe('user');
  });
});
