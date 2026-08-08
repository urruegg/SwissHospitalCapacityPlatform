/**
 * Canonical BVA figures — single source of truth for every BVA number shown in
 * the app (Start hero references, the Backstage `BvaDecisionSection`, and any
 * future surface). Values are transcribed verbatim from **docs/BVA.md v2.0.0
 * (Frontier-informed)** and `data/master-data/bva/*.csv`, so a later sprint can
 * bind these constants to Fabric gold tables (`gold.bva_fact_*`) without
 * touching any consuming component.
 *
 * ROM / evidence-based estimate figures only — no PHI. When docs/BVA.md is
 * re-baselined, update this file (and only this file) plus its unit test.
 *
 * Sources:
 *  - docs/BVA.md §6 (Business Value Model), §7.1 (ROI comparison), §7.2
 *    (Sensitivity — Frontier-informed model)
 *  - data/master-data/bva/fact_roi_scenario.csv (rows SC-V2-*)
 *  - data/master-data/bva/fact_value_lever.csv (rows VL-00*)
 */

/** Model baseline used for the headline decision figures. */
export const BVA_MODEL_VERSION = 'v2.0.0';
/** Reporting currency for every BVA figure. */
export const BVA_CURRENCY = 'CHF';

// --- One-time build cost (docs/BVA.md §7.1) ---
export const BVA_ONE_TIME_FRONTIER = 780_000;
export const BVA_ONE_TIME_ROM = 1_300_000;

// --- Annual run cost (identical in both models, docs/BVA.md §7.1) ---
export const BVA_ANNUAL_RUN_COST = 1_250_000;

// --- Annual benefit (docs/BVA.md §6) ---
export const BVA_GROSS_ANNUAL_BENEFIT = 3_820_000;
export const BVA_NET_ANNUAL_BENEFIT = 2_570_000;

// --- 3-year total cost of ownership (docs/BVA.md §7.1) ---
export const BVA_TCO_3YR_FRONTIER = 4_530_000;
export const BVA_TCO_3YR_ROM = 5_050_000;
/** Frontier-informed 3-year TCO variance vs the ROM baseline (negative = under budget). */
export const BVA_TCO_VARIANCE_PCT = -10.3;

// --- 3-year benefit / net value (docs/BVA.md §7.1) ---
export const BVA_GROSS_BENEFIT_3YR = 11_460_000;
export const BVA_NET_VALUE_3YR_FRONTIER = 6_930_000;
export const BVA_NET_VALUE_3YR_ROM = 6_410_000;

// --- 3-year ROI (docs/BVA.md §7.1) ---
export const BVA_ROI_3YR_FRONTIER_PCT = 153;
export const BVA_ROI_3YR_ROM_PCT = 127;

// --- Simple payback in months (docs/BVA.md §7.1) ---
export const BVA_PAYBACK_MONTHS_FRONTIER = 3.6;
export const BVA_PAYBACK_MONTHS_ROM = 6.1;

/** A single sensitivity scenario row (docs/BVA.md §7.2, Frontier-informed). */
export interface BvaScenarioFigures {
  id: string;
  label: string;
  annualBenefit: number;
  annualRunCost: number;
  oneTimeCost: number;
  threeYearTco: number;
  threeYearRoiPct: number;
  paybackMonths: number;
}

/**
 * Sensitivity scenarios — Frontier-informed model (docs/BVA.md §7.2 /
 * fact_roi_scenario.csv rows SC-V2-*). `base-rom` is the executive go/no-go
 * baseline; its `annualBenefit` equals the sum of {@link BVA_VALUE_LEVERS}.
 */
export const BVA_SCENARIOS: readonly BvaScenarioFigures[] = [
  {
    id: 'conservative',
    label: 'Conservative',
    annualBenefit: 2_600_000,
    annualRunCost: 1_320_000,
    oneTimeCost: 900_000,
    threeYearTco: 4_860_000,
    threeYearRoiPct: 60,
    paybackMonths: 8.4,
  },
  {
    id: 'base-rom',
    label: 'Base (Frontier-informed)',
    annualBenefit: 3_820_000,
    annualRunCost: 1_250_000,
    oneTimeCost: 780_000,
    threeYearTco: 4_530_000,
    threeYearRoiPct: 153,
    paybackMonths: 3.6,
  },
  {
    id: 'upside',
    label: 'Upside',
    annualBenefit: 5_000_000,
    annualRunCost: 1_230_000,
    oneTimeCost: 700_000,
    threeYearTco: 4_390_000,
    threeYearRoiPct: 242,
    paybackMonths: 2.2,
  },
];

/** A single value-lever annual-benefit driver (docs/BVA.md §6). */
export interface BvaLeverFigures {
  id: string;
  annualBenefit: number;
}

/**
 * Value levers — ROM annual-benefit drivers (docs/BVA.md §6 /
 * fact_value_lever.csv rows VL-00*). The sum equals
 * {@link BVA_GROSS_ANNUAL_BENEFIT}.
 */
export const BVA_VALUE_LEVERS: readonly BvaLeverFigures[] = [
  { id: 'bed-day-discharge-throughput', annualBenefit: 1_650_000 },
  { id: 'command-center-productivity', annualBenefit: 980_000 },
  { id: 'staffing-overtime-reduction', annualBenefit: 620_000 },
  { id: 'integration-reliability', annualBenefit: 350_000 },
  { id: 'compliance-audit-efficiency', annualBenefit: 220_000 },
];

/** Formats a whole-CHF figure as a compact `X.XXM` string (e.g. 6_930_000 -> "6.93M"). */
export function toMillionsLabel(value: number): string {
  return `${(value / 1_000_000).toFixed(2)}M`;
}
