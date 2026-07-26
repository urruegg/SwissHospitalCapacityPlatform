import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act, fireEvent } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { OrCaseScheduleTable } from '../../src/workspaces/main/boards/or-steering/OrCaseScheduleTable';
import { OR_STEERING_PINNED } from '../../src/data/roleboard/or-steering-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderTable(onSelectCase = vi.fn()) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={onSelectCase} />
    </FluentProvider>,
  );
}

describe('OrCaseScheduleTable', () => {
  it('renders every elective case by its unique case number', () => {
    renderTable();
    for (const c of OR_STEERING_PINNED.cases) {
      expect(screen.getByText(c.caseNo)).toBeInTheDocument();
    }
  });

  it('renders the per-case action badge (DEFER / RESLOT / REDIRECT / PROCEED)', () => {
    renderTable();
    expect(screen.getAllByText('DEFER').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('RESLOT').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('REDIRECT')).toBeInTheDocument();
    expect(screen.getAllByText('PROCEED').length).toBeGreaterThanOrEqual(1);
  });

  it('flags the post-op ward on every case row', () => {
    renderTable();
    expect(screen.getAllByText('Medicine A').length).toBeGreaterThanOrEqual(OR_STEERING_PINNED.cases.length);
  });

  it('fires onSelectCase with the correct case when a row is clicked (by case number)', () => {
    const onSelectCase = vi.fn();
    renderTable(onSelectCase);
    const firstCase = OR_STEERING_PINNED.cases[0]; // OR-3301 / ortho-knee-tue
    act(() => screen.getByRole('button', { name: /OR-3301/i }).click());
    expect(onSelectCase).toHaveBeenCalledWith(firstCase);
  });

  it('renders a row with role=button for every case', () => {
    renderTable();
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBeGreaterThanOrEqual(OR_STEERING_PINNED.cases.length);
  });

  it('calls onSelectCase with the correct General surgery case when that row is clicked', () => {
    const onSelectCase = vi.fn();
    renderTable(onSelectCase);
    const herniaCase = OR_STEERING_PINNED.cases.find((c) => c.id === 'gen-hernia-tue')!; // OR-3302
    act(() => screen.getByRole('button', { name: /OR-3302/i }).click());
    expect(onSelectCase).toHaveBeenCalledWith(herniaCase);
  });

  it('fires onSelectCase and prevents default on Space (no page scroll)', () => {
    const onSelectCase = vi.fn();
    renderTable(onSelectCase);
    const row = screen.getByRole('button', { name: /OR-3301/i });
    const notPrevented = fireEvent.keyDown(row, { key: ' ' });
    expect(notPrevented).toBe(false);
    expect(onSelectCase).toHaveBeenCalledWith(OR_STEERING_PINNED.cases[0]);
  });
});
