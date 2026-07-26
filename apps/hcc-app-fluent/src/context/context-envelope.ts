import type { ParsedClaims } from '../auth/claim-parser';
import type { HccRole, HospitalScope } from '../auth/rbac-model';
import type { AgentId } from '../journey/RoleBoard';

/**
 * Sprint 29 M0 — the `ContextEnvelope`.
 *
 * The single object every IQ read + agent turn carries (design §4.2). It is
 * derived, by construction, from the signed-in user's claims + active role
 * lens, so the three context tiers (user / agent / grounding) stay consistent.
 *
 * Pure, side-effect free: given the same inputs it always returns the same
 * envelope. Missing user context degrades to least privilege (Viewer /
 * aggregated) rather than throwing, so an unauthenticated or partially-loaded
 * shell never leaks a wider data scope than it should.
 */

/** Where a board's data came from — mirrors {@link Provenance} in RoleBoard. */
export type DataSource = 'live' | 'simulated';

/** Least-privilege defaults applied when user context is missing. */
const LEAST_PRIVILEGE_ROLE: HccRole = 'HCC.Viewer';
const LEAST_PRIVILEGE_SCOPE: HospitalScope = 'aggregated';

/** Default forecast/observation window (matches the golden-thread default). */
export const DEFAULT_WINDOW_HOURS = 72;

/**
 * The subset of the role lens the envelope needs. Structurally compatible with
 * `useRoleLens()`'s value, but decoupled so `buildEnvelope` stays a pure
 * function testable without React.
 */
export interface RoleLensLike {
  heldRoles: HccRole[];
  activeRole: HccRole;
  capabilities: { hospitalScope: HospitalScope };
}

export interface ContextEnvelope {
  /** Object id of the signed-in user; `null` when unauthenticated. */
  userOid: string | null;
  /** All demo roles the user actually holds. */
  heldRoles: HccRole[];
  /** The active role lens (never elevated beyond a held role). */
  activeRole: HccRole;
  /** Resolved hospital data scope; the RLS filter key. */
  hospitalScope: HospitalScope;
  /** Live golden-source vs simulated dataset. */
  dataSource: DataSource;
  /** The board-agent this turn is scoped to; `null` outside a board. */
  agent: AgentId | null;
  /** Forecast/observation window in hours. */
  windowHours: number;
}

/**
 * Build the per-request {@link ContextEnvelope} from the signed-in user's
 * claims and active role lens.
 *
 * @param claims      Parsed ID-token claims (or `null`/`undefined` when unauthenticated).
 * @param lens        The active role lens (or `null`/`undefined` before it loads).
 * @param dataSource  Live vs simulated data-source preference. Defaults to `simulated`.
 * @param agent       The board-agent this turn targets. Defaults to `null`.
 * @param windowHours Forecast/observation window. Defaults to {@link DEFAULT_WINDOW_HOURS}.
 */
export function buildEnvelope(
  claims: ParsedClaims | null | undefined,
  lens: RoleLensLike | null | undefined,
  dataSource: DataSource = 'simulated',
  agent: AgentId | null = null,
  windowHours: number = DEFAULT_WINDOW_HOURS,
): ContextEnvelope {
  const heldRoles =
    lens && lens.heldRoles.length > 0 ? lens.heldRoles : [LEAST_PRIVILEGE_ROLE];
  const activeRole = lens?.activeRole ?? LEAST_PRIVILEGE_ROLE;
  const hospitalScope = lens?.capabilities.hospitalScope ?? LEAST_PRIVILEGE_SCOPE;

  return {
    userOid: claims?.oid ?? null,
    heldRoles,
    activeRole,
    hospitalScope,
    dataSource,
    agent,
    windowHours,
  };
}
