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
        signals={CRISIS_PINNED.signals}
        internalSignals={CRISIS_PINNED.internalSignals}
        scenarios={CRISIS_PINNED.scenarios}
        onSelectSignal={vi.fn()}
        onSelectScenario={vi.fn()}
        {...props}
      />
    </FluentProvider>,
  );
}

describe('TrustedSignalsPanel', () => {
  it('renders external Trust-A signal sources', () => {
    renderPanel();
    expect(screen.getAllByText('MeteoSwiss')[0]).toBeInTheDocument();
    expect(screen.getAllByText('BAG/FOPH')[0]).toBeInTheDocument();
  });

  it('renders internal signals', () => {
    renderPanel();
    expect(screen.getByText('Oncology RN roster')).toBeInTheDocument();
    expect(screen.getByText('ED arrivals')).toBeInTheDocument();
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

  it('fires onSelectSignal when an external signal is clicked', () => {
    const onSelectSignal = vi.fn();
    renderPanel({ onSelectSignal });
    act(() => screen.getByRole('button', { name: /MeteoSwiss/ }).click());
    expect(onSelectSignal).toHaveBeenCalledTimes(1);
    expect((onSelectSignal.mock.calls[0][0] as { id: string }).id).toBe('meteoswiss-heat');
  });
});
