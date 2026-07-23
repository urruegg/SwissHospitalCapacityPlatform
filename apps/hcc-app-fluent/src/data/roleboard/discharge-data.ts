/**
 * Sprint 2 (parity) — synthesized discharge dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "9 expeditable discharges, residual site -7 beds".
 */
export interface DischargeCandidate {
  id: string;
  ward: string;
  blocker: string;
  bedsFreeable: number;
  expedite: boolean;
}

export interface DischargePayload {
  bedsNeeded: number;
  bedsFreeable: number;
  residualBeds: number;
  candidates: DischargeCandidate[];
}

export const DISCHARGE_PINNED: DischargePayload = {
  bedsNeeded: 16,
  bedsFreeable: 9,
  residualBeds: -7,
  candidates: [
    { id: 'med-a-spitex', ward: 'Medicine A', blocker: 'Awaiting Spitex slot', bedsFreeable: 4, expedite: true },
    { id: 'med-a-rehab', ward: 'Medicine A', blocker: 'Rehab transfer pending', bedsFreeable: 3, expedite: true },
    { id: 'surg-a-imaging', ward: 'Surgery A', blocker: 'Discharge imaging pending', bedsFreeable: 2, expedite: true },
    { id: 'med-b-family', ward: 'Medicine B', blocker: 'Family readiness', bedsFreeable: 2, expedite: false },
  ],
};
