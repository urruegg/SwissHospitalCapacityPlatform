import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { SignalsPanel } from '../../src/workspaces/main/boards/occupancy/SignalsPanel';
import { OCCUPANCY_SIGNALS } from '../../src/data/roleboard/occupancy-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('SignalsPanel', () => {
  it('renders external Trust-A and internal signal sections with status + provenance badges', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <SignalsPanel signals={OCCUPANCY_SIGNALS} />
      </FluentProvider>,
    );
    expect(screen.getByTestId('ooa-signals-panel')).toBeInTheDocument();
    expect(screen.getByText(/External signals/i)).toBeInTheDocument();
    expect(screen.getByText(/Internal signals/i)).toBeInTheDocument();
    // status badges (external + internal)
    expect(screen.getByText('ELEVATED')).toBeInTheDocument();
    expect(screen.getByText('THIN')).toBeInTheDocument();
    // every signal carries a provenance badge (all simulated in demo scope)
    const provenance = screen.getAllByLabelText(/Simulated data|Live data/);
    expect(provenance.length).toBe(OCCUPANCY_SIGNALS.length);
  });
});
