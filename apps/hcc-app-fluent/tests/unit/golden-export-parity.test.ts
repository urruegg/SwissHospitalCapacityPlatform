// Golden-export drift guard: asserts the agent-host's committed golden JSON
// (apps/hcc-agent-host/src/golden/data/*.json) stays byte-equal to the app's
// board fixtures (the single source of truth). Runs under vitest in full-repo
// CI where BOTH apps are checked out.
//
// NOTE: this is the only file that imports across the app boundary into
// hcc-agent-host. It is therefore EXCLUDED from tsconfig.json ("exclude"), so
// the app's `tsc -b && vite build` (which runs inside an app-only Docker build
// context where the sibling hcc-agent-host folder is absent) does not try to
// resolve these cross-app imports. vitest discovers this test via
// vite.config.ts `test.include`, independent of tsconfig, so the guard still
// runs in CI. Do not add cross-app imports to any file under src/.
import { describe, it, expect } from 'vitest';

import { OCCUPANCY_PINNED } from '../../src/data/roleboard/occupancy-data';
import { DISCHARGE_PINNED } from '../../src/data/roleboard/discharge-data';
import { BED_MANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';
import { OR_STEERING_PINNED } from '../../src/data/roleboard/or-steering-data';
import { STAFFING_PINNED } from '../../src/data/roleboard/staffing-data';
import { CRISIS_PINNED } from '../../src/data/roleboard/crisis-data';

import occupancyJson from '../../../hcc-agent-host/src/golden/data/occupancy.json';
import dischargeJson from '../../../hcc-agent-host/src/golden/data/discharge.json';
import bedManagerJson from '../../../hcc-agent-host/src/golden/data/bed-manager.json';
import orSteeringJson from '../../../hcc-agent-host/src/golden/data/or-steering.json';
import staffingJson from '../../../hcc-agent-host/src/golden/data/staffing.json';
import crisisJson from '../../../hcc-agent-host/src/golden/data/crisis.json';

/**
 * #424 M2 — golden-source drift guard.
 *
 * The agent-host serves `live` golden payloads from committed JSON exported from
 * these RoleBoard `*_PINNED` fixtures (the single source of truth). This test
 * fails if the committed host JSON drifts from the fixtures, so the live read
 * path can never silently diverge from the simulated one. Regenerate with the
 * esbuild export documented in the PR when a fixture legitimately changes.
 */
const cases: ReadonlyArray<readonly [string, unknown, unknown]> = [
  ['occupancy', OCCUPANCY_PINNED, occupancyJson],
  ['discharge', DISCHARGE_PINNED, dischargeJson],
  ['bed-manager', BED_MANAGER_PINNED, bedManagerJson],
  ['or-steering', OR_STEERING_PINNED, orSteeringJson],
  ['staffing', STAFFING_PINNED, staffingJson],
  ['crisis', CRISIS_PINNED, crisisJson],
];

describe('golden-source export parity (#424 M2)', () => {
  it.each(cases)('agent-host %s.json matches the RoleBoard fixture', (_resource, fixture, json) => {
    // JSON round-trip the fixture to drop `undefined`s exactly as the export does.
    expect(json).toEqual(JSON.parse(JSON.stringify(fixture)));
  });
});
