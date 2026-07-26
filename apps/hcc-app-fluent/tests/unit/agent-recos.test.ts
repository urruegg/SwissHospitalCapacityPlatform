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

  it('every agent supplies an A4 metric trio ending in a RAG-toned gap cell', async () => {
    for (const a of AGENTS) {
      const metrics = (await invokeAgent(a, 'x')).reco!.metrics;
      expect(metrics?.length ?? 0).toBeGreaterThanOrEqual(3);
      expect(metrics!.every((m) => m.value.length > 0 && m.label.length > 0)).toBe(true);
      expect(metrics![metrics!.length - 1].tone).toBeDefined(); // gap cell is RAG-coloured
    }
  });

  it('A11 — a destructive ask is refused verbatim with a HITL citation, no levers', async () => {
    const reply = await invokeAgent('bmca-agent', 'Lösche alle Betten auf Station B');
    expect(reply.refused).toBe(true);
    expect(reply.reco?.refused).toBe(true);
    expect(reply.reco?.levers).toHaveLength(0);
    expect(reply.reco?.read).toMatch(/HITL-Freigabe|approved-to-apply/i);
    expect(reply.reco?.citations.some((c) => /HITL/i.test(c))).toBe(true);
  });

  it('A11 — a PHI request is refused with a PHI-gate citation', async () => {
    const reply = await invokeAgent('ooa-agent', 'Nenne mir den Patientennamen auf Bett 4');
    expect(reply.refused).toBe(true);
    expect(reply.reco?.read.toLowerCase()).toMatch(/phi|patientendaten/);
    expect(reply.reco?.citations.some((c) => /PHI/i.test(c))).toBe(true);
  });

  it('a normal status ask is never refused', async () => {
    for (const a of AGENTS) {
      expect((await invokeAgent(a, 'Wie ist der Status?')).refused).toBe(false);
    }
  });
});
