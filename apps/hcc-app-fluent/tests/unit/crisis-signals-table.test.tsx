import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { CrisisSignalsTable } from '../../src/workspaces/main/boards/crisis/CrisisSignalsTable';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';
import type { ExternalSignal } from '../../src/data/roleboard/crisis-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function Harness({ children }: { children: React.ReactNode }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

describe('CrisisSignalsTable', () => {
  it('renders a row for every signal', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBe(CRISIS_PINNED.signals.length);
  });

  it('shows source text for each signal', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    expect(screen.getAllByText('MeteoSwiss').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('BAG/FOPH').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('SED-ETH').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Alertswiss/BABS').length).toBeGreaterThanOrEqual(1);
  });

  it('shows Quarantined badge for filtered signals and Nominal for active ones', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    const filteredCount = CRISIS_PINNED.signals.filter((s) => s.filtered).length;
    const activeCount = CRISIS_PINNED.signals.filter((s) => !s.filtered).length;
    expect(screen.getAllByText('Quarantined').length).toBe(filteredCount);
    expect(screen.getAllByText('Nominal').length).toBe(activeCount);
  });

  it('calls onSelectSignal with the correct signal when a row is clicked', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button')[0];
    fireEvent.click(firstRow);
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect((onSelect.mock.calls[0][0] as ExternalSignal).id).toBe(CRISIS_PINNED.signals[0].id);
  });

  it('calls onSelectSignal on Enter keydown', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button')[0];
    fireEvent.keyDown(firstRow, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onSelectSignal on Space keydown', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    const firstRow = screen.getAllByRole('button')[0];
    fireEvent.keyDown(firstRow, { key: ' ' });
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('shows Trust-A badge for every signal', () => {
    const onSelect = vi.fn();
    render(
      <Harness>
        <CrisisSignalsTable signals={CRISIS_PINNED.signals} onSelectSignal={onSelect} />
      </Harness>,
    );
    expect(screen.getAllByText('Trust-A').length).toBe(CRISIS_PINNED.signals.length);
  });
});
