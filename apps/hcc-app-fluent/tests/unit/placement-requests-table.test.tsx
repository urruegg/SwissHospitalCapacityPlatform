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
  it('renders all placement requests with patient IDs and wards', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    for (const p of BEDMANAGER_PINNED.placements) {
      expect(screen.getByText(p.patientId)).toBeInTheDocument();
    }
    expect(screen.getAllByText('Surgery A')[0]).toBeInTheDocument();
    expect(screen.getByText('ICU')).toBeInTheDocument();
  });

  it('renders HIGH priority badge in danger color', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getAllByText('HIGH')[0]).toBeInTheDocument();
  });

  it('renders MED and LOW priority badges', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={BEDMANAGER_PINNED.placements}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getByText('MED')).toBeInTheDocument();
    expect(screen.getByText('LOW')).toBeInTheDocument();
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
          name: new RegExp(
            `Move ${firstReq.patientId} from ${firstReq.fromWard} to ${firstReq.toWard}`,
            'i',
          ),
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
      name: new RegExp(
        `Move ${firstReq.patientId} from ${firstReq.fromWard} to ${firstReq.toWard}`,
        'i',
      ),
    });
    const notPrevented = fireEvent.keyDown(row, { key: ' ' });
    expect(notPrevented).toBe(false);
    expect(onSelectRequest).toHaveBeenCalledWith(firstReq);
  });

  it('renders a BLOCKED placement request (refused reco) without crashing', () => {
    const blockedReq: PlacementRequest = {
      id: 'test-blocked',
      patientId: 'PT-9999',
      fromWard: 'Test Ward',
      toWard: 'ICU',
      priority: 'HIGH',
      waitMin: 90,
      recoId: 'move-pt-4004-refused',
    };
    render(
      <FluentProvider theme={webLightTheme}>
        <PlacementRequestsTable
          placements={[blockedReq]}
          onSelectRequest={vi.fn()}
        />
      </FluentProvider>,
    );
    expect(screen.getByText('PT-9999')).toBeInTheDocument();
  });
});
