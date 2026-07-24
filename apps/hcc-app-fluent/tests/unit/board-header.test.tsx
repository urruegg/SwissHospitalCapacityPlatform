import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { BoardHeader } from '../../src/workspaces/main/boards/occupancy/BoardHeader';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderHeader() {
  return render(
    <FluentProvider theme={webLightTheme}>
      <BoardHeader agent="ooa-agent" title="Occupancy & 72h Forecast" provenance="simulated" lens="Bed Ops" />
    </FluentProvider>,
  );
}

describe('BoardHeader', () => {
  it('renders the agent label, title, and badges', () => {
    renderHeader();
    expect(screen.getByText(/ooa-agent/)).toBeInTheDocument();
    expect(screen.getByText('Occupancy & 72h Forecast')).toBeInTheDocument();
    expect(screen.getByText(/simulated data/i)).toBeInTheDocument();
    expect(screen.getByText(/Bed Ops/)).toBeInTheDocument();
  });
});
