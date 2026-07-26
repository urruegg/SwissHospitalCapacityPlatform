import type { Mode, RoleBoardData, ScenarioScope } from '../../journey/RoleBoard';
import type { ContextEnvelope } from '../../context/context-envelope';
import { getPreferredSource } from '../data-source';
import { OCCUPANCY_PINNED, type OccupancyPayload, type SiteCapacitySummary, aggregateSiteCapacity } from './occupancy-data';
import { DISCHARGE_PINNED, type DischargePayload } from './discharge-data';
import { BED_MANAGER_PINNED, type BedManagerPayload } from './bed-manager-data';
import { OR_STEERING_PINNED, type OrSteeringPayload } from './or-steering-data';
import { STAFFING_PINNED, type StaffingPayload } from './staffing-data';
import { CRISIS_PINNED, type CrisisPayload } from './crisis-data';

/**
 * Sprint 1 (parity) / Sprint 27 / Sprint 29 — trusted-data read adapter.
 *
 * The data source is chosen by the Live/Simulated toggle (`getPreferredSource`,
 * Sprint 27): `simulated` serves the layer's synthesized fixtures; `live` reads
 * the golden source (`VITE_GOLDEN_SOURCE_URL`) through the IQ gateway. Live calls
 * carry a per-user `ContextEnvelope` (ADR-0052 OBO/RLS) as scoped headers, and a
 * live call without an envelope is refused (throws). Every result carries an
 * evidence envelope (provenance + `hcp:*` / `gold.*` citations + `degraded`);
 * when `live` is selected but no golden source is configured we fail loud
 * (`degraded: true`) rather than silently pretending.
 */
let currentEnvelope: ContextEnvelope | null = null;

function goldenUrl(): string {
  return import.meta.env.VITE_GOLDEN_SOURCE_URL ?? '';
}

/** The app sets this once the user context/active board is established; the IQ gateway attaches it as scoped headers on every live call. */
export function setContextEnvelope(env: ContextEnvelope | null): void {
  currentEnvelope = env;
}

export function getContextEnvelope(): ContextEnvelope | null {
  return currentEnvelope;
}

/** Live IQ fetch with per-user OBO/RLS headers (ADR-0052). Refuses ungrounded calls. */
async function iqFetch(path: string): Promise<Response> {
  if (currentEnvelope === null) {
    throw new Error('IQ gateway call requires a ContextEnvelope; call setContextEnvelope() first');
  }
  return fetch(path, {
    headers: {
      'X-User-Oid': currentEnvelope.userOid ?? '',
      'X-Hospital-Scope': currentEnvelope.hospitalScope,
      'X-Active-Role': currentEnvelope.activeRole,
    },
  });
}

// Representative ontology + gold citations per board. The demo fixtures are
// grounded on these MVO entities; a live golden source returns its own.
const CITES = {
  occupancy: ['hcp:CapacityUnit', 'hcp:Bed', 'gold.fact_capacity_baseline', 'gold.fact_occupancy_forecast'],
  discharge: ['hcp:Encounter', 'hcp:Bed', 'gold.fact_discharge_readiness'],
  bedManager: ['hcp:CapacityUnit', 'hcp:Bed', 'gold.bed_assignment'],
  orSteering: ['hcp:ORSlot', 'hcp:CapacityUnit', 'gold.fact_or_schedule'],
  staffing: ['hcp:CareTeam', 'gold.fact_staffing_roster'],
  crisis: ['hcp:Facility', 'hcp:CapacityUnit', 'gold.fact_capacity_baseline'],
} as const;

/**
 * Shared structured-read path: simulated fixture when the toggle is `simulated`
 * (or the golden source is unavailable, flagged `degraded`), or live golden
 * evidence via the IQ gateway (OBO/RLS scoped) when `live` is selected and
 * configured.
 */
async function loadBoard<P>(
  resource: string,
  fixture: P,
  citations: readonly string[],
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<P>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  const cites = [...citations];
  // Simulated preference (or the demo default) -> fixtures, clean provenance.
  if (getPreferredSource() === 'simulated') {
    return { provenance: 'simulated', scope: pinnedScope, payload: fixture, citations: cites, degraded: false };
  }
  // Live requested but no golden source configured -> fail loud (degraded).
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: fixture, citations: cites, degraded: true };
  }
  // Live + configured -> OBO/RLS gateway (iqFetch refuses without a ContextEnvelope).
  const res = await iqFetch(
    `${goldenUrl()}/${resource}?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`${resource} load failed: ${res.status}`);
  const payload = (await res.json()) as P;
  return { provenance: 'live', scope: pinnedScope, payload, citations: cites, degraded: false };
}

export function loadOccupancy(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<OccupancyPayload>> {
  return loadBoard('occupancy', OCCUPANCY_PINNED, CITES.occupancy, scope, mode);
}

export function loadDischarge(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<DischargePayload>> {
  return loadBoard('discharge', DISCHARGE_PINNED, CITES.discharge, scope, mode);
}

export function loadBedManager(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<BedManagerPayload>> {
  return loadBoard('bed-manager', BED_MANAGER_PINNED, CITES.bedManager, scope, mode);
}

export function loadOrSteering(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<OrSteeringPayload>> {
  return loadBoard('or-steering', OR_STEERING_PINNED, CITES.orSteering, scope, mode);
}

export function loadStaffing(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<StaffingPayload>> {
  return loadBoard('staffing', STAFFING_PINNED, CITES.staffing, scope, mode);
}

export function loadCrisis(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<CrisisPayload>> {
  return loadBoard('crisis', CRISIS_PINNED, CITES.crisis, scope, mode);
}

/**
 * Aggregates the OOA occupancy source into a site-level summary for the START
 * surface teaser. START and OOA read the same golden source so their figures agree.
 * Delegates to the pure `aggregateSiteCapacity` helper (testable without I/O mocking).
 */
export async function loadSiteCapacitySummary(
  scope: ScenarioScope,
  mode: Mode,
): Promise<SiteCapacitySummary> {
  const data = await loadOccupancy(scope, mode);
  return aggregateSiteCapacity(
    data.payload.wards,
    data.payload.capacity,
    scope.windowHours,
    data.provenance,
    new Date().toISOString(),
  );
}
