/**
 * Sprint 2 (parity) — synthesized bed-manager dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "7 beds short, 4 beds reallocated, residual site -3 beds".
 */
export interface BedReallocation {
  id: string;
  fromWard: string;
  toWard: string;
  beds: number;
}

export interface BedManagerPayload {
  bedsShort: number;       // carried from dca (7)
  bedsReallocated: number; // absorbed via reallocations (4)
  residualBeds: number;    // bedsReallocated - bedsShort (-3), forwarded to orsa
  reallocations: BedReallocation[];
}

export const BED_MANAGER_PINNED: BedManagerPayload = {
  bedsShort: 7,
  bedsReallocated: 4,
  residualBeds: -3,
  reallocations: [
    { id: 'surg-a-to-med-a', fromWard: 'Surgery A', toWard: 'Medicine A', beds: 2 },
    { id: 'surg-b-to-med-a', fromWard: 'Surgery B', toWard: 'Medicine A', beds: 1 },
    { id: 'ortho-to-med-b', fromWard: 'Orthopedics', toWard: 'Medicine B', beds: 1 },
  ],
};
