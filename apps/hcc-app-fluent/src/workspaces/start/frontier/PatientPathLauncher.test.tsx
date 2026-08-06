import '../../../i18n';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { CopilotRailProvider, useCopilotRail } from '../../../copilot-rail/rail-context';
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

function RailProbe() {
  const rail = useCopilotRail();
  return (
    <div hidden>
      <span data-testid="rail-open">{String(rail.open)}</span>
      <span data-testid="rail-read">{rail.activeReco?.read ?? ''}</span>
      <span data-testid="rail-citations">{rail.activeReco?.citations.join('|') ?? ''}</span>
    </div>
  );
}

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

function renderLauncherWithRail(roles: string[] = ['HCC.PlatformAdmin']) {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <RoleProvider testRoles={roles} testHomeSite="usz">
          <CopilotRailProvider>
            <PatientPathLauncher />
            <RailProbe />
          </CopilotRailProvider>
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

  it('renders the DC-INSIGHT five-beat pattern and the 102%\u219294% worked example', () => {
    renderLauncher();

    const dcInsightCard = screen.getByTestId('patient-path-dc-insight-card');
    expect(within(dcInsightCard).getByText(/how an agent answers/i)).toBeInTheDocument();
    ['SIGNAL', 'UNDERSTANDING', 'RECOMMENDATION', 'ACTION', 'COORDINATION'].forEach((label) => {
      expect(within(dcInsightCard).getByText(label)).toBeInTheDocument();
    });

    const workedExample = screen.getByTestId('patient-path-worked-example-card');
    expect(within(workedExample).getByText('102%')).toBeInTheDocument();
    expect(within(workedExample).getByText('94%')).toBeInTheDocument();
    expect(within(workedExample).getByText(/advisory/i)).toBeInTheDocument();
    expect(within(workedExample).getByText(/auditable/i)).toBeInTheDocument();
  });

  it('wires patient-path stops, advisories, and the DC-INSIGHT/worked-example cards to the Copilot rail', () => {
    renderLauncherWithRail(['HCC.PlatformAdmin']);

    expect(screen.getByTestId('rail-open')).toHaveTextContent('false');

    fireEvent.click(screen.getByRole('link', { name: /open occupancy role board/i }));
    expect(screen.getByTestId('rail-open')).toHaveTextContent('true');

    fireEvent.click(screen.getByTestId('patient-path-dc-insight-card'));
    expect(screen.getByTestId('rail-read')).toHaveTextContent(/medicine a is forecast to breach/i);

    fireEvent.click(screen.getByTestId('patient-path-worked-example-card'));
    expect(screen.getByTestId('rail-citations')).toHaveTextContent('hcp:CapacityForecast');

    fireEvent.click(screen.getByTestId('patient-path-data-quality-trigger'));
    expect(screen.getByTestId('rail-read')).toHaveTextContent(/data quality agent checks provenance/i);

    fireEvent.click(screen.getByRole('link', { name: /open scenario planning role board/i }));
    expect(screen.getByTestId('rail-citations')).toHaveTextContent('hcp:PatientPath:crisis');
  });

  it('renders circular agent nodes with acronym badges and evidence chips for each operational stop', () => {
    renderLauncher(['HCC.PlatformAdmin']);

    const flow = screen.getByTestId('patient-path-flow');

    // 5 operational stops + 1 recovery terminal = 6 circular nodes
    expect(within(flow).getAllByTestId('patient-path-node')).toHaveLength(6);

    // agent acronym badges derived from LAUNCHER_TILES agent ids
    ['OOA', 'BMCA', 'ORSA', 'SBA', 'DCA'].forEach((acronym) => {
      expect(within(flow).getByText(acronym)).toBeInTheDocument();
    });

    // operational step names + evidence chips from the content model
    expect(within(flow).getByText('Emergency & Admission')).toBeInTheDocument();
    expect(within(flow).getByText('Place 8 + boarders')).toBeInTheDocument();
    expect(within(flow).getByText('Free 8 beds')).toBeInTheDocument();
    expect(within(flow).getAllByTestId('patient-path-evidence')).toHaveLength(5);
  });

  it('surfaces the cross-path crisis and data-quality copilots as top banners', () => {
    const admin = renderLauncher(['HCC.PlatformAdmin']);
    const banners = screen.getByTestId('patient-path-banners');
    expect(within(banners).getByText(/crisis & scenarios/i)).toBeInTheDocument();
    expect(within(banners).getByText(/data quality gates/i)).toBeInTheDocument();
    admin.unmount();

    // the crisis banner stays gated by the CSA navigation capability
    renderLauncher(['HCC.Viewer']);
    const viewerBanners = screen.getByTestId('patient-path-banners');
    expect(within(viewerBanners).queryByText(/crisis & scenarios/i)).not.toBeInTheDocument();
    expect(within(viewerBanners).getByText(/data quality gates/i)).toBeInTheDocument();
  });
});
