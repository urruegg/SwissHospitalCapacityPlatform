import { isGoldenSourceConfigured } from './iq-client';

/** Sprint 27 — data-source preference: live golden evidence vs simulated fixtures. */
export type DataSourceMode = 'live' | 'simulated';

/**
 * Module-level preference read by the (pure, non-React) data layer without
 * threading a param through the frozen `RoleBoard.load(scope, mode)` contract.
 * The `DataSourceProvider` keeps this in sync with the header toggle. Defaults to
 * `live` when a golden source is configured, else `simulated` (demo scope).
 */
let preferred: DataSourceMode = isGoldenSourceConfigured() ? 'live' : 'simulated';

export function getPreferredSource(): DataSourceMode {
  return preferred;
}

export function setPreferredSource(mode: DataSourceMode): void {
  preferred = mode;
}
