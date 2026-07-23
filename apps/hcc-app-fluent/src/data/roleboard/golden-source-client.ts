import type { Mode, RoleBoardData, ScenarioScope } from '../../journey/RoleBoard';
import { OCCUPANCY_PINNED, type OccupancyPayload } from './occupancy-data';
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
const goldenSourceUrl: string = import.meta.env.VITE_GOLDEN_SOURCE_URL ?? '';

export async function loadOccupancy(
  scope: ScenarioScope,
  mode: Mode,
): Promise<RoleBoardData<OccupancyPayload>> {
  const pinnedScope: ScenarioScope = { ...scope, pinned: mode === 'demo' };
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: OCCUPANCY_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/occupancy?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
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
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: DISCHARGE_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/discharge?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
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
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: BED_MANAGER_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/bed-manager?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
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
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: OR_STEERING_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/or-steering?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
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
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: STAFFING_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/staffing?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
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
  if (!goldenSourceUrl) {
    return { provenance: 'simulated', scope: pinnedScope, payload: CRISIS_PINNED };
  }
  const res = await fetch(
    `${goldenSourceUrl}/crisis?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
  );
  if (!res.ok) throw new Error(`crisis load failed: ${res.status}`);
  const payload = (await res.json()) as CrisisPayload;
  return { provenance: 'live', scope: pinnedScope, payload };
}
