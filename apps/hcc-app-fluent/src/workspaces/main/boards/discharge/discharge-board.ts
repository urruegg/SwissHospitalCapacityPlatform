import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData } from '../../../../journey/RoleBoard';
import type { DischargePayload } from '../../../../data/roleboard/discharge-data';
import { loadDischarge } from '../../../../data/roleboard/golden-source-client';

/** Sprint 2 (parity) — the dca RoleBoard implementation (discharge readiness). */
export const dischargeBoard: RoleBoard<DischargePayload> = {
  agent: 'dca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadDischarge(scope, mode),
  insights: (data: RoleBoardData<DischargePayload>) =>
    data.payload.candidates
      .filter((c) => c.expedite === true)
      .map((c) => ({
        id: c.id,
        label: i18n.t('insight.dischargeExpedite', { ward: c.ward }),
        context: {
          candidate: c.id,
          ward: c.ward,
          blocker: c.blocker,
          bedsFreeable: c.bedsFreeable,
        },
      })),
  toHandoff: (data: RoleBoardData<DischargePayload>) => ({
    fromAgent: 'dca-agent',
    headline: `${data.payload.bedsFreeable} discharges free beds, site still ${data.payload.residualBeds} beds`,
    metrics: { bedsFreeable: data.payload.bedsFreeable, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Discharge readiness',
    loopBackToOoa: false,
  }),
};
