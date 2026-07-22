import { describe, it, expect, beforeAll, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { ModeProvider } from '../../src/context/mode-context';
import { RoleProvider } from '../../src/context/role-context';
import { StartView } from '../../src/workspaces/start/StartView';

// Sprint 20 M6 — assert the English mission/disclaimer copy deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(() => {
  localStorage.setItem('hcc.mode', 'demo');
});

function renderStart(roles: string[] = ['HCC.PlatformAdmin']) {
  return render(
    <MemoryRouter>
      <RoleProvider testRoles={roles}>
        <ModeProvider>
          <StartView />
        </ModeProvider>
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('StartView', () => {
  it('shows the mission and the simulated-data disclaimer', () => {
    renderStart();
    expect(screen.getByRole('heading', { name: /curavias/i })).toBeInTheDocument();
    expect(screen.getByText(/Microsoft Innovation Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/simulated .* generic data .* demo/i)).toBeInTheDocument();
  });

  it('renders all six role launcher links for a platform admin', () => {
    renderStart();

    expect(screen.getByTestId('launch-occupancy')).toHaveAttribute('href', '/main/occupancy');
    expect(screen.getByTestId('launch-discharge')).toHaveAttribute('href', '/main/discharge');
    expect(screen.getByTestId('launch-bed-manager')).toHaveAttribute('href', '/main/bed-manager');
    expect(screen.getByTestId('launch-or-steering')).toHaveAttribute('href', '/main/or-steering');
    expect(screen.getByTestId('launch-staffing')).toHaveAttribute('href', '/main/staffing');
    expect(screen.getByTestId('launch-crisis')).toHaveAttribute('href', '/main/crisis');
  });

  it('hides the crisis launcher when the active role lacks CSA navigation', () => {
    renderStart(['HCC.BedManager']);

    expect(screen.getByTestId('launch-occupancy')).toBeInTheDocument();
    expect(screen.queryByTestId('launch-crisis')).toBeNull();
  });

  it('shows the demo mode badge by default', () => {
    renderStart();

    expect(screen.getByTestId('start-mode-badge')).toHaveTextContent(
      /Demo — simulated golden-thread showcase/i,
    );
  });
});
