import '../../../i18n';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { ModeProvider } from '../../../context/mode-context';
import { RoleProvider } from '../../../context/role-context';
import { StartView } from '../StartView';
import { CioChallengerSection } from './CioChallengerSection';
import { HospitalsSection } from './HospitalsSection';
import { NinetyDaySection } from './NinetyDaySection';
import { WorkChartSection } from './WorkChartSection';
import {
  CIO_DECISIONS,
  FRONTIER_AGENTS,
  FRONTIER_HOSPITALS,
  NINETY_DAY_PHASES,
  WORK_MODES,
} from './start-content';

vi.mock('./StartHero', () => ({
  StartHero: () => <div>Start hero</div>,
}));

vi.mock('./PatientPathLauncher', () => ({
  PatientPathLauncher: () => <div>Patient path</div>,
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

function renderSection(section: React.ReactNode) {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>{section}</FluentProvider>
    </MemoryRouter>,
  );
}

describe('WorkChartSection', () => {
  it('renders the three work modes as a structured work flow', () => {
    renderSection(<WorkChartSection />);

    const modes = screen.getAllByTestId('work-chart-mode');
    expect(modes).toHaveLength(WORK_MODES.length);
    expect(modes.map((mode) => within(mode).getByRole('heading').textContent)).toEqual([
      'Humans',
      'Agents',
      'On-demand work',
    ]);
    expect(screen.getByRole('note', { name: /frontier firm principle/i })).toHaveTextContent(
      /curavias/i,
    );
  });
});

describe('CioChallengerSection', () => {
  it('renders all seven operational decisions with accessible table semantics', () => {
    renderSection(<CioChallengerSection />);

    const table = screen.getByRole('table', { name: /operational decisions/i });
    expect(within(table).getAllByRole('row')).toHaveLength(CIO_DECISIONS.length + 1);
    expect(within(table).getAllByRole('columnheader')).toHaveLength(3);
    expect(within(table).getAllByTestId('cio-decision-row')).toHaveLength(7);
  });
});

describe('HospitalsSection', () => {
  it('renders exactly three synthetic hospitals and seven agent roster items', () => {
    renderSection(<HospitalsSection />);

    expect(
      screen.getByRole('region', { name: 'Synthetic Curavias hospital network' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('region', { name: 'Seven-agent capacity team' }),
    ).toBeInTheDocument();
    expect(screen.getAllByTestId('frontier-hospital-card')).toHaveLength(
      FRONTIER_HOSPITALS.length,
    );
    expect(screen.getAllByTestId('frontier-agent-roster-item')).toHaveLength(
      FRONTIER_AGENTS.length,
    );
    expect(screen.getByRole('heading', { name: 'CuraNova' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Curalp' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Vialta' })).toBeInTheDocument();
  });
});

describe('NinetyDaySection', () => {
  it('renders the three roadmap phases in blueprint order', () => {
    renderSection(<NinetyDaySection />);

    const phases = screen.getAllByTestId('ninety-day-phase');
    expect(phases).toHaveLength(NINETY_DAY_PHASES.length);
    expect(phases.map((phase) => within(phase).getByRole('heading').textContent)).toEqual([
      'Frame & Ground',
      'Build & Prove',
      'Operate & Scale',
    ]);
    phases.forEach((phase) => expect(phase).toHaveTextContent(/illustrative ROM/i));
  });
});

describe('StartView static narrative integration', () => {
  it('replaces all four static placeholders without duplicating section wrappers', () => {
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

    const expectedOrder = [
      'start-hero',
      'start-work-chart',
      'start-cio-why-now',
      'start-hospitals',
      'start-patient-path',
      'start-ninety-day',
      'start-bva',
    ];
    const wrappers = Array.from(
      screen.getByTestId('start-view').querySelectorAll<HTMLElement>(
        'section[data-testid^="start-"]',
      ),
    );

    expect(wrappers.map((wrapper) => wrapper.dataset.testid)).toEqual(expectedOrder);
    ['work-chart', 'cio-why-now', 'hospitals', 'ninety-day'].forEach((id) => {
      const sectionWrappers = screen.getAllByTestId(`start-${id}`);
      expect(sectionWrappers).toHaveLength(1);
      expect(within(sectionWrappers[0]).queryByText('Narrative section')).not.toBeInTheDocument();
      expect(
        within(sectionWrappers[0]).queryByText(/narrative copy and visuals land/i),
      ).not.toBeInTheDocument();
    });
  });
});
