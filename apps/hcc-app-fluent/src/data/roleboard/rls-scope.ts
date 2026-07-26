import type { HospitalScope } from '../../auth/rbac-model';
import type { ContextEnvelope } from '../../context/context-envelope';

/**
 * Simulated row-level security for Sprint 29 M5.
 *
 * The live row-level-security boundary runs in the Fabric semantic model in
 * SIT. This app-side mirror is deliberately config-agnostic and follows the
 * same design contract from design §4.3/§4.4: the `ContextEnvelope`
 * `hospitalScope` is the single filter key for site-tagged rows.
 *
 * Least-privilege role fallback is handled when an envelope is constructed
 * (`buildEnvelope(null, null)` yields Viewer / aggregated). A wholly absent
 * envelope is different: the M3 single-ingress guard refuses it upstream, and
 * this helper returns no rows to avoid leaking a wider scope than the caller
 * proved. When live endpoints are enabled, the same scope contract lifts to
 * Fabric RLS via config without code changes (ADR-0052: config, not code).
 */
export interface HospitalScoped {
  hospital: HospitalScope;
}

export function applyRlsScope<T extends HospitalScoped>(
  rows: readonly T[],
  envelope: ContextEnvelope | null | undefined,
): T[] {
  if (!envelope) {
    return [];
  }

  if (envelope.hospitalScope === 'aggregated') {
    return [...rows];
  }

  return rows.filter((row) => row.hospital === envelope.hospitalScope);
}

export function rlsScopeOf(
  envelope: ContextEnvelope | null | undefined,
): HospitalScope | 'denied' {
  return envelope?.hospitalScope ?? 'denied';
}
