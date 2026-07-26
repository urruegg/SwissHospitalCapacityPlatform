import type { RoleCapabilities } from '../../auth/rbac-model';

/**
 * Sprint 29 M2 — role-first-eligible default board (design Q1).
 *
 * Replaces the hard-coded `bed-manager` default so `/main` opens the first
 * board in patient-journey order that the active role's nav gates actually
 * allow. A role that cannot see the main boards never lands on one it has no
 * access to.
 */

export type BoardKey =
  | 'occupancy'
  | 'bed-manager'
  | 'or-steering'
  | 'staffing'
  | 'discharge'
  | 'crisis';

type BoardGate = keyof RoleCapabilities['nav'];

/** Boards in patient-journey order, each paired with the nav gate it needs. */
export const PATIENT_JOURNEY_BOARDS: ReadonlyArray<{ key: BoardKey; gate: BoardGate }> = [
  { key: 'occupancy', gate: 'main' },
  { key: 'bed-manager', gate: 'main' },
  { key: 'or-steering', gate: 'main' },
  { key: 'staffing', gate: 'main' },
  { key: 'discharge', gate: 'main' },
  { key: 'crisis', gate: 'csa' },
];

/**
 * The first patient-journey board whose nav gate the given capabilities allow.
 * Falls back to the first journey board when no gate is open — defensive only;
 * every real demo role holds `nav.main`, so `occupancy` is always eligible.
 */
export function firstEligibleBoard(capabilities: Pick<RoleCapabilities, 'nav'>): BoardKey {
  const nav = capabilities.nav as Record<BoardGate, boolean>;
  const match = PATIENT_JOURNEY_BOARDS.find((board) => nav[board.gate]);
  return (match ?? PATIENT_JOURNEY_BOARDS[0]).key;
}
