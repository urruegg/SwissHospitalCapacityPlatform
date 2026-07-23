import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { CapacityFlowDiagram } from '../../src/workspaces/main/boards/occupancy/CapacityFlowDiagram';
import { OCCUPANCY_PINNED } from '../../src/data/roleboard/occupancy-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('CapacityFlowDiagram', () => {
  it('renders channels, streams, outputs, and routes stream + gap clicks', () => {
    const onSelectStream = vi.fn();
    const onSelectGap = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <CapacityFlowDiagram
          channels={OCCUPANCY_PINNED.channels}
          streams={OCCUPANCY_PINNED.streams}
          capacity={OCCUPANCY_PINNED.capacity}
          onSelectStream={onSelectStream}
          onSelectGap={onSelectGap}
        />
      </FluentProvider>,
    );
    expect(screen.getByText('ED arrivals')).toBeInTheDocument();
    expect(screen.getByText('Emergency & Acute Medicine')).toBeInTheDocument();
    expect(screen.getByText(/105\s*\/\s*130/)).toBeInTheDocument();

    act(() => screen.getByRole('button', { name: /Emergency & Acute Medicine/ }).click());
    expect(onSelectStream).toHaveBeenCalledWith(OCCUPANCY_PINNED.streams[0]);

    act(() => screen.getByRole('button', { name: /beds needed within 72h/i }).click());
    expect(onSelectGap).toHaveBeenCalled();
  });
});
