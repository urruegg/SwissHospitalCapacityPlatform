import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { DischargeBarriersBoard } from '../../src/workspaces/main/boards/discharge/DischargeBarriersBoard';
import { DISCHARGE_PINNED, sortCapacityBarriers } from '../../src/data/roleboard/discharge-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderBoard(props: Partial<React.ComponentProps<typeof DischargeBarriersBoard>> = {}) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <DischargeBarriersBoard
        barriers={DISCHARGE_PINNED.barriers}
        onSelectBarrier={vi.fn()}
        {...props}
      />
    </FluentProvider>,
  );
}

describe('DischargeBarriersBoard', () => {
  it('renders barrier names ranked by bed impact', () => {
    renderBoard();
    const sorted = sortCapacityBarriers(DISCHARGE_PINNED.barriers);
    expect(screen.getByText(sorted[0].name)).toBeInTheDocument();
  });

  it('renders barriers sorted by bedImpact descending even when input is unsorted', () => {
    const reversed = [...DISCHARGE_PINNED.barriers].reverse();
    renderBoard({ barriers: reversed });
    const sorted = sortCapacityBarriers(DISCHARGE_PINNED.barriers);
    const allText = document.body.textContent ?? '';
    const firstIdx = allText.indexOf(sorted[0].name);
    const secondIdx = allText.indexOf(sorted[1].name);
    expect(firstIdx).toBeGreaterThanOrEqual(0);
    expect(firstIdx).toBeLessThan(secondIdx);
  });

  it('fires onSelectBarrier with the correct barrier when a row is clicked', () => {
    const onSelectBarrier = vi.fn();
    renderBoard({ onSelectBarrier });
    const sorted = sortCapacityBarriers(DISCHARGE_PINNED.barriers);
    act(() => screen.getByRole('button', { name: sorted[0].name }).click());
    expect(onSelectBarrier).toHaveBeenCalledWith(sorted[0]);
  });

  it('renders the view coordinated plan CTA button', () => {
    renderBoard();
    expect(screen.getByRole('button', { name: /view coordinated plan/i })).toBeInTheDocument();
  });

  it('fires onViewPlan when the view coordinated plan CTA button is clicked', () => {
    const onViewPlan = vi.fn();
    renderBoard({ onViewPlan });
    act(() => screen.getByRole('button', { name: /view coordinated plan/i }).click());
    expect(onViewPlan).toHaveBeenCalledOnce();
  });

  it('renders rank badges numbered from 1', () => {
    renderBoard();
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);
  });
});
