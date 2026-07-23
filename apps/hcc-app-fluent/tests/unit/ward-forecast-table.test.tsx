import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { WardForecastTable } from '../../src/workspaces/main/boards/occupancy/WardForecastTable';
import { OCCUPANCY_PINNED } from '../../src/data/roleboard/occupancy-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('WardForecastTable', () => {
  it('renders every ward with now/forecast and fires onSelectWard', () => {
    const onSelectWard = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <WardForecastTable wards={OCCUPANCY_PINNED.wards} onSelectWard={onSelectWard} />
      </FluentProvider>,
    );
    expect(screen.getByText('Medicine A')).toBeInTheDocument();
    expect(screen.getByText('102%')).toBeInTheDocument();
    act(() => screen.getByRole('button', { name: /Medicine A/ }).click());
    expect(onSelectWard).toHaveBeenCalledWith(OCCUPANCY_PINNED.wards[0]);
  });
});
