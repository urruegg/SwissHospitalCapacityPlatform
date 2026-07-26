import { describe, it, expect } from 'vitest';
import { invokeAgent } from '../../src/copilot-drawer/agent-manifest';

/**
 * Sprint 27 Step 2 — validates that every role agent's Copilot chat returns a
 * distinct, grounded, PHI-free artefact that exercises the A1–A12 pattern
 * catalogue (context chip, read, levers+impact, CTA, citations). Runs against the
 * deterministic mock (no `VITE_AGENT_HOST_URL` in test).
 */
const AGENTS = ['ooa-agent', 'bmca-agent', 'dca-agent', 'orsa-agent', 'sba-agent', 'csa-agent'] as const;

describe('per-agent chat artefacts', () => {
  it('every role agent returns a grounded artefact with the full stack', async () => {
    for (const a of AGENTS) {
      const reply = await invokeAgent(a, 'Status?');
      expect(reply.reco).toBeDefined();
      const reco = reply.reco!;
      expect(reco.agentLabel.length).toBeGreaterThan(0);
      expect(reco.contextChip.subject.length).toBeGreaterThan(0);
      expect(reco.read.length).toBeGreaterThan(0);
      expect(reco.levers.length).toBeGreaterThan(0);
      expect(reco.levers.every((l) => Boolean(l.impact))).toBe(true); // each lever has an impact delta
      expect(reco.primaryCta).toBeDefined();
      expect(reco.citations.some((c) => c.startsWith('hcp:'))).toBe(true); // >= 1 ontology citation
      expect(reco.refused).toBe(false);
      expect(reco.read.toLowerCase()).not.toMatch(/ahv|geburtsdatum/); // no PHI
    }
  });

  it('read agent (ooa) hands off; write/deploy agents gate the CTA (HITL)', async () => {
    const ooa = (await invokeAgent('ooa-agent', 'x')).reco!;
    expect(ooa.primaryCta?.kind).toBe('handoff');
    expect(ooa.primaryCta?.requiresApproval ?? false).toBe(false);
    for (const a of ['bmca-agent', 'dca-agent', 'orsa-agent', 'sba-agent', 'csa-agent']) {
      const reco = (await invokeAgent(a, 'x')).reco!;
      expect(reco.primaryCta?.requiresApproval).toBe(true);
    }
  });

  it('each agent has a distinct context subject', async () => {
    const subjects = await Promise.all(
      AGENTS.map(async (a) => (await invokeAgent(a, 'x')).reco!.contextChip.subject),
    );
    expect(new Set(subjects).size).toBe(AGENTS.length);
  });
});
