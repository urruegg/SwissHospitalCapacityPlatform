import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { ScenarioQueueTable } from '../../src/workspaces/main/boards/crisis/ScenarioQueueTable';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderTable(onSelectQueued = vi.fn()) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <ScenarioQueueTable queue={CRISIS_PINNED.scenarioQueue} onSelectQueued={onSelectQueued} />
    </FluentProvider>,
  );
}

describe('ScenarioQueueTable', () => {
  it('renders a row for every queued scenario', () => {
    renderTable();
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBe(CRISIS_PINNED.scenarioQueue.length);
  });

  it('renders the result badges', () => {
    renderTable();
    expect(screen.getByText('SIMULATE')).toBeInTheDocument();
    expect(screen.getAllByText('MODELLED').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('HOLDS')).toBeInTheDocument();
    expect(screen.getByText('STRESS-MAX')).toBeInTheDocument();
  });

  it('fires onSelectQueued with the correct row when clicked', () => {
    const onSelectQueued = vi.fn();
    renderTable(onSelectQueued);
    act(() => screen.getByRole('button', { name: /SC-01/ }).click());
    expect(onSelectQueued).toHaveBeenCalledWith(CRISIS_PINNED.scenarioQueue[0]);
  });
});
