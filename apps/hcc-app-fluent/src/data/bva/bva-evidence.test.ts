import { describe, expect, it } from 'vitest';
import {
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaProofPoints,
  bvaSensitivityScenarios,
  bvaTrend,
  bvaValueLevers,
} from './bva-evidence';

const PHI_PATTERN = /patient|ahv|geburtsdatum|dob|ssn/i;

function expectProvenance(entries: Array<{ source: string; asOf: string; powerBiEmbedFallback: boolean }>) {
  for (const entry of entries) {
    expect(entry.source).toBeTruthy();
    expect(entry.asOf).toMatch(/^\d{4}-\d{2}-\d{2}/);
    expect(typeof entry.powerBiEmbedFallback).toBe('boolean');
  }
}

describe('bva-evidence · distinct typed groups (Sprint 37 T3)', () => {
  it('keeps value levers, sensitivity scenarios, and proof points as distinct exports from headline KPIs and trend', () => {
    // Distinct arrays, not aliases/re-exports of each other or of the headline/trend groups.
    expect(bvaValueLevers).not.toBe(bvaHeadlineKpis);
    expect(bvaSensitivityScenarios).not.toBe(bvaTrend.points);
    expect(bvaProofPoints).not.toBe(bvaHeadlineKpis);
    expect(bvaProofPoints).not.toBe(bvaPlanVsActual as unknown as unknown[]);

    // Shape checks: each group carries its own semantic fields, not headline/trend fields.
    for (const lever of bvaValueLevers) {
      expect(lever).toHaveProperty('lever');
      expect(lever).toHaveProperty('annualBenefit');
      expect(lever).toHaveProperty('valueLogic');
      expect(lever).not.toHaveProperty('measure');
      expect(typeof lever.annualBenefit).toBe('number');
    }

    for (const scenario of bvaSensitivityScenarios) {
      expect(scenario).toHaveProperty('scenario');
      expect(scenario).toHaveProperty('annualBenefit');
      expect(scenario).toHaveProperty('annualRunCost');
      expect(scenario).toHaveProperty('threeYearTco');
      expect(scenario).toHaveProperty('threeYearRoiPct');
      expect(scenario).toHaveProperty('comment');
      expect(scenario).not.toHaveProperty('label'); // not a trend point
      expect(typeof scenario.threeYearRoiPct).toBe('number');
    }

    for (const proof of bvaProofPoints) {
      expect(proof).toHaveProperty('claim');
      expect(proof).toHaveProperty('target');
      expect(proof).toHaveProperty('cadence');
      // Qualitative claims must not smuggle in a numeric figure duplicating another group.
      expect(typeof proof.target).toBe('string');
    }
  });

  it('has at least one entry per group and matches the docs/BVA.md ROM figures', () => {
    expect(bvaValueLevers.length).toBeGreaterThanOrEqual(5);
    expect(bvaSensitivityScenarios.length).toBe(3);
    expect(bvaProofPoints.length).toBeGreaterThanOrEqual(3);

    const totalLeverBenefit = bvaValueLevers.reduce((sum, l) => sum + l.annualBenefit, 0);
    // docs/BVA.md "Total Gross Annual Benefit" = 3820000, matching the Base ROM scenario.
    expect(totalLeverBenefit).toBe(3820000);

    const baseRom = bvaSensitivityScenarios.find((s) => s.scenario === 'Base ROM');
    expect(baseRom?.annualBenefit).toBe(totalLeverBenefit);
    expect(baseRom?.threeYearRoiPct).toBe(127);

    const conservative = bvaSensitivityScenarios.find((s) => s.scenario === 'Conservative');
    const upside = bvaSensitivityScenarios.find((s) => s.scenario === 'Upside');
    expect(conservative?.threeYearRoiPct).toBeLessThan(baseRom!.threeYearRoiPct);
    expect(upside?.threeYearRoiPct).toBeGreaterThan(baseRom!.threeYearRoiPct);
  });

  it('carries complete provenance (source + ISO asOf + fallback flag) on every entry', () => {
    expectProvenance(bvaValueLevers);
    expectProvenance(bvaSensitivityScenarios);
    expectProvenance(bvaProofPoints);
  });

  it('cites docs/BVA.md (not the Sprint 15 semantic model) for the new evidence groups', () => {
    for (const lever of bvaValueLevers) {
      expect(lever.source).toContain('docs/BVA.md');
    }
    for (const scenario of bvaSensitivityScenarios) {
      expect(scenario.source).toContain('docs/BVA.md');
    }
    for (const proof of bvaProofPoints) {
      expect(proof.source).toContain('docs/BVA.md');
    }
  });

  it('has unique IDs within each new evidence group', () => {
    const leverIds = bvaValueLevers.map((l) => l.id);
    expect(new Set(leverIds).size).toBe(leverIds.length);

    const scenarioIds = bvaSensitivityScenarios.map((s) => s.id);
    expect(new Set(scenarioIds).size).toBe(scenarioIds.length);

    const proofIds = bvaProofPoints.map((p) => p.id);
    expect(new Set(proofIds).size).toBe(proofIds.length);
  });

  it('contains no PHI-shaped content across the new evidence groups', () => {
    const serialized = JSON.stringify([bvaValueLevers, bvaSensitivityScenarios, bvaProofPoints]).toLowerCase();
    expect(serialized).not.toMatch(PHI_PATTERN);
  });
});
