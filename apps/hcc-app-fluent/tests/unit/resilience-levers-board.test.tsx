import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { ResilienceLeversBoard } from '../../src/workspaces/main/boards/crisis/ResilienceLeversBoard';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderBoard(props: Partial<React.ComponentProps<typeof ResilienceLeversBoard>> = {}) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <ResilienceLeversBoard
        levers={CRISIS_PINNED.resilienceLevers}
        onSelectLever={vi.fn()}
        summary={CRISIS_PINNED.resilienceSummary}
        absorbed={CRISIS_PINNED.absorbed}
        {...props}
      />
    </FluentProvider>,
  );
}

describe('ResilienceLeversBoard', () => {
  it('renders every lever label (curated SPOF-first order)', () => {
    renderBoard();
    expect(screen.getByText('Pre-stage oncology backup')).toBeInTheDocument();
    expect(screen.getByText('Site command escalation')).toBeInTheDocument();
  });

  it('renders the THE SPOF badge on the SPOF lever', () => {
    renderBoard();
    expect(screen.getByText('THE SPOF')).toBeInTheDocument();
  });

  it('renders the view resilience plan CTA and fires onViewPlan when clicked', () => {
    const onViewPlan = vi.fn();
    renderBoard({ onViewPlan });
    act(() => screen.getByRole('button', { name: /view resilience plan/i }).click());
    expect(onViewPlan).toHaveBeenCalledOnce();
  });

  it('fires onSelectLever when a lever row is clicked', () => {
    const onSelectLever = vi.fn();
    renderBoard({ onSelectLever });
    act(() => screen.getByRole('button', { name: 'Pre-stage oncology backup' }).click());
    expect(onSelectLever).toHaveBeenCalledTimes(1);
    expect((onSelectLever.mock.calls[0][0] as { id: string }).id).toBe('pre-stage-oncology');
  });

  it('renders the absorbed-shocks summary footer', () => {
    renderBoard();
    expect(screen.getByText(/5 \/ 6 internally/)).toBeInTheDocument();
  });
});
