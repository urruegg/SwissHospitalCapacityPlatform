/**
 * Sprint 1 (parity) — synthesized occupancy dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "Medicine A -> 102% occupancy in 72h, site -16 beds".
 */
export interface OccupancyChannel {
  id: string;
  label: string;
  occupancyPct: number;
  deltaBeds: number;
}

export interface OccupancyPayload {
  siteOccupancyPct: number;
  siteDeltaBeds: number;
  channels: OccupancyChannel[];
}

export const OCCUPANCY_PINNED: OccupancyPayload = {
  siteOccupancyPct: 97,
  siteDeltaBeds: -16,
  channels: [
    { id: 'med-a', label: 'Medicine A', occupancyPct: 102, deltaBeds: -9 },
    { id: 'med-b', label: 'Medicine B', occupancyPct: 94, deltaBeds: -4 },
    { id: 'surg-a', label: 'Surgery A', occupancyPct: 88, deltaBeds: -3 },
  ],
};