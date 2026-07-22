/**
 * Sprint 3 (parity) — synthesized OR-steering dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "2 elective cases deferred, residual site -1 beds".
 */
export interface OrCase {
  id: string;
  specialty: string;
  slot: string;         // e.g. "Tue 08:00"
  bedsImpact: number;   // post-op beds this case would consume
  deferable: boolean;
}

export interface OrSteeringPayload {
  bedsShort: number;     // carried from bmca (3)
  casesDeferred: number; // deferable elective cases (2)
  bedsFreed: number;     // post-op beds freed by deferral (2)
  residualBeds: number;  // bedsFreed - bedsShort (-1), forwarded to staffing
  cases: OrCase[];
}

export const OR_STEERING_PINNED: OrSteeringPayload = {
  bedsShort: 3,
  casesDeferred: 2,
  bedsFreed: 2,
  residualBeds: -1,
  cases: [
    { id: 'ortho-knee-tue', specialty: 'Orthopedics', slot: 'Tue 08:00', bedsImpact: 1, deferable: true },
    { id: 'gen-hernia-tue', specialty: 'General surgery', slot: 'Tue 10:30', bedsImpact: 1, deferable: true },
    { id: 'cardiac-cabg-wed', specialty: 'Cardiac surgery', slot: 'Wed 07:30', bedsImpact: 2, deferable: false },
  ],
};
