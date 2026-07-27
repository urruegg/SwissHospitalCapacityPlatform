import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { TrustedSignalsPanel } from '../../src/workspaces/main/boards/crisis/TrustedSignalsPanel';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderPanel(props: Partial<React.ComponentProps<typeof TrustedSignalsPanel>> = {}) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <TrustedSignalsPanel
        boardSignals={CRISIS_PINNED.boardSignals}
        scenarios={CRISIS_PINNED.scenarios}
        onSelectScenario={vi.fn()}
        {...props}
      />
    </FluentProvider>,
  );
}

describe('TrustedSignalsPanel', () => {
  it('renders external + internal signals via the shared OOA SignalsPanel', () => {
    renderPanel();
    // label · detail render together in one Body1, so match by substring
    expect(screen.getAllByText(/MeteoSwiss/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Oncology RN roster/).length).toBeGreaterThanOrEqual(1);
    // status badges from the OOA pattern
    expect(screen.getByText('THIN')).toBeInTheDocument();
    expect(screen.getAllByText('WATCH').length).toBeGreaterThanOrEqual(1);
  });

  it('renders each scenario name and its probability', () => {
    renderPanel();
    expect(screen.getAllByText('Summer heatwave demand surge').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('68%')).toBeInTheDocument();
    expect(screen.getByText('31%')).toBeInTheDocument();
    expect(screen.getByText('6%')).toBeInTheDocument();
  });

  it('fires onSelectScenario when a scenario card is clicked', () => {
    const onSelectScenario = vi.fn();
    renderPanel({ onSelectScenario });
    act(() => screen.getByRole('button', { name: 'Summer heatwave demand surge' }).click());
    expect(onSelectScenario).toHaveBeenCalledTimes(1);
    expect((onSelectScenario.mock.calls[0][0] as { id: string }).id).toBe('heatwave-surge');
  });
});
