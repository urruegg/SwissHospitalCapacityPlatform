import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { PlacementBarriersBoard } from '../../src/workspaces/main/boards/bed-manager/PlacementBarriersBoard';
import { BEDMANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('PlacementBarriersBoard', () => {
  it('renders barrier labels and bed-impact numbers', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementBarriersBoard
          barriers={BEDMANAGER_PINNED.barriers}
          onSelectBarrier={vi.fn()}
        />
      </FluentProvider>,
    );
    const sorted = [...BEDMANAGER_PINNED.barriers].sort((a, b) => b.bedImpact - a.bedImpact);
    expect(screen.getByText(sorted[0].name)).toBeInTheDocument();
    expect(screen.getByText(sorted[1].name)).toBeInTheDocument();
  });

  it('renders barriers sorted by bedImpact descending — highest impact appears first', () => {
    const reversed = [...BEDMANAGER_PINNED.barriers].reverse();
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementBarriersBoard
          barriers={reversed}
          onSelectBarrier={vi.fn()}
        />
      </FluentProvider>,
    );
    const sorted = [...BEDMANAGER_PINNED.barriers].sort((a, b) => b.bedImpact - a.bedImpact);
    const allText = document.body.textContent ?? '';
    const firstIdx = allText.indexOf(sorted[0].name);
    const secondIdx = allText.indexOf(sorted[1].name);
    expect(firstIdx).toBeGreaterThanOrEqual(0);
    expect(firstIdx).toBeLessThan(secondIdx);
  });

  it('fires onSelectBarrier with the correct barrier when a row is clicked', () => {
    const onSelectBarrier = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementBarriersBoard
          barriers={BEDMANAGER_PINNED.barriers}
          onSelectBarrier={onSelectBarrier}
        />
      </FluentProvider>,
    );
    const sorted = [...BEDMANAGER_PINNED.barriers].sort((a, b) => b.bedImpact - a.bedImpact);
    act(() => screen.getByRole('button', { name: sorted[0].name }).click());
    expect(onSelectBarrier).toHaveBeenCalledWith(sorted[0]);
  });

  it('renders the auto-sequence CTA button', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementBarriersBoard
          barriers={BEDMANAGER_PINNED.barriers}
          onSelectBarrier={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getByRole('button', { name: /auto-sequence/i })).toBeInTheDocument();
  });

  it('fires onAutoSequence when the auto-sequence CTA button is clicked', () => {
    const onAutoSequence = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementBarriersBoard
          barriers={BEDMANAGER_PINNED.barriers}
          onSelectBarrier={vi.fn()}
          onAutoSequence={onAutoSequence}
        />
      </FluentProvider>,
    );
    act(() => screen.getByRole('button', { name: /auto-sequence/i }).click());
    expect(onAutoSequence).toHaveBeenCalledOnce();
  });
});
