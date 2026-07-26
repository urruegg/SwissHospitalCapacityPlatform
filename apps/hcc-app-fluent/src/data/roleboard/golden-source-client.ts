import type { Mode, RoleBoardData, ScenarioScope } from '../../journey/RoleBoard';
import type { ContextEnvelope } from '../../context/context-envelope';
import { OCCUPANCY_PINNED, type OccupancyPayload, type SiteCapacitySummary, aggregateSiteCapacity } from './occupancy-data';
import { DISCHARGE_PINNED, type DischargePayload } from './discharge-data';
import { BED_MANAGER_PINNED, type BedManagerPayload } from './bed-manager-data';
import { OR_STEERING_PINNED, type OrSteeringPayload } from './or-steering-data';
import { STAFFING_PINNED, type StaffingPayload } from './staffing-data';
import { CRISIS_PINNED, type CrisisPayload } from './crisis-data';

/**
 * Sprint 1 (parity) — trusted-data read adapter. When the Sprint 22 golden
 * source is wired (VITE_GOLDEN_SOURCE_URL), reads live; otherwise serves the
 * layer's synthesized dataset flagged `simulated`. Demo mode pins the golden
 * thread window over the same trusted data (a real slice, not fabricated).
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

export async function loadOccupancy(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<OccupancyPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: OCCUPANCY_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/occupancy?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`occupancy load failed: ${res.status}`);
  const payload = (await res.json()) as OccupancyPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}

export async function loadDischarge(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<DischargePayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: DISCHARGE_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/discharge?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`discharge load failed: ${res.status}`);
  const payload = (await res.json()) as DischargePayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}

export async function loadBedManager(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<BedManagerPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: BED_MANAGER_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/bed-manager?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`bed-manager load failed: ${res.status}`);
  const payload = (await res.json()) as BedManagerPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}

export async function loadOrSteering(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<OrSteeringPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: OR_STEERING_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/or-steering?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`or-steering load failed: ${res.status}`);
  const payload = (await res.json()) as OrSteeringPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}

export async function loadStaffing(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<StaffingPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: STAFFING_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/staffing?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`staffing load failed: ${res.status}`);
  const payload = (await res.json()) as StaffingPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}

export async function loadCrisis(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<CrisisPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenUrl()) {
    return { provenance: 'simulated', scope: pinnedScope, payload: CRISIS_PINNED };
  }
  const res = await iqFetch(
    `${goldenUrl()}/crisis?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`crisis load failed: ${res.status}`);
  const payload = (await res.json()) as CrisisPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
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
