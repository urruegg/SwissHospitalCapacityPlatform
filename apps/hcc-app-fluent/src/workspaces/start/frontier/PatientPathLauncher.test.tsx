import '../../../i18n';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { ModeProvider } from '../../../context/mode-context';
import { RoleProvider } from '../../../context/role-context';
import { LAUNCHER_TILES } from '../role-launcher';
import { StartView } from '../StartView';
import { PatientPathLauncher } from './PatientPathLauncher';

vi.mock('./StartHero', () => ({
  StartHero: () => <div>Start hero</div>,
}));

vi.mock('./BvaDecisionSection', () => ({
  BvaDecisionSection: () => <div>BVA decision</div>,
}));

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(async () => {
  await i18n.changeLanguage('en');
  localStorage.setItem('hcc.mode', 'demo');
});

function renderLauncher(roles: string[] = ['HCC.Viewer']) {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <RoleProvider testRoles={roles} testHomeSite="usz">
          <PatientPathLauncher />
        </RoleProvider>
      </FluentProvider>
    </MemoryRouter>,
  );
}

describe('PatientPathLauncher', () => {
  it('resolves occupancy and discharge links from LAUNCHER_TILES', () => {
    renderLauncher();

    const occupancy = LAUNCHER_TILES.find((tile) => tile.boardKey === 'occupancy');
    const discharge = LAUNCHER_TILES.find((tile) => tile.boardKey === 'discharge');

    expect(occupancy).toBeDefined();
    expect(discharge).toBeDefined();
    expect(screen.getByRole('link', { name: /open occupancy role board/i })).toHaveAttribute(
      'href',
      occupancy?.route,
    );
    expect(screen.getByRole('link', { name: /open discharge role board/i })).toHaveAttribute(
      'href',
      discharge?.route,
    );
  });

  it('represents every standard operational route exactly once', () => {
    const { container } = renderLauncher();
    const standardTiles = LAUNCHER_TILES.filter((tile) => !tile.requiresCsaNav);

    standardTiles.forEach((tile) => {
      expect(container.querySelectorAll(`a[href="${tile.route}"]`)).toHaveLength(1);
    });
    expect(screen.getAllByTestId('patient-path-stop')).toHaveLength(standardTiles.length + 1);
    expect(screen.getByRole('heading', { name: /recovery destination/i })).toBeInTheDocument();
  });

  it('gates the spanning CSA advisory card with the established role capability', () => {
    const crisis = LAUNCHER_TILES.find((tile) => tile.requiresCsaNav);
    expect(crisis).toBeDefined();

    const viewer = renderLauncher(['HCC.Viewer']);
    expect(viewer.container.querySelector(`a[href="${crisis?.route}"]`)).not.toBeInTheDocument();
    expect(screen.queryByTestId('patient-path-csa-advisory')).not.toBeInTheDocument();
    viewer.unmount();

    const admin = renderLauncher(['HCC.PlatformAdmin']);
    const advisory = screen.getByTestId('patient-path-csa-advisory');
    expect(within(advisory).getByRole('link', { name: /open scenario planning role board/i })).toHaveAttribute(
      'href',
      crisis?.route,
    );
    expect(advisory).toHaveTextContent(/advisory/i);
    admin.unmount();
  });

  it('keeps data-quality advisory, evidence, golden-thread, and human-decision semantics visible', () => {
    renderLauncher();

    expect(screen.getByRole('note', { name: /data quality advisory/i })).toBeInTheDocument();
    expect(screen.getByText(/evidence-backed/i)).toBeInTheDocument();
    expect(screen.getByText(/golden thread/i)).toBeInTheDocument();
    const humanDecision = screen.getByRole('contentinfo', { name: /human decision/i });
    expect(humanDecision).toHaveAttribute('role', 'contentinfo');
    expect(humanDecision).toHaveTextContent(/the human decides/i);
  });

  it('replaces the Start placeholder inside the existing patient-path section wrapper', () => {
    render(
      <MemoryRouter initialEntries={['/start']}>
        <FluentProvider theme={webLightTheme}>
          <RoleProvider testRoles={['HCC.PlatformAdmin']} testHomeSite="usz">
            <ModeProvider>
              <StartView />
            </ModeProvider>
          </RoleProvider>
        </FluentProvider>
      </MemoryRouter>,
    );

    const wrappers = screen.getAllByTestId('start-patient-path');
    expect(wrappers).toHaveLength(1);
    expect(within(wrappers[0]).getByRole('link', { name: /open occupancy role board/i })).toBeInTheDocument();
    expect(within(wrappers[0]).queryByText(/launcher section/i)).not.toBeInTheDocument();
  });
});
