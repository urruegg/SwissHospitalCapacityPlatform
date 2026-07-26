import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act, fireEvent } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { PlacementRequestsTable } from '../../src/workspaces/main/boards/bed-manager/PlacementRequestsTable';
import { BEDMANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';
import type { PlacementRequest } from '../../src/data/roleboard/bed-manager-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('PlacementRequestsTable', () => {
  it('renders all placement requests with RQ ids, source and target', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    for (const p of BEDMANAGER_PINNED.placements) {
      expect(screen.getByText(p.id)).toBeInTheDocument();
    }
    expect(screen.getAllByText('ED boarder')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Medicine A')[0]).toBeInTheDocument();
  });

  it('renders PLACED, WAITING and BLOCKED status badges', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getAllByText('PLACED')[0]).toBeInTheDocument();
    expect(screen.getAllByText('WAITING')[0]).toBeInTheDocument();
    expect(screen.getByText('BLOCKED')).toBeInTheDocument();
  });

  it('fires onSelectRequest with the correct request when a row is clicked', () => {
    const onSelectRequest = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={onSelectRequest}
        />
      </FluentProvider>,
    );
    const firstReq = BEDMANAGER_PINNED.placements[0];
    act(() =>
      screen
        .getByRole('button', {
          name: `Place ${firstReq.id}: ${firstReq.source} → ${firstReq.target}`,
        })
        .click(),
    );
    expect(onSelectRequest).toHaveBeenCalledWith(firstReq);
  });

  it('fires onSelectRequest and prevents default on Space (no page scroll)', () => {
    const onSelectRequest = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={onSelectRequest}
        />
      </FluentProvider>,
    );
    const firstReq = BEDMANAGER_PINNED.placements[0];
    const row = screen.getByRole('button', {
      name: `Place ${firstReq.id}: ${firstReq.source} → ${firstReq.target}`,
    });
    const notPrevented = fireEvent.keyDown(row, { key: ' ' });
    expect(notPrevented).toBe(false);
    expect(onSelectRequest).toHaveBeenCalledWith(firstReq);
  });

  it('renders a BLOCKED placement request (refused reco) without crashing', () => {
    const blockedReq: PlacementRequest = {
      id: 'RQ-9999',
      source: 'ED boarder',
      target: 'ICU',
      status: 'BLOCKED',
      barrier: 'Ward at staff ratio',
      recoId: 'rq-9999',
    };
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={[blockedReq]}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getByText('RQ-9999')).toBeInTheDocument();
    expect(screen.getByText('BLOCKED')).toBeInTheDocument();
  });
});
