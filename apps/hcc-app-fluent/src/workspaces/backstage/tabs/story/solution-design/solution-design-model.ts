import type { TFunction } from 'i18next';
import type { ContextInsight } from '../../../../../journey/RoleBoard';
import type { GroundedReco } from '../../../../../copilot-rail/reco';

/** Sprint 36 intake — the IQ operating model catalog (design sections 2-4). No PHI, no live values. */
export type IqPlaneId = 'work' | 'process' | 'foundry' | 'fabric' | 'devsecops' | 'gov' | 'sec';
export type CapabilityTier = 'mvp' | 'target';

export interface Capability {
  id: string;
  label: string;
  tier: CapabilityTier;
}

export interface IqPlane {
  id: IqPlaneId;
  kind: 'layer' | 'lane';
  label: string;
  tagline: string;
  /** Left-accent + icon-tile colour (brandkit). */
  accent: string;
  /** AA-safe text colour on white. */
  text: string;
  capabilities: readonly Capability[];
}

export interface SolutionDesignContext {
  scope: IqPlaneId | 'model';
  kind: 'plane' | 'capability';
  capabilityId?: string;
  tier?: CapabilityTier;
  source: 'backstage-solution-design';
}

const cap = (id: string, label: string, tier: CapabilityTier): Capability => ({ id, label, tier });

export const IQ_PLANES: readonly IqPlane[] = [
  {
    id: 'work',
    kind: 'layer',
    label: 'Work IQ',
    tagline: 'experience & role-based control plane',
    accent: '#17B890',
    text: '#12765F',
    capabilities: [
      cap('work-command-center', 'Fluent UI command center', 'mvp'),
      cap('work-copilot-rail', 'In-app Copilot rail', 'mvp'),
      cap('work-role-surfaces', 'Role surfaces (6 copilots)', 'mvp'),
      cap('work-hitl', 'Agent-boss HITL approval', 'mvp'),
      cap('work-m365', 'Work IQ M365 context', 'target'),
    ],
  },
  {
    id: 'process',
    kind: 'layer',
    label: 'Process IQ',
    tagline: 'patient-flow journey through the role copilots',
    accent: '#1FA9D6',
    text: '#176C8A',
    capabilities: [
      cap('process-journey', 'OOA -> DCA -> BMCA -> ORSA -> SBA -> CSA', 'mvp'),
      cap('process-golden-thread', 'Golden-thread steering', 'mvp'),
      cap('process-handoffs', 'Cross-role handoffs', 'mvp'),
      cap('process-whatif', 'What-if simulation overlay', 'target'),
    ],
  },
  {
    id: 'foundry',
    kind: 'layer',
    label: 'Foundry IQ',
    tagline: 'orchestrated role agents, closed-loop learning',
    accent: '#365B7D',
    text: '#365B7D',
    capabilities: [
      cap('foundry-orchestrator', 'Copilot orchestrator', 'mvp'),
      cap('foundry-agents', 'Agents per role (x6 + PO + BVA)', 'mvp'),
      cap('foundry-grounded', 'Grounded on GroundedChunk', 'mvp'),
      cap('foundry-closed-loop', 'Closed-loop learning', 'mvp'),
    ],
  },
  {
    id: 'fabric',
    kind: 'layer',
    label: 'Fabric IQ',
    tagline: 'ontology, semantic data & steering signals',
    accent: '#1FA9D6',
    text: '#176C8A',
    capabilities: [
      cap('fabric-medallion', 'Medallion + Direct Lake', 'mvp'),
      cap('fabric-data-agents', 'Data Agents (da_hospital_capacity)', 'mvp'),
      cap('fabric-dq-gate', 'Data Quality gate + trust score', 'mvp'),
      cap('fabric-ontology-ga', 'Ontology (GA)', 'target'),
      cap('fabric-ingestion', 'KIS / Epic / SAP ingestion', 'target'),
    ],
  },
  {
    id: 'devsecops',
    kind: 'layer',
    label: 'DevSecOps IQ',
    tagline: 'a product team of agents that build agents',
    accent: '#6B7A88',
    text: '#4A5A68',
    capabilities: [
      cap('devsecops-agent-boss', 'Human agent boss (gated)', 'mvp'),
      cap('devsecops-github', 'GitHub delivery plane + CLI Copilot', 'mvp'),
      cap('devsecops-mcp', 'MCP allow-list', 'mvp'),
      cap('devsecops-build-relatives', 'Agents build their Foundry-IQ relatives', 'mvp'),
    ],
  },
  {
    id: 'gov',
    kind: 'lane',
    label: 'Governance',
    tagline: 'policy & compliance',
    accent: '#5A6CF0',
    text: '#4A46C7',
    capabilities: [
      cap('gov-residency', 'Swiss residency', 'mvp'),
      cap('gov-advisory', 'Advisory-only', 'mvp'),
      cap('gov-no-phi', 'No-PHI', 'mvp'),
      cap('gov-evidence', 'Evidence audit', 'mvp'),
      cap('gov-dsg', 'DSG / CH-C01..C10', 'mvp'),
    ],
  },
  {
    id: 'sec',
    kind: 'lane',
    label: 'Security',
    tagline: 'Zero Trust protection',
    accent: '#E30613',
    text: '#C70713',
    capabilities: [
      cap('sec-zero-trust', 'Zero Trust', 'mvp'),
      cap('sec-managed-identity', 'Managed identity', 'mvp'),
      cap('sec-rbac', 'RBAC least-priv', 'mvp'),
      cap('sec-key-vault', 'Key Vault secrets', 'mvp'),
      cap('sec-private-endpoints', 'Private endpoints', 'mvp'),
    ],
  },
];

