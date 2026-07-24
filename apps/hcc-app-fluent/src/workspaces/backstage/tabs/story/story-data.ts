/**
 * Sprint 20 — Backstage "Story" tab data.
 *
 * All values are Tier-1 repo-grounded: derived from the committed evidence
 * fixture via `loadEvidenceDataset()` or from repo-invariant constants.
 * No values are inlined as literals — every stat tile carries source + asOf +
 * provenance (FR-CX-004, FR-CX-006, NFR-GOV-006). The 8 runtime copilots
 * mirror AGENTS.md §1 registry.
 */
import { loadEvidenceDataset } from '../../../../data/evidence/evidence-service';
import type { EvidenceDataset } from '../../../../data/evidence/evidence-types';

// ---------------------------------------------------------------------------
// Stat tile types
// ---------------------------------------------------------------------------

export type TileProvenance = 'snapshot' | 'live' | 'invariant';

export interface StoryStatTile {
  id: string;
  labelKey: string;
  /** Derived at call time — never a literal. */
  value: number | string;
  source: string;
  asOf: string;
  provenance: TileProvenance;
}

// ---------------------------------------------------------------------------
// Repo-invariant constants (validated by structure, not asserted as literals)
// ---------------------------------------------------------------------------

/**
 * HITL gate: 100% of deploy/delete side-effect actions require an explicit
 * human `approved-to-apply` comment on the agent's draft PR/issue before the
 * MCP call fires (AGENTS.md §4, copilot-instructions.md §3).
 * This value is an invariant enforced by the agent-prompt contract, not a
 * measured metric — stamp as 'invariant'.
 */
export const HITL_GATE_PCT = 100 as const;

/**
 * PHI-zero invariant: only synthetic patient identifiers (`PT-xxxx`) are used
 * throughout the platform — no real patient data is stored or displayed
 * (FR-CX-004, docs/SECURITY.md §4).
 */
export const PHI_COUNT = 0 as const;

// ---------------------------------------------------------------------------
// Stat tiles
// ---------------------------------------------------------------------------

/**
 * Build the stat tile row for the Story tab.
 * Every tile is derived from `dataset` or a validated constant — no literals.
 */
export function storyStatTiles(dataset: EvidenceDataset = loadEvidenceDataset()): StoryStatTile[] {
  const asOf = dataset.generatedAt.slice(0, 10); // "YYYY-MM-DD" from the fixture

  return [
    {
      id: 'adr-count',
      labelKey: 'backstage.story.stats.adrCount',
      value: dataset.adrs.length,
      source: 'docs/adr/*.md → evidence-demo.json',
      asOf,
      provenance: 'snapshot',
    },
    {
      id: 'bom-count',
      labelKey: 'backstage.story.stats.bomCount',
      value: dataset.boms.length,
      source: 'docs/bom.yaml → evidence-demo.json',
      asOf,
      provenance: 'snapshot',
    },
    {
      id: 'requirements-tracked',
      labelKey: 'backstage.story.stats.requirementsTracked',
      value: dataset.requirements.length,
      source: 'docs/PRD.md §7 → evidence-demo.json',
      asOf,
      provenance: 'snapshot',
    },
    {
      id: 'hitl-pct',
      labelKey: 'backstage.story.stats.hitlPct',
      value: `${HITL_GATE_PCT}%`,
      source: 'AGENTS.md §4 · approved-to-apply gate',
      asOf,
      provenance: 'invariant',
    },
    {
      id: 'phi-count',
      labelKey: 'backstage.story.stats.phiCount',
      value: PHI_COUNT,
      source: 'docs/SECURITY.md §4 · synthetic-data constant',
      asOf,
      provenance: 'invariant',
    },
  ];
}

// ---------------------------------------------------------------------------
// 8-copilot roster (mirrors AGENTS.md §1 runtime-hosted agents)
// ---------------------------------------------------------------------------

export interface CopilotRosterEntry {
  name: string;
  displayName: string;
  ceiling: 'read' | 'write' | 'deploy' | 'delete';
  lane: string;
}

/**
 * The 8 runtime copilots loaded by the Sprint 13 Container Apps agent-host.
 * Source: AGENTS.md §1 registry (rows where runtime: is agent-host).
 * Count must equal COPILOT_ROSTER.length === 8 — do NOT use a literal 8 in
 * the UI; derive the count from this array.
 */
export const COPILOT_ROSTER: CopilotRosterEntry[] = [
  { name: 'bmca-agent',         displayName: 'BMCA',         ceiling: 'write',  lane: 'Bed management' },
  { name: 'ooa-agent',          displayName: 'OOA',          ceiling: 'write',  lane: 'Occupancy' },
  { name: 'dca-agent',          displayName: 'DCA',          ceiling: 'write',  lane: 'Discharge' },
  { name: 'orsa-agent',         displayName: 'ORSA',         ceiling: 'write',  lane: 'OR steering' },
  { name: 'sba-agent',          displayName: 'SBA',          ceiling: 'write',  lane: 'Staffing' },
  { name: 'csa-agent',          displayName: 'CSA',          ceiling: 'deploy', lane: 'Crisis' },
  { name: 'data-quality-agent', displayName: 'Data Quality', ceiling: 'write',  lane: 'Data platform' },
  { name: 'onboarding-agent',   displayName: 'Onboarding',   ceiling: 'write',  lane: 'Platform' },
];

/** Source annotation for the roster. */
export const COPILOT_ROSTER_SOURCE = 'AGENTS.md §1 registry' as const;

// ---------------------------------------------------------------------------
// Delivery strips (editorial — i18n-keyed stage lists)
// ---------------------------------------------------------------------------

export interface DeliveryStage {
  key: string;
  labelKey: string;
}

/** PLAN → SPEC → BUILD → REVIEW → RELEASE — software delivery lifecycle */
export const PLAN_TO_RELEASE: DeliveryStage[] = [
  { key: 'plan',    labelKey: 'backstage.story.delivery.plan.plan' },
  { key: 'spec',    labelKey: 'backstage.story.delivery.plan.spec' },
  { key: 'build',   labelKey: 'backstage.story.delivery.plan.build' },
  { key: 'review',  labelKey: 'backstage.story.delivery.plan.review' },
  { key: 'release', labelKey: 'backstage.story.delivery.plan.release' },
];

/** DEV → SIT → PROD — environment promotion strip */
export const DEV_TO_PROD: DeliveryStage[] = [
  { key: 'dev',  labelKey: 'backstage.story.delivery.env.dev' },
  { key: 'sit',  labelKey: 'backstage.story.delivery.env.sit' },
  { key: 'prod', labelKey: 'backstage.story.delivery.env.prod' },
];
