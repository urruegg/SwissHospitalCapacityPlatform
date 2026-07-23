import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { DischargeWorklistTable } from '../../src/workspaces/main/boards/discharge/DischargeWorklistTable';
import { DISCHARGE_PINNED } from '../../src/data/roleboard/discharge-data';
import type { DischargeCandidate } from '../../src/data/roleboard/discharge-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('DischargeWorklistTable', () => {
  it('renders all candidates showing ward, readiness, and blocker', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <DischargeWorklistTable candidates={DISCHARGE_PINNED.candidates} onSelectCandidate={vi.fn()} />
      </FluentProvider>,
    );
    // ward text visible
    expect(screen.getAllByText('Medicine A')[0]).toBeInTheDocument();
    // blocker text visible
    expect(screen.getByText('Awaiting Spitex slot')).toBeInTheDocument();
    // READY badge visible
    expect(screen.getAllByText('READY')[0]).toBeInTheDocument();
  });

  it('renders PENDING badge for PENDING candidates', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <DischargeWorklistTable candidates={DISCHARGE_PINNED.candidates} onSelectCandidate={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getByText('PENDING')).toBeInTheDocument();
  });

  it('renders BLOCKED badge for BLOCKED candidates', () => {
    const withBlocked: DischargeCandidate[] = [
      {
        id: 'test-blocked',
        patientId: 'PT-9999',
        ward: 'Test Ward',
        readiness: 'BLOCKED',
        blocker: 'Insurance hold',
        estFreeHours: 48,
        bedsFreeable: 1,
        recoId: 'test-blocked',
      },
    ];
    render(
      <FluentProvider theme={webLightTheme}>
        <DischargeWorklistTable candidates={withBlocked} onSelectCandidate={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getByText('BLOCKED')).toBeInTheDocument();
  });

  it('fires onSelectCandidate with the correct candidate when a row is clicked', () => {
    const onSelectCandidate = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <DischargeWorklistTable candidates={DISCHARGE_PINNED.candidates} onSelectCandidate={onSelectCandidate} />
      </FluentProvider>,
    );
    act(() =>
      screen
        .getByRole('button', { name: /Expedite Medicine A discharge.*Awaiting Spitex slot/i })
        .click(),
    );
    expect(onSelectCandidate).toHaveBeenCalledWith(DISCHARGE_PINNED.candidates[0]);
  });
});
