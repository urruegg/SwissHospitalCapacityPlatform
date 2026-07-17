import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import i18n from '../../src/i18n';
import { StartView } from '../../src/workspaces/start/StartView';

// Sprint 20 M6 — assert the English mission/disclaimer copy deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('StartView', () => {
  it('shows the mission and the simulated-data disclaimer', () => {
    render(<StartView />);
    expect(screen.getByRole('heading', { name: /curavias/i })).toBeInTheDocument();
    expect(screen.getByText(/Microsoft Innovation Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/simulated .* generic data .* demo/i)).toBeInTheDocument();
  });
});
