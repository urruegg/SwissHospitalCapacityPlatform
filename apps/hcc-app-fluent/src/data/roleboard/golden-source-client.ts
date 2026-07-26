import type { Mode, RoleBoardData, ScenarioScope } from '../../journey/RoleBoard';
import { isGoldenSourceConfigured, iqStructuredRead } from '../iq-client';
import { getPreferredSource } from '../data-source';
import { OCCUPANCY_PINNED, type OccupancyPayload, type SiteCapacitySummary, aggregateSiteCapacity } from './occupancy-data';
import { DISCHARGE_PINNED, type DischargePayload } from './discharge-data';
import { BED_MANAGER_PINNED, type BedManagerPayload } from './bed-manager-data';
import { OR_STEERING_PINNED, type OrSteeringPayload } from './or-steering-data';
import { STAFFING_PINNED, type StaffingPayload } from './staffing-data';
import { CRISIS_PINNED, type CrisisPayload } from './crisis-data';

/**
 * Sprint 1 (parity) / Sprint 27 — trusted-data read adapter, routed through the
 * IQ-layer gateway (`../iq-client`). When the golden source is configured
 * (`VITE_GOLDEN_SOURCE_URL` -> Fabric Data Agent / semantic model over Gold) it
 * reads live golden evidence; otherwise it serves the layer's simulated fixture
 * flagged `simulated`. If the source is configured but the read fails, it falls
 * back to the fixture flagged `degraded` (fail loud, never silent). Every result
 * carries an evidence envelope (provenance + `hcp:*` / `gold.*` citations + degraded).
 */

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
 * Shared structured-read path: simulated fixture when unconfigured, live golden
 * evidence when configured, or a loud `degraded` fallback on read failure.
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
  if (!isGoldenSourceConfigured()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: fixture, citations: cites, degraded: true };
  }
  try {
    const { payload, citations: live } = await iqStructuredRead<P>(
      `/${resource}?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
    );
    return { provenance: 'live', scope: pinnedScope, payload, citations: live.length ? live : cites, degraded: false };
  } catch {
    return { provenance: 'simulated', scope: pinnedScope, payload: fixture, citations: cites, degraded: true };
  }
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
