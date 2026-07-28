import { useEffect } from 'react';
import { useRoleLens } from './role-context';
import { useDataSource } from './data-source-context';
import { buildEnvelope } from './context-envelope';
import { setContextEnvelope } from '../data/roleboard/golden-source-client';
import type { ParsedClaims } from '../auth/claim-parser';

/**
 * Sprint 29 (#424 M1) — keeps the single IQ `ContextEnvelope` in sync with the
 * shell's active role lens and the Live/Simulated toggle.
 *
 * Mounted once under the role + data-source providers. Every live IQ read then
 * carries a consistent `(userOid x activeRole x hospitalScope x dataSource)`
 * envelope, and the single-ingress guard (`iqFetch`) has an envelope to check
 * instead of throwing. Board-agnostic: the per-turn `agent` tier is attached in
 * the send path (Copilot drawer), not here, because a board read scopes by
 * hospital + window, not by agent. Renders nothing.
 */
export function ContextEnvelopeSync(): null {
  const { userOid, heldRoles, activeRole, capabilities } = useRoleLens();
  const { source } = useDataSource();
  const hospitalScope = capabilities.hospitalScope;

  useEffect(() => {
    const claims = { oid: userOid ?? undefined } as ParsedClaims;
    setContextEnvelope(
      buildEnvelope(
        claims,
        { heldRoles, activeRole, capabilities: { hospitalScope } },
        source,
      ),
    );
  }, [userOid, heldRoles, activeRole, hospitalScope, source]);

  return null;
}
