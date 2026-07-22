import { CsaRoleGuard } from './CsaRoleGuard';
import { CsaWizard } from './CsaWizard';

/**
 * Sprint 20 M5 — CSA surface.
 *
 * Wraps the existing Sprint 16 CSA wizard with its role guard behind `/main/crisis`.
 * The guard (design spec §8) renders a friendly deny message for callers
 * without a CSA-authorised role; the outer section is always present so the
 * surface has a stable test/anchor id.
 */
export function CsaView() {
  return (
    <section data-testid="csa-view">
      <CsaRoleGuard>
        <CsaWizard />
      </CsaRoleGuard>
    </section>
  );
}
