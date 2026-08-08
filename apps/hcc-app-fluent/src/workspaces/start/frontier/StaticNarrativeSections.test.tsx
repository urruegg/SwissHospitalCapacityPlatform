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
  FRONTIER_ROSTER,
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
    expect(
      modes.map((mode) => within(mode).getByTestId('work-chart-mode-title').textContent),
    ).toEqual(['Humans', 'Agents', 'On-demand intelligence']);
    modes.forEach((mode) => expect(within(mode).getByRole('button')).toBeInTheDocument());
  });

  it('renders the Frontier Firm fit table with all four principle rows', () => {
    renderSection(<WorkChartSection />);

    const table = screen.getByRole('table', { name: /how curavias fits/i });
    expect(within(table).getAllByRole('columnheader')).toHaveLength(2);
    expect(within(table).getAllByTestId('work-chart-fit-row')).toHaveLength(4);
    expect(
      within(table).getByText('7 runtime agents + operational staff'),
    ).toBeInTheDocument();
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
  it('renders exactly three synthetic hospitals and the eight-chip agent roster', () => {
    renderSection(<HospitalsSection />);

    expect(
      screen.getByRole('region', { name: 'Synthetic Curavias hospital network' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('region', { name: 'The agent team behind every hospital' }),
    ).toBeInTheDocument();
    expect(screen.getAllByTestId('frontier-hospital-card')).toHaveLength(
      FRONTIER_HOSPITALS.length,
    );
    expect(screen.getAllByTestId('frontier-agent-roster-item')).toHaveLength(
      FRONTIER_ROSTER.length,
    );
    // Hospital titles render as plain spans (not headings) because each card is
    // an interactive <button> — button content model disallows heading descendants.
    expect(screen.getByText('Uniklinik CuraNova')).toBeInTheDocument();
    expect(screen.getByText('Kantonsspital Curalp')).toBeInTheDocument();
    expect(screen.getByText('Spital Vialta')).toBeInTheDocument();
    // Synthetic aggregate hard-facts row (mockup `.metarow`) renders per hospital.
    expect(screen.getAllByTestId('frontier-hospital-facts')).toHaveLength(
      FRONTIER_HOSPITALS.length,
    );
    expect(screen.getByText(/7 medical centres/)).toBeInTheDocument();
  });

  it('renders up to four real service badges per hospital under the ops-side role', () => {
    renderSection(<HospitalsSection />);

    const cards = screen.getAllByTestId('frontier-hospital-card');
    const serviceRows = screen.getAllByTestId('frontier-hospital-services');
    // One service row per hospital card.
    expect(serviceRows).toHaveLength(cards.length);

    serviceRows.forEach((row) => {
      const chips = within(row).getAllByTestId('frontier-hospital-service');
      // Capped at four real services per synthetic hospital.
      expect(chips.length).toBeGreaterThanOrEqual(1);
      expect(chips.length).toBeLessThanOrEqual(4);
    });

    // Real, place-stripped services from the capacity master data render as chips.
    expect(screen.getByText('Comprehensive Cancer Center')).toBeInTheDocument();
    expect(screen.getByText('University Heart Centre')).toBeInTheDocument();
    expect(screen.getByText('Tumour Centre')).toBeInTheDocument();
    // Vialta (regional acute) shows its four real service centres.
    const vialtaServices = within(cards[2]).getAllByTestId('frontier-hospital-service');
    expect(vialtaServices).toHaveLength(4);
    expect(within(cards[2]).getByText('Interdisciplinary Emergency Centre')).toBeInTheDocument();
  });
});

describe('NinetyDaySection', () => {
  it('renders the three roadmap phases in blueprint order', () => {
    renderSection(<NinetyDaySection />);

    const phases = screen.getAllByTestId('ninety-day-phase');
    expect(phases).toHaveLength(NINETY_DAY_PHASES.length);
    // Phase titles render as plain spans (not headings) because each phase card is
    // an interactive <button> — button content model disallows heading descendants.
    expect(phases.map((phase) => within(phase).getByRole('button').textContent)).toEqual([
      expect.stringContaining('Frame & Ground'),
      expect.stringContaining('Build & Prove'),
      expect.stringContaining('Operate & Scale'),
    ]);
    phases.forEach((phase) => expect(phase).not.toHaveTextContent(/illustrative ROM/i));
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
      'start-challenger',
      'start-vision',
      'start-work-chart',
      'start-hospitals',
      'start-patient-path',
    ];
    const wrappers = Array.from(
      screen.getByTestId('start-view').querySelectorAll<HTMLElement>(
        'section[data-testid^="start-"]',
      ),
    );

    expect(wrappers.map((wrapper) => wrapper.dataset.testid)).toEqual(expectedOrder);
    ['work-chart', 'hospitals'].forEach((id) => {
      const sectionWrappers = screen.getAllByTestId(`start-${id}`);
      expect(sectionWrappers).toHaveLength(1);
      expect(within(sectionWrappers[0]).queryByText('Narrative section')).not.toBeInTheDocument();
      expect(
        within(sectionWrappers[0]).queryByText(/narrative copy and visuals land/i),
      ).not.toBeInTheDocument();
    });

    // Sprint 40 — the Operating Model story is split into two sections: the "Model"
    // section (start-work-chart) holds the work-chart block + Frontier Firm fit table,
    // and the "Organisation" section (start-hospitals) holds the three hospital cards +
    // eight-chip agent roster. The two must not collapse back into one.
    const modelSection = screen.getByTestId('start-work-chart');
    expect(within(modelSection).queryByTestId('frontier-hospital-card')).not.toBeInTheDocument();
    const organisationSection = screen.getByTestId('start-hospitals');
    expect(within(organisationSection).getAllByTestId('frontier-hospital-card')).toHaveLength(3);
    expect(
      within(organisationSection).getAllByTestId('frontier-agent-roster-item'),
    ).toHaveLength(8);
  });

  it('does not force full-height on ordinary Start sections', () => {
    renderSection(
      <RoleProvider testRoles={['HCC.PlatformAdmin']} testHomeSite="usz">
        <ModeProvider>
          <StartView />
        </ModeProvider>
      </RoleProvider>,
    );
    const hospitals = screen.getByTestId('start-hospitals');
    // The opt-in flag is observable via data-full; ordinary sections must not set it.
    expect(hospitals.closest('[data-full="true"]')).toBeNull();
    expect(hospitals.closest('[data-testid="widget-hospitals"]')).not.toHaveStyle({
      minHeight: 'calc(100vh - 150px)',
    });
  });

  it('colour-codes the work-chart accent clause within a single heading', () => {
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

    const heading = screen.getByRole('heading', {
      name: /From the org chart to the\s*work chart/i,
    });
    expect(within(heading).getByText('work chart').getAttribute('data-tone')).toBe('accent');
  });

  it('renders the mockup patient-journey eyebrow and colour-coded title', () => {
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

    // Sprint 40 change 4 — the patient-journey section adopts the mockup copy. The
    // eyebrow is the semantic kicker "Patient journey" (the mockup's "Key visual 2 ·"
    // prefix is dropped, matching the Model / Organisation / Why Curavias exists pattern).
    expect(screen.getByText('Patient journey')).toBeInTheDocument();
    // The mockup h2, with its trailing clause colour-coded within a single heading node.
    const heading = screen.getByRole('heading', {
      name: /One patient, one flow.*humans and agents together/i,
    });
    expect(
      within(heading).getByText('humans and agents together').getAttribute('data-tone'),
    ).toBe('accent');
  });

  it('localises the section nav tab labels (de) instead of hard-coded English', async () => {
    await i18n.changeLanguage('de');
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

    expect(screen.getByTestId('start-nav-hero')).toHaveTextContent('Bühne');
    expect(screen.getByTestId('start-nav-challenger')).toHaveTextContent('Herausforderer');
    expect(screen.getByTestId('start-nav-vision')).toHaveTextContent('Warum Curavias');
    expect(screen.getByTestId('start-nav-work-chart')).toHaveTextContent('Modell');
    expect(screen.getByTestId('start-nav-hospitals')).toHaveTextContent('Organisation');
    expect(screen.getByTestId('start-nav-patient-path')).toHaveTextContent('Versorgungspfad');
    // Regression guard: BVA moved to Backstage (changes 1-9) — it must not surface as a Start nav tab.
    expect(screen.queryByTestId('start-nav-bva')).toBeNull();
    // Regression guard: the German tab strip must not fall back to English labels.
    expect(screen.getByTestId('start-nav-work-chart')).not.toHaveTextContent('Operating model');
  });
});
