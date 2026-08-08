import '../../../i18n';
import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { HospitalsSection } from './HospitalsSection';

beforeEach(async () => {
  await i18n.changeLanguage('en');
});

function renderHospitals() {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <HospitalsSection />
      </FluentProvider>
    </MemoryRouter>,
  );
}

describe('HospitalsSection', () => {
  it('renders each hospital with a Fluent glyph icon and full name + profile', () => {
    renderHospitals();

    const glyphs = screen.getAllByTestId('frontier-hospital-glyph');
    expect(glyphs).toHaveLength(3);
    glyphs.forEach((glyph) => expect(glyph.querySelector('svg')).toBeTruthy());

    expect(screen.getByText('Uniklinik CuraNova')).toBeInTheDocument();
    expect(screen.getByText('Kantonsspital Curalp')).toBeInTheDocument();
    expect(screen.getByText('Spital Vialta')).toBeInTheDocument();

    expect(screen.getByText(/University central hospital · Canton Zurich/)).toBeInTheDocument();
    expect(screen.getByText(/Cantonal multi-site group · Canton Luzern/)).toBeInTheDocument();
    expect(screen.getByText(/Regional acute.*Canton Zurich/)).toBeInTheDocument();
  });

  it('renders four role rows per hospital (bed side, ops side, agents, product owner)', () => {
    renderHospitals();

    expect(screen.getAllByTestId('frontier-hospital-role')).toHaveLength(12);

    // Hospital-specific human roles.
    expect(screen.getByText(/Head of Nursing/)).toBeInTheDocument();
    expect(screen.getByText(/Physicians & OR/)).toBeInTheDocument();
    expect(screen.getByText(/Medical & OR leads/)).toBeInTheDocument();

    // Shared agent + product-owner rows appear on all three cards.
    expect(screen.getAllByText(/HCC Operation \+ Patient Flow/)).toHaveLength(3);
    expect(screen.getAllByText(/answers the hard questions/)).toHaveLength(3);
  });

  it('drops the per-card synthetic badge and focus caption (moved to the section lead)', () => {
    renderHospitals();

    expect(screen.queryByText(/Synthetic profile/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/^Focus:/)).not.toBeInTheDocument();

    // Facts metarow is retained.
    expect(screen.getAllByTestId('frontier-hospital-facts')).toHaveLength(3);
    expect(screen.getByText(/7 medical centres/)).toBeInTheDocument();
  });

  it('renders the eight-chip agent roster (seven runtime agents + the PO Agent) with icons', () => {
    renderHospitals();

    const chips = screen.getAllByTestId('frontier-agent-roster-item');
    expect(chips).toHaveLength(8);
    chips.forEach((chip) => expect(chip.querySelector('svg')).toBeTruthy());

    // Section heading + "runtime agents" live tag.
    expect(
      screen.getByRole('heading', { name: 'The agent team behind every hospital' }),
    ).toBeInTheDocument();
    expect(screen.getByText(/7 runtime agents/)).toBeInTheDocument();

    // Abbreviations, including the new Product Owner Agent chip.
    expect(screen.getByText('OOA')).toBeInTheDocument();
    expect(screen.getByText('BMCA')).toBeInTheDocument();
    expect(screen.getByText('PO Agent')).toBeInTheDocument();

    // Short descriptions.
    expect(screen.getByText(/Occupancy & 72-h forecast/)).toBeInTheDocument();
    expect(screen.getByText(/grounded Q&A rail/)).toBeInTheDocument();

    // Advisory / no-PHI footer note.
    expect(screen.getByText(/advisory and human-in-the-loop/)).toBeInTheDocument();
  });
});
