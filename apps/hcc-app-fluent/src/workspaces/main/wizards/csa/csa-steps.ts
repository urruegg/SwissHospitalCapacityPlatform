/**
 * Sprint 16.1 · S16.5 — CSA wizard step definitions + type surface.
 *
 * Pure module; unit-tested. The wizard is a linear 4-step flow (Prepare → Run →
 * Evaluate → Recommend) per S16 design spec §6-§8. Each step declares its own
 * agent prompt template and HITL requirements so the wizard renderer stays
 * agent-agnostic.
 */

export type CsaStepId = 'prepare' | 'run' | 'evaluate' | 'recommend';

export interface CsaStep {
  id: CsaStepId;
  /** Short label for the stepper (single-word if possible). */
  label: string;
  /** One-line description shown under the label on the current step card. */
  description: string;
  /** Wired = clickable, real behaviour. Stub = renders scaffold + pending badge. */
  status: 'wired' | 'stub';
  /**
   * Deferred-reason label rendered when `status === 'stub'`. Sprint 13 T5
   * documents the MCP-wiring gap so the wizard shows the exact blocker.
   */
  deferredReason?: string;
}

/**
 * Canonical CSA wizard flow. Kept in export so tests + the audit doc reference
 * the same source of truth.
 */
export const CSA_STEPS: readonly CsaStep[] = [
  {
    id: 'prepare',
    label: 'Prepare',
    description:
      'Describe the scenario; the agent retrieves similar cases from Cosmos and drafts the plan.',
    status: 'wired',
  },
  {
    id: 'run',
    label: 'Run',
    description:
      'Trigger csa-simulate.ipynb on the Fabric medallion. Returns a runId immediately (async).',
    status: 'stub',
    deferredReason:
      'Real MCP tool execution (fabric-mcp.run-notebook) waits on the Sprint 13 T5 MCP-wiring completion.',
  },
  {
    id: 'evaluate',
    label: 'Evaluate',
    description:
      'Poll the simulation output; classifier assigns tier + summarises bed-day impact.',
    status: 'stub',
    deferredReason:
      'Depends on Run completing + cosmos-mcp.read-item wiring (Sprint 13 T5).',
  },
  {
    id: 'recommend',
    label: 'Recommend',
    description:
      'Draft the recommendation as a PR into docs/csa/runs/. HITL-04 gate mandatory.',
    status: 'stub',
    deferredReason:
      'Depends on github-mcp.create-pull-request wiring + human approval (Sprint 13 T5).',
  },
];

/** Look up a step by id; throws if unknown so callers fail loudly. */
export function csaStepById(id: CsaStepId): CsaStep {
  const step = CSA_STEPS.find((s) => s.id === id);
  if (!step) throw new Error(`unknown csa step id: ${id}`);
  return step;
}

/**
 * Sample recommendation PRs merged during Sprint 16 T4 — kept in a static list
 * for the Recommend step's read-only reference view (design spec §8 asked for
 * the Recommend step to render sample recs from `docs/csa/runs/`).
 */
export interface CsaSampleRecommendation {
  slug: string;
  title: string;
  scenarioTier: 1 | 2 | 3;
  /** GitHub blob URL (relative — resolved by the Fluent app at render). */
  path: string;
}

export const CSA_SAMPLE_RECOMMENDATIONS: readonly CsaSampleRecommendation[] = [
  {
    slug: 'cyberattack-hospital-services',
    title: 'Cyberattack on hospital services (Q1)',
    scenarioTier: 3,
    path: 'docs/csa/runs/2026-07-09-cyberattack-hospital-services.md',
  },
  {
    slug: 'pediatric-virus-surge-rsv',
    title: 'Pediatric virus surge — RSV (Q3)',
    scenarioTier: 2,
    path: 'docs/csa/runs/2026-07-09-pediatric-virus-surge-rsv.md',
  },
  {
    slug: 'summer-heatwave-demand-surge',
    title: 'Summer heatwave demand surge (Q2)',
    scenarioTier: 2,
    path: 'docs/csa/runs/2026-07-09-summer-heatwave-demand-surge.md',
  },
];
