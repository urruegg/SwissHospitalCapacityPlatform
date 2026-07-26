import { describe, it, expect } from 'vitest';
import {
  firstEligibleBoard,
  PATIENT_JOURNEY_BOARDS,
} from '../../src/shell/planes/first-eligible-board';
import { deriveCapabilities, type RoleCapabilities } from '../../src/auth/rbac-model';

/** Build a capabilities-like value with only the nav gates that matter here. */
function caps(nav: Partial<RoleCapabilities['nav']>): Pick<RoleCapabilities, 'nav'> {
  return {
    nav: { start: false, main: false, csa: false, backstage: false, settings: false, ...nav },
  };
}

describe('firstEligibleBoard', () => {
  it('returns the first patient-journey board a main-capable role can see', () => {
    expect(firstEligibleBoard(deriveCapabilities('HCC.Viewer', 'usz'))).toBe('occupancy');
    expect(firstEligibleBoard(deriveCapabilities('HCC.BedManager', 'usz'))).toBe('occupancy');
    expect(firstEligibleBoard(deriveCapabilities('HCC.RegionalCrisisLead', 'aggregated'))).toBe(
      'occupancy',
    );
  });

  it('never defaults to bed-manager for a role that cannot see the main boards', () => {
    // csa-only role: main boards hidden, crisis (csa gate) is the only eligible board.
    const board = firstEligibleBoard(caps({ csa: true }));
    expect(board).toBe('crisis');
    expect(board).not.toBe('bed-manager');
  });

  it('honours patient-journey order (occupancy before bed-manager)', () => {
    expect(PATIENT_JOURNEY_BOARDS.map((b) => b.key)).toEqual([
      'occupancy',
      'bed-manager',
      'or-steering',
      'staffing',
      'discharge',
      'crisis',
    ]);
  });

  it('falls back to the first journey board when no gate is open (defensive)', () => {
    expect(firstEligibleBoard(caps({}))).toBe('occupancy');
  });
});
