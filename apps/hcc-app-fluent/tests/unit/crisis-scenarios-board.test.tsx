import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { CrisisScenariosBoard } from '../../src/workspaces/main/boards/crisis/CrisisScenariosBoard';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';
import type { Scenario } from '../../src/data/roleboard/crisis-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function Harness({ children }: { children: React.ReactNode }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

describe('CrisisScenariosBoard', () => {
  it('renders a row for every scenario', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    const rows = screen.getAllByRole('button').filter((r) => r.tagName === 'TR');
    expect(rows.length).toBe(CRISIS_PINNED.scenarios.length);
  });

  it('renders scenarios sorted by probability desc — heatwave-surge first', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    const rows = screen.getAllByRole('button').filter((r) => r.tagName === 'TR');
    expect(rows[0]).toHaveAttribute('aria-label', 'Summer heatwave demand surge');
  });

  it('shows circular rank badges', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('shows probability badges with % suffix', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    expect(screen.getByText('68%')).toBeInTheDocument();
    expect(screen.getByText('31%')).toBeInTheDocument();
    expect(screen.getByText('6%')).toBeInTheDocument();
  });

  it('calls onSelectScenario with the correct scenario when a row is clicked', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button').filter((r) => r.tagName === 'TR')[0];
    fireEvent.click(firstRow);
    expect(onSelect).toHaveBeenCalledTimes(1);
    // First sorted scenario is heatwave-surge
    expect((onSelect.mock.calls[0][0] as Scenario).id).toBe('heatwave-surge');
  });

  it('calls onSelectScenario on Enter keydown', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button').filter((r) => r.tagName === 'TR')[0];
    fireEvent.keyDown(firstRow, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onSelectScenario on Space keydown', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard scenarios={CRISIS_PINNED.scenarios} onSelectScenario={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button').filter((r) => r.tagName === 'TR')[0];
    fireEvent.keyDown(firstRow, { key: ' ' });
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onSimulateTop when the CTA button is clicked', () => {
    const onSelect = vi.fn();
    const onSimulate = vi.fn();
    render(
      <Harness>
        <CrisisScenariosBoard
          scenarios={CRISIS_PINNED.scenarios}
          onSelectScenario={onSelect}
          onSimulateTop={onSimulate}
        />
      </Harness>,
    );
    // The CTA button is the non-TR button in the header
    const ctaBtn = screen.getAllByRole('button').find((r) => r.tagName === 'BUTTON');
    expect(ctaBtn).toBeDefined();
    fireEvent.click(ctaBtn!);
    expect(onSimulate).toHaveBeenCalledTimes(1);
  });
});
