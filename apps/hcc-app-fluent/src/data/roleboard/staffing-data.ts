/**
 * Sprint 3 (parity) — synthesized Staffing dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "1 surge bed enabled, residual site balanced".
 */
export interface StaffMove {
  id: string;
  fromUnit: string;
  toUnit: string;
  role: string;      // e.g. "RN"
  fte: number;
}

export interface StaffingPayload {
  bedsShort: number;        // carried from orsa (1)
  surgeBedsEnabled: number; // surge beds unlocked by staffing (1)
  residualBeds: number;     // surgeBedsEnabled - bedsShort (0 = balanced)
  moves: StaffMove[];
}

export const STAFFING_PINNED: StaffingPayload = {
  bedsShort: 1,
  surgeBedsEnabled: 1,
  residualBeds: 0,
  moves: [
    { id: 'rn-icu-to-meda', fromUnit: 'ICU float', toUnit: 'Medicine A', role: 'RN', fte: 1 },
    { id: 'hca-surg-to-medb', fromUnit: 'Surgery B', toUnit: 'Medicine B', role: 'HCA', fte: 0.5 },
  ],
};
