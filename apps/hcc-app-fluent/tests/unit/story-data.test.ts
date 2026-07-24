import { describe, it, expect } from 'vitest';
import { loadEvidenceDataset } from '../../src/data/evidence/evidence-service';
import {
  storyStatTiles,
  COPILOT_ROSTER,
  COPILOT_ROSTER_SOURCE,
  HITL_GATE_PCT,
  PHI_COUNT,
  PLAN_TO_RELEASE,
  DEV_TO_PROD,
} from '../../src/workspaces/backstage/tabs/story/story-data';

describe('storyStatTiles — Tier-1 repo-grounded derivation', () => {
  const dataset = loadEvidenceDataset();
  const tiles = storyStatTiles(dataset);

  it('derives ADR count from dataset.adrs.length (not a literal)', () => {
    const adrTile = tiles.find((t) => t.id === 'adr-count');
    expect(adrTile).toBeDefined();
    expect(adrTile!.value).toBe(dataset.adrs.length);
  });

  it('derives BOM count from dataset.boms.length (not a literal)', () => {
    const bomTile = tiles.find((t) => t.id === 'bom-count');
    expect(bomTile).toBeDefined();
    expect(bomTile!.value).toBe(dataset.boms.length);
  });

  it('derives requirements-tracked from dataset.requirements.length (not a literal)', () => {
    const reqTile = tiles.find((t) => t.id === 'requirements-tracked');
    expect(reqTile).toBeDefined();
    expect(reqTile!.value).toBe(dataset.requirements.length);
  });

  it('ADR count is at least 10 (acceptance floor — dataset is non-trivial)', () => {
    expect(dataset.adrs.length).toBeGreaterThanOrEqual(10);
  });

  it('BOM count is at least 25 (acceptance floor)', () => {
    expect(dataset.boms.length).toBeGreaterThanOrEqual(25);
  });

  it('every stat tile has a non-empty source', () => {
    for (const tile of tiles) {
      expect(tile.source).toBeTruthy();
    }
  });

  it('every stat tile has an asOf in YYYY-MM-DD format', () => {
    for (const tile of tiles) {
      expect(tile.asOf).toMatch(/^\d{4}-\d{2}-\d{2}/);
    }
  });

  it('every stat tile has a provenance field', () => {
    for (const tile of tiles) {
      expect(['snapshot', 'live', 'invariant']).toContain(tile.provenance);
    }
  });

  it('every stat tile has a labelKey starting with backstage.story', () => {
    for (const tile of tiles) {
      expect(tile.labelKey).toMatch(/^backstage\.story\./);
    }
  });

  it('HITL tile value encodes HITL_GATE_PCT (100%)', () => {
    const hitl = tiles.find((t) => t.id === 'hitl-pct');
    expect(hitl).toBeDefined();
    expect(String(hitl!.value)).toContain(String(HITL_GATE_PCT));
  });

  it('PHI tile value encodes PHI_COUNT (0)', () => {
    const phi = tiles.find((t) => t.id === 'phi-count');
    expect(phi).toBeDefined();
    expect(Number(phi!.value)).toBe(PHI_COUNT);
  });

  it('HITL and PHI tiles carry invariant provenance', () => {
    const hitl = tiles.find((t) => t.id === 'hitl-pct');
    const phi  = tiles.find((t) => t.id === 'phi-count');
    expect(hitl!.provenance).toBe('invariant');
    expect(phi!.provenance).toBe('invariant');
  });

  it('snapshot tiles carry snapshot provenance', () => {
    const snapshotIds = ['adr-count', 'bom-count', 'requirements-tracked'];
    for (const id of snapshotIds) {
      const tile = tiles.find((t) => t.id === id);
      expect(tile!.provenance).toBe('snapshot');
    }
  });

  it('asOf is derived from dataset.generatedAt (not hardcoded)', () => {
    const expected = dataset.generatedAt.slice(0, 10);
    for (const tile of tiles) {
      expect(tile.asOf).toBe(expected);
    }
  });
});

describe('COPILOT_ROSTER — 8 runtime agents from AGENTS.md §1', () => {
  it('COPILOT_ROSTER.length === 8 (count derives from array, not a literal)', () => {
    expect(COPILOT_ROSTER.length).toBe(8);
  });

  it('includes all 8 expected agent names', () => {
    const names = COPILOT_ROSTER.map((a) => a.name);
    expect(names).toContain('bmca-agent');
    expect(names).toContain('ooa-agent');
    expect(names).toContain('dca-agent');
    expect(names).toContain('orsa-agent');
    expect(names).toContain('sba-agent');
    expect(names).toContain('csa-agent');
    expect(names).toContain('data-quality-agent');
    expect(names).toContain('onboarding-agent');
  });

  it('every roster entry has a non-empty displayName', () => {
    for (const entry of COPILOT_ROSTER) {
      expect(entry.displayName).toBeTruthy();
    }
  });

  it('every roster entry has a valid ceiling', () => {
    const valid = ['read', 'write', 'deploy', 'delete'] as const;
    for (const entry of COPILOT_ROSTER) {
      expect(valid).toContain(entry.ceiling);
    }
  });

  it('every roster entry has a non-empty lane', () => {
    for (const entry of COPILOT_ROSTER) {
      expect(entry.lane).toBeTruthy();
    }
  });

  it('csa-agent has deploy ceiling (AGENTS.md §1 — approved-to-apply gate)', () => {
    const csa = COPILOT_ROSTER.find((a) => a.name === 'csa-agent');
    expect(csa?.ceiling).toBe('deploy');
  });

  it('ooa-agent has write ceiling (AGENTS.md §1)', () => {
    const ooa = COPILOT_ROSTER.find((a) => a.name === 'ooa-agent');
    expect(ooa?.ceiling).toBe('write');
  });

  it('COPILOT_ROSTER_SOURCE references AGENTS.md §1', () => {
    expect(COPILOT_ROSTER_SOURCE).toMatch(/AGENTS\.md/);
  });
});

describe('Delivery strips', () => {
  it('PLAN_TO_RELEASE has 5 stages ending with release', () => {
    expect(PLAN_TO_RELEASE.length).toBe(5);
    expect(PLAN_TO_RELEASE[PLAN_TO_RELEASE.length - 1].key).toBe('release');
  });

  it('PLAN_TO_RELEASE starts with plan', () => {
    expect(PLAN_TO_RELEASE[0].key).toBe('plan');
  });

  it('DEV_TO_PROD has 3 stages: dev, sit, prod', () => {
    expect(DEV_TO_PROD.length).toBe(3);
    expect(DEV_TO_PROD.map((s) => s.key)).toEqual(['dev', 'sit', 'prod']);
  });

  it('all PLAN_TO_RELEASE stages have i18n keys', () => {
    for (const stage of PLAN_TO_RELEASE) {
      expect(stage.labelKey).toMatch(/^backstage\.story\.delivery\.plan\./);
    }
  });

  it('all DEV_TO_PROD stages have i18n keys', () => {
    for (const stage of DEV_TO_PROD) {
      expect(stage.labelKey).toMatch(/^backstage\.story\.delivery\.env\./);
    }
  });
});
