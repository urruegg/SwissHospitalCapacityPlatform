import { render, screen, act } from '@testing-library/react';
import { ThemeModeProvider, useThemeMode } from '../../src/theme/theme-context';

function Probe() {
  const { mode, toggle } = useThemeMode();
  return <button onClick={toggle}>{mode}</button>;
}

describe('theme mode', () => {
  it('defaults to light and toggles + persists to localStorage', () => {
    render(
      <ThemeModeProvider>
        <Probe />
      </ThemeModeProvider>,
    );
    const btn = screen.getByRole('button');
    expect(btn.textContent).toBe('light');
    act(() => btn.click());
    expect(btn.textContent).toBe('dark');
    expect(localStorage.getItem('curavias.theme')).toBe('dark');
  });
});