const SD_CITATIONS = [
  'docs/SD.md',
  'docs/ARCHITECTURE.md',
  'docs/adr/0043-product-owner-agent-foundry-iq-domain.md',
] as const;

export function buildSolutionDesignInsight(ctx: SolutionDesignContext, label: string): ContextInsight {
  return {
    id: `solution-design-${ctx.scope}${ctx.capabilityId ? `-${ctx.capabilityId}` : ''}`,
    label,
    context: { ...ctx },
  };
}

/** Grounded Product Owner Agent answer for a selected plane or capability. */
export function buildSolutionDesignReco(
  plane: IqPlane,
  ctx: SolutionDesignContext,
  t: TFunction,
): GroundedReco {
  const capability =
    ctx.kind === 'capability' ? plane.capabilities.find((c) => c.id === ctx.capabilityId) : undefined;
  const mvp = plane.capabilities.filter((c) => c.tier === 'mvp').map((c) => c.label);
  const target = plane.capabilities.filter((c) => c.tier === 'target').map((c) => c.label);

  const read = capability
    ? `${plane.label} - ${capability.label} (${capability.tier === 'mvp' ? 'delivered' : 'roadmap'}): ${plane.tagline}. This capability is grounded, advisory-only and human-decided.`
    : `${plane.label}: ${plane.tagline}. Delivered today: ${mvp.join('; ')}.${target.length ? ` On the roadmap: ${target.join('; ')}.` : ''}`;

  return {
    agentLabel: 'product-owner-agent',
    contextChip: {
      subject: plane.label,
      qualifiers: [plane.tagline],
      status: t('backstage.story.feedbackLoop.advisoryNote', 'Advisory only'),
      tone: 'signal',
    },
    read,
    levers: plane.capabilities.map((c) => ({
      text: `${c.label} (${c.tier === 'mvp' ? 'delivered' : 'roadmap'})`,
      ...(c.tier === 'mvp'
        ? { impact: { label: 'delivered', tone: 'status' as const } }
        : {}),
    })),
    citations: [...SD_CITATIONS],
    provenance: 'simulated',
  };
}
