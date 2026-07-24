import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { CoverageWorklistTable } from '../../src/workspaces/main/boards/staffing/CoverageWorklistTable';
import { STAFFING_PINNED } from '../../src/data/roleboard/staffing-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('CoverageWorklistTable', () => {
  it('renders all moves showing role, fromUnit, toUnit, and shiftGap', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={vi.fn()} />
      </FluentProvider>,
    );
    for (const m of STAFFING_PINNED.moves) {
      expect(screen.getByText(m.role)).toBeInTheDocument();
      expect(screen.getByText(m.fromUnit)).toBeInTheDocument();
      expect(screen.getByText(m.toUnit)).toBeInTheDocument();
      expect(screen.getByText(m.shiftGap)).toBeInTheDocument();
    }
  });

  it('fires onSelectMove with the correct move when a row is clicked', () => {
    const onSelectMove = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={onSelectMove} />
      </FluentProvider>,
    );
    const firstMove = STAFFING_PINNED.moves[0]; // rn-icu-to-meda
    act(() =>
      screen.getByRole('button', { name: /Shift RN ICU float -> Medicine A/i }).click(),
    );
    expect(onSelectMove).toHaveBeenCalledWith(firstMove);
  });

  it('fires onSelectMove with the HCA move when that row is clicked', () => {
    const onSelectMove = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={onSelectMove} />
      </FluentProvider>,
    );
    const hcaMove = STAFFING_PINNED.moves.find((m) => m.id === 'hca-surg-to-medb')!;
    act(() =>
      screen.getByRole('button', { name: /Shift HCA Surgery B -> Medicine B/i }).click(),
    );
    expect(onSelectMove).toHaveBeenCalledWith(hcaMove);
  });

  it('renders a row with role=button for every move', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={vi.fn()} />
      </FluentProvider>,
    );
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBeGreaterThanOrEqual(STAFFING_PINNED.moves.length);
  });

  it('renders the column headers from i18n keys', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <CoverageWorklistTable moves={STAFFING_PINNED.moves} onSelectMove={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getByText('Role')).toBeInTheDocument();
    expect(screen.getByText('From unit')).toBeInTheDocument();
    expect(screen.getByText('To unit')).toBeInTheDocument();
  });
});
