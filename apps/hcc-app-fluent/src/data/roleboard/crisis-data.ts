/**
 * Sprint 4 (parity) — synthesized CSA crisis dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes Trust-A `DC-EXT-SIGNAL-v1`
 * external sources: MeteoSwiss, Alertswiss/BABS, SED-ETH, and BAG/FOPH.
 */
export type Certainty = 'high' | 'medium' | 'low';

/** Trust-A certainty -> scenario probability mapping (DC-EXT-SIGNAL-v1). */
export function certaintyToProbability(c: Certainty): number {
  return c === 'high' ? 0.8 : c === 'medium' ? 0.5 : 0.2;
}

export interface ExternalSignal {
  id: string;
  source: string;     // 'MeteoSwiss' | 'Alertswiss/BABS' | 'SED-ETH' | 'BAG/FOPH'
  label: string;
  certainty: Certainty;
}

export interface CrisisScenario {
  id: string;
  label: string;
  probability: number;   // 0..1, consistent with the driving signal's certainty
  bedDayImpact: number;  // added bed-days if the scenario materialises
  drivenBy: string[];    // ExternalSignal ids
}

export interface CrisisPayload {
  residualBeds: number;      // carried in from sba (0 = balanced steady state)
  signals: ExternalSignal[];
  scenarios: CrisisScenario[];
}

export const CRISIS_PINNED: CrisisPayload = {
  residualBeds: 0,
  signals: [
    { id: 'meteoswiss-heat', source: 'MeteoSwiss', label: 'Heatwave warning (level 3)', certainty: 'high' },
    { id: 'bag-resp', source: 'BAG/FOPH', label: 'Rising respiratory virus activity', certainty: 'medium' },
    { id: 'sed-seismic', source: 'SED-ETH', label: 'Minor seismic activity', certainty: 'low' },
  ],
  scenarios: [
    { id: 'heatwave-surge', label: 'Summer heatwave demand surge', probability: certaintyToProbability('high'), bedDayImpact: 14, drivenBy: ['meteoswiss-heat'] },
    { id: 'resp-virus-surge', label: 'Respiratory virus surge', probability: certaintyToProbability('medium'), bedDayImpact: 9, drivenBy: ['bag-resp'] },
  ],
};
