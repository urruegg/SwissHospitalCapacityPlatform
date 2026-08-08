import '../../../i18n';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import {
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaProofPoints,
  bvaSensitivityScenarios,
  bvaTrend,
  bvaValueLevers,
} from '../../../data/bva/bva-evidence';
import * as goldenSourceClient from '../../../data/roleboard/golden-source-client';
import { CopilotRailProvider, useCopilotRail } from '../../../copilot-rail/rail-context';
import { RoleProvider } from '../../../context/role-context';
import { StartView } from '../StartView';
import { BvaDecisionSection } from './BvaDecisionSection';

function formatHeadlineValue(value: { value: string; unit?: string }) {
  return value.unit ? `${value.value} ${value.unit}` : value.value;
}

function formatCurrency(amount: number, currency: string) {
  return `${currency} ${new Intl.NumberFormat('de-CH', { maximumFractionDigits: 0 }).format(amount)}`;
}

function formatVariance(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
}

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

function renderSection(ui: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <RoleProvider testRoles={['HCC.PlatformAdmin']} testHomeSite="usz">
          <CopilotRailProvider>
            {ui}
            <RailProbe />
          </CopilotRailProvider>
        </RoleProvider>
      </FluentProvider>
    </MemoryRouter>,
  );
}

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(async () => {
  await i18n.changeLanguage('en');
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('BvaDecisionSection', () => {
  it('binds the KPI tiles to bvaHeadlineKpis only (not trend/sensitivity data)', () => {
    renderSection(<BvaDecisionSection />);

    const section = screen.getByTestId('bva-decision-section');
    const kpiGrid = within(section).getByTestId('bva-kpi-grid');
    const figures = within(kpiGrid).getAllByTestId('bva-kpi-figure').map((node) => node.textContent?.trim());

    // Exactly the headline KPIs — no trend point / sensitivity scenario mixed in as a "KPI tile".
    expect(figures).toEqual(bvaHeadlineKpis.map((payload) => formatHeadlineValue(payload)));

    const romCaptions = within(section).getAllByTestId('bva-rom-caption').map((node) => node.textContent?.trim());
    expect(romCaptions).toContain(
      `ROM estimate · ${bvaHeadlineKpis[0].source} · as of ${bvaHeadlineKpis[0].asOf.slice(0, 10)}`,
    );
    expect(romCaptions).toContain(
      `ROM estimate · ${bvaPlanVsActual.source} · as of ${bvaPlanVsActual.asOf.slice(0, 10)}`,
    );
  });

  it('binds the TCO table to bvaPlanVsActual', () => {
    renderSection(<BvaDecisionSection />);
    const section = screen.getByTestId('bva-decision-section');

    const tcoTable = within(section).getByTestId('bva-tco-table');
    expect(within(tcoTable).getByText(bvaPlanVsActual.measure)).toBeInTheDocument();
    expect(within(tcoTable).getByText(formatCurrency(bvaPlanVsActual.plan, bvaPlanVsActual.currency))).toBeInTheDocument();
    expect(within(tcoTable).getByText(formatCurrency(bvaPlanVsActual.actual, bvaPlanVsActual.currency))).toBeInTheDocument();
    expect(within(tcoTable).getByText(formatVariance(bvaPlanVsActual.variancePct))).toBeInTheDocument();
  });

  it('binds the value-levers table to bvaValueLevers only (not bvaHeadlineKpis)', () => {
    renderSection(<BvaDecisionSection />);
    const section = screen.getByTestId('bva-decision-section');

    const leversTable = within(section).getByTestId('bva-value-levers-table');
    bvaValueLevers.forEach((payload) => {
      expect(within(leversTable).getByText(payload.lever)).toBeInTheDocument();
      expect(within(leversTable).getByText(formatCurrency(payload.annualBenefit, payload.currency))).toBeInTheDocument();
      expect(within(leversTable).getByText(payload.valueLogic)).toBeInTheDocument();
    });

    // Regression guard: headline KPI measures must not appear inside the levers table
    // (that was the Sprint 37 review failure — rebranding headline KPIs as "value levers").
    bvaHeadlineKpis.forEach((payload) => {
      expect(within(leversTable).queryByText(payload.measure)).not.toBeInTheDocument();
    });
  });

  it('binds the sensitivity pills/cards to bvaSensitivityScenarios only (not bvaTrend.points)', () => {
    renderSection(<BvaDecisionSection />);
    const section = screen.getByTestId('bva-decision-section');

    const controls = within(section).getByTestId('bva-sensitivity-controls');
    bvaSensitivityScenarios.forEach((scenario) => {
      expect(within(controls).getByRole('button', { name: scenario.scenario })).toBeInTheDocument();
    });

    // Regression guard: trend month labels must not appear as sensitivity pills
    // (that was the Sprint 37 review failure — rebranding trend points as "sensitivity scenarios").
    bvaTrend.points.forEach((point) => {
      expect(within(controls).queryByRole('button', { name: point.label })).not.toBeInTheDocument();
    });

    const conservative = bvaSensitivityScenarios.find((s) => s.scenario === 'Conservative')!;
    fireEvent.click(within(controls).getByRole('button', { name: conservative.scenario }));

    const value = screen.getByTestId('bva-sensitivity-value');
    expect(value.textContent).toContain(formatCurrency(conservative.annualBenefit, conservative.currency));
    expect(value.textContent).toContain(formatCurrency(conservative.threeYearTco, conservative.currency));
    expect(value.textContent).toContain(`${conservative.threeYearRoiPct}%`);
    expect(screen.getByText(conservative.comment)).toBeInTheDocument();
  });

  it('renders distinct proof/evidence entries (trend + bvaProofPoints), not a duplicate of KPI/TCO figures', () => {
    renderSection(<BvaDecisionSection />);
    const section = screen.getByTestId('bva-decision-section');

    const evidenceList = within(section).getByTestId('bva-proof-list');

    const latestTrendPoint = bvaTrend.points[bvaTrend.points.length - 1];
    expect(within(evidenceList).getByText(new RegExp(bvaTrend.measure, 'i'))).toBeInTheDocument();
    expect(within(evidenceList).getByText(new RegExp(latestTrendPoint.label, 'i'))).toBeInTheDocument();

    bvaProofPoints.forEach((payload) => {
      const claimNode = within(evidenceList).getByText(payload.claim);
      const item = claimNode.closest('li');
      expect(item).not.toBeNull();
      expect(within(item as HTMLElement).getByText(new RegExp(payload.target, 'i'))).toBeInTheDocument();
    });

    // Regression guard: proof list must not merely re-list headline KPI measures or the TCO measure.
    bvaHeadlineKpis.forEach((payload) => {
      expect(within(evidenceList).queryByText(payload.measure)).not.toBeInTheDocument();
    });
    expect(within(evidenceList).queryByText(bvaPlanVsActual.measure)).not.toBeInTheDocument();
  });

  it('keeps the decision card bound to headline KPIs, TCO, and the latest trend point; opens the Product Owner rail', () => {
    renderSection(<BvaDecisionSection />);

    expect(screen.getByTestId('rail-open')).toHaveTextContent('false');

    fireEvent.click(screen.getByTestId('bva-decision-cta'));

    expect(screen.getByTestId('rail-open')).toHaveTextContent('true');
    expect(screen.getByTestId('rail-read')).toHaveTextContent(bvaPlanVsActual.measure);
    expect(screen.getByTestId('rail-citations')).toHaveTextContent(bvaTrend.source);
    // Base ROM is the default selected scenario; its source must be cited once selected.
    const baseRom = bvaSensitivityScenarios.find((s) => s.scenario === 'Base ROM')!;
    expect(screen.getByTestId('rail-citations')).toHaveTextContent(baseRom.source);
  });
});

describe('StartView BVA integration', () => {
  it('replaces the BVA placeholder while preserving the approved section order and test ids', () => {
    vi.spyOn(goldenSourceClient, 'loadSiteCapacitySummary').mockImplementation(
      () => new Promise(() => {}),
    );

    renderSection(<StartView />);

    const sectionIds = Array.from(document.querySelectorAll('section[data-testid^="start-"]'))
      .map((node) => node.getAttribute('data-testid'))
      .filter((value): value is string => value !== null && value !== 'start-view');

    expect(sectionIds).toEqual([
      'start-hero',
      'start-challenger',
      'start-vision',
      'start-work-chart',
      'start-hospitals',
      'start-patient-path',
    ]);
  });
});
