import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData } from '../../../../journey/RoleBoard';
import type { BedManagerPayload } from '../../../../data/roleboard/bed-manager-data';
import { loadBedManager } from '../../../../data/roleboard/golden-source-client';

/** Sprint 2 (parity) — the bmca RoleBoard implementation (bed reallocation). */
export const bedManagerBoard: RoleBoard<BedManagerPayload> = {
  agent: 'bmca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadBedManager(scope, mode),
  insights: (data: RoleBoardData<BedManagerPayload>) =>
    data.payload.reallocations.map((r) => ({
      id: r.id,
      label: i18n.t('insight.bedShift', { beds: r.beds, fromWard: r.fromWard, toWard: r.toWard }),
      context: {
        reallocation: r.id,
        fromWard: r.fromWard,
        toWard: r.toWard,
        beds: r.beds,
      },
    })),
  toHandoff: (data: RoleBoardData<BedManagerPayload>) => ({
    fromAgent: 'bmca-agent',
    headline: `${data.payload.bedsReallocated} beds reallocated, site still ${data.payload.residualBeds} beds`,
    metrics: { bedsReallocated: data.payload.bedsReallocated, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Bed reallocation',
    loopBackToOoa: false,
  }),
};
