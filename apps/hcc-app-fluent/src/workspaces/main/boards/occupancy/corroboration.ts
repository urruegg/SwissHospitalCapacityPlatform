export interface SignalKey {
  hazardType: string;
  cantons: string[];
  trustClass: 'Trust-A' | 'Trust-B';
}

/**
 * Display-only: a Trust-B web signal corroborates a Trust-A signal iff same
 * hazard type and overlapping canton. This NEVER changes a lever, a forecast
 * number, or a recommendation (ADR-0036/ADR-0060) — it only raises reviewer
 * confidence in the already-gated Trust-A signal.
 */
export function corroborates(trustA: SignalKey, web: SignalKey): boolean {
  if (trustA.trustClass !== 'Trust-A' || web.trustClass !== 'Trust-B') return false;
  if (trustA.hazardType !== web.hazardType) return false;
  return trustA.cantons.some((c) => web.cantons.includes(c));
}
