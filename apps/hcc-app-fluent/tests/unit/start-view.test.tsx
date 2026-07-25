import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { ModeProvider } from '../../src/context/mode-context';
import { RoleProvider } from '../../src/context/role-context';
import { StartView } from '../../src/workspaces/start/StartView';
import { LAUNCHER_TILES } from '../../src/workspaces/start/role-launcher';
import { bvaHeadlineKpis } from '../../src/data/bva/bva-evidence';

// Mock loadSiteCapacitySummary so the capacity teaser renders synchronously in tests.
vi.mock('../../src/data/roleboard/golden-source-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../src/data/roleboard/golden-source-client')>();
  return {
    ...actual,
    loadSiteCapacitySummary: vi.fn().mockResolvedValue({
      peakWard: 'Medicine A',
      peakPct: 102,
      siteGapBeds: -16,
      breachEtaHours: 54,
      firstSurfacedBy: 'ooa-agent' as const,
      provenance: 'simulated' as const,
      asOf: '2026-07-23T20:00:00.000Z',
    }),
  };
});

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

  // --- New sections (Sprint 20 M5 parity) ---

  describe('capacity teaser', () => {
    it('renders the capacity teaser section', () => {
      renderStart();
      expect(screen.getByTestId('start-capacity-teaser')).toBeInTheDocument();
    });

    it('renders live/simulated provenance badge after async load', async () => {
      renderStart();
      await waitFor(() => {
        expect(screen.getByTestId('start-capacity-provenance-badge')).toBeInTheDocument();
      });
      expect(screen.getByTestId('start-capacity-provenance-badge')).toHaveTextContent(/simulated/i);
    });

    it('displays peak ward and pct from the loaded summary (not hardcoded)', async () => {
      renderStart();
      await waitFor(() => {
        expect(screen.getByTestId('start-capacity-teaser')).toHaveTextContent(/Medicine A/);
      });
      expect(screen.getByTestId('start-capacity-teaser')).toHaveTextContent(/102/);
    });
  });

  describe('value tiles', () => {
    it('renders the value tiles section', () => {
      renderStart();
      expect(screen.getByTestId('start-value-tiles')).toBeInTheDocument();
    });

    it('renders one tile per bvaHeadlineKpi entry (no inline literals)', () => {
      renderStart();
      // Every kpi measure label should appear
      for (const kpi of bvaHeadlineKpis) {
        expect(screen.getByText(kpi.measure)).toBeInTheDocument();
      }
    });

    it('shows the ROM estimate label on each value tile', () => {
      renderStart();
      const romLabels = screen.getAllByText(/ROM estimate/i);
      expect(romLabels.length).toBeGreaterThanOrEqual(bvaHeadlineKpis.length);
    });

    it('shows the BVA asOf date on each value tile (NFR-GOV-006 provenance)', () => {
      renderStart();
      const section = screen.getByTestId('start-value-tiles');
      // bvaHeadlineKpis all share asOf '2026-06-30T…'; the sliced date fragment must appear
      expect(section).toHaveTextContent(bvaHeadlineKpis[0].asOf.slice(0, 10));
    });
  });

  describe('copilot count tile', () => {
    it('renders the copilot count tile', () => {
      renderStart();
      expect(screen.getByTestId('start-copilot-count')).toBeInTheDocument();
    });

    it('shows LAUNCHER_TILES.length as the copilot count (registry-derived)', () => {
      renderStart();
      const tile = screen.getByTestId('start-copilot-count');
      expect(tile).toHaveTextContent(String(LAUNCHER_TILES.length));
    });
  });

  describe('why-now table', () => {
    it('renders the why-now table section', () => {
      renderStart();
      expect(screen.getByTestId('start-why-now')).toBeInTheDocument();
    });

    it('shows the editorial disclaimer caption', () => {
      renderStart();
      const section = screen.getByTestId('start-why-now');
      expect(section).toHaveTextContent(/illustrative/i);
    });

    it('has Today and With Curavias column headers', () => {
      renderStart();
      expect(screen.getByText(/Today/i)).toBeInTheDocument();
      expect(screen.getByText(/With Curavias/i)).toBeInTheDocument();
    });
  });

  describe('patient-path strip', () => {
    it('renders the patient-path section', () => {
      renderStart();
      expect(screen.getByTestId('start-patient-path')).toBeInTheDocument();
    });

    it('shows illustrative PHI disclaimer in the caption', () => {
      renderStart();
      const section = screen.getByTestId('start-patient-path');
      expect(section).toHaveTextContent(/illustrative/i);
    });

    it('shows the live capacity note in the treatment node after load', async () => {
      renderStart();
      // The treatment step showCapacity=true — Medicine A from the mocked summary
      await waitFor(() => {
        expect(screen.getByTestId('start-patient-path')).toHaveTextContent(/Medicine A/);
      });
    });
  });
});

