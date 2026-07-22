import type { Mode, RoleBoardData, ScenarioScope } from '../../journey/RoleBoard';
import { OCCUPANCY_PINNED, type OccupancyPayload } from './occupancy-data';

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