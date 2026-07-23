import type { Provenance } from '../journey/RoleBoard';

/** Reco status/severity tones. */
export type ChipTone = 'over' | 'watch' | 'ok' | 'blocked' | 'pending' | 'ranked' | 'signal';

/** Lever impact tones. */
export type ImpactTone = 'beds' | 'buffer' | 'time' | 'routing' | 'trust' | 'probability' | 'status';

/** Primary-CTA behaviour. */
export type CtaKind = 'handoff' | 'action' | 'navigate';

/** Fluent Badge `color` values used by the rail. */
export type BadgeColor =
  | 'brand' | 'danger' | 'important' | 'informative' | 'severe' | 'subtle' | 'success' | 'warning';

export interface RecoContextChip {
  subject: string;
  qualifiers?: string[];
  status?: string;
  tone: ChipTone;
}

export interface RecoLever {
  text: string;
  impact?: { label: string; tone?: ImpactTone };
}

export interface RecoCta {
  label: string;
  kind: CtaKind;
  target?: string;
  requiresApproval?: boolean;
}

export interface GroundedReco {
  agentLabel: string;
  contextChip: RecoContextChip;
  read: string;
  levers: RecoLever[];
  primaryCta?: RecoCta;
  projection?: string;
  citations: string[];
  provenance: Provenance;
  refused?: boolean;
}

const CHIP_COLORS: Record<ChipTone, BadgeColor> = {
  over: 'danger',
  watch: 'warning',
  ok: 'success',
  blocked: 'severe',
  pending: 'informative',
  ranked: 'brand',
  signal: 'important',
};

const IMPACT_COLORS: Record<ImpactTone, BadgeColor> = {
  beds: 'success',
  buffer: 'success',
  time: 'informative',
  routing: 'brand',
  trust: 'important',
  probability: 'informative',
  status: 'subtle',
};

export function chipBadgeColor(tone: ChipTone): BadgeColor {
  return CHIP_COLORS[tone];
}

export function impactBadgeColor(tone: ImpactTone | undefined): BadgeColor {
  return tone ? IMPACT_COLORS[tone] : 'subtle';
}
