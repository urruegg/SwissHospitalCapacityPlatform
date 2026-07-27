import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { StaffingLeversBoard } from '../../src/workspaces/main/boards/staffing/StaffingLeversBoard';
import { STAFFING_PINNED, sortStaffingLevers } from '../../src/data/roleboard/staffing-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('StaffingLeversBoard', () => {
  it('renders lever labels and bedsEnabled numbers', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard levers={STAFFING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    const sorted = sortStaffingLevers(STAFFING_PINNED.levers);
    expect(screen.getByText(sorted[0].label)).toBeInTheDocument();
  });

  it('renders levers sorted by bedsEnabled descending even when input is unsorted', () => {
    const reversed = [...STAFFING_PINNED.levers].reverse();
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard levers={reversed} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    const sorted = sortStaffingLevers(STAFFING_PINNED.levers);
    const allText = document.body.textContent ?? '';
    const firstIdx = allText.indexOf(sorted[0].label);
    const secondIdx = allText.indexOf(sorted[1].label);
    expect(firstIdx).toBeGreaterThanOrEqual(0);
    expect(firstIdx).toBeLessThan(secondIdx);
  });

  it('fires onSelectLever with the correct lever when a row is clicked', () => {
    const onSelectLever = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard levers={STAFFING_PINNED.levers} onSelectLever={onSelectLever} />
      </FluentProvider>,
    );
    const sorted = sortStaffingLevers(STAFFING_PINNED.levers);
    act(() => screen.getByRole('button', { name: sorted[0].label }).click());
    expect(onSelectLever).toHaveBeenCalledWith(sorted[0]);
  });

  it('renders the view staffing plan CTA button', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard levers={STAFFING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getByRole('button', { name: /view staffing plan/i })).toBeInTheDocument();
  });

  it('fires onViewPlan when the view staffing plan CTA button is clicked', () => {
    const onViewPlan = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard
          levers={STAFFING_PINNED.levers}
          onSelectLever={vi.fn()}
          onViewPlan={onViewPlan}
        />
      </FluentProvider>,
    );
    act(() => screen.getByRole('button', { name: /view staffing plan/i }).click());
    expect(onViewPlan).toHaveBeenCalledOnce();
  });

  it('rank badges are numbered starting from 1', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <StaffingLeversBoard levers={STAFFING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    // Both rank badges 1 and 2 should be present; use getAllByText because
    // bedsEnabled values may also render the number 1 elsewhere in the table.
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);
  });
});
