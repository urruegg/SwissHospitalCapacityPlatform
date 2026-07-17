import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '../../src/i18n';
import { StartView } from '../../src/workspaces/start/StartView';

describe('StartView', () => {
  it('shows the mission and the simulated-data disclaimer', () => {
    render(<StartView />);
    expect(screen.getByRole('heading', { name: /curavias/i })).toBeInTheDocument();
    expect(screen.getByText(/Microsoft Innovation Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/simulated .* generic data .* demo/i)).toBeInTheDocument();
  });
});
