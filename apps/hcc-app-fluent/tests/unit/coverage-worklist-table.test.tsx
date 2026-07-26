import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { CoverageWorklistTable } from '../../src/workspaces/main/boards/staffing/CoverageWorklistTable';
import { STAFFING_PINNED } from '../../src/data/roleboard/staffing-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderTable(onSelectMove = vi.fn()) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={onSelectMove} />
    </FluentProvider>,
  );
}

describe('CoverageWorklistTable', () => {
  it('renders every shift by its unique shift number', () => {
    renderTable();
    for (const m of STAFFING_PINNED.moves) {
      expect(screen.getByText(m.shiftNo)).toBeInTheDocument();
    }
  });

  it('renders the per-shift status badge (GAP / FILLED / PENDING / WATCH)', () => {
    renderTable();
    expect(screen.getByText('GAP')).toBeInTheDocument();
    expect(screen.getAllByText('FILLED').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('PENDING')).toBeInTheDocument();
    expect(screen.getByText('WATCH')).toBeInTheDocument();
  });

  it('fires onSelectMove with the RN surge move when that row is clicked', () => {
    const onSelectMove = vi.fn();
    renderTable(onSelectMove);
    const rnMove = STAFFING_PINNED.moves.find((m) => m.id === 'rn-icu-to-meda')!;
    act(() => screen.getByRole('button', { name: /Shift RN ICU float -> Medicine A/i }).click());
    expect(onSelectMove).toHaveBeenCalledWith(rnMove);
  });

  it('fires onSelectMove with the HCA move when that row is clicked', () => {
    const onSelectMove = vi.fn();
    renderTable(onSelectMove);
    const hcaMove = STAFFING_PINNED.moves.find((m) => m.id === 'hca-surg-to-medb')!;
    act(() => screen.getByRole('button', { name: /Shift HCA Surgery B -> Medicine B/i }).click());
    expect(onSelectMove).toHaveBeenCalledWith(hcaMove);
  });

  it('renders a row with role=button for every shift', () => {
    renderTable();
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBeGreaterThanOrEqual(STAFFING_PINNED.moves.length);
  });

  it('renders the new column headers from i18n keys', () => {
    renderTable();
    expect(screen.getByText('Shift')).toBeInTheDocument();
    expect(screen.getByText('From unit')).toBeInTheDocument();
    expect(screen.getByText('To unit')).toBeInTheDocument();
    expect(screen.getByText('Skill')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });
});
