import { describe, expect, it } from 'vitest';
import de from '../../../i18n/de.json';
import en from '../../../i18n/en.json';
import fr from '../../../i18n/fr.json';
import itLocale from '../../../i18n/it.json';
import { agentForRoute } from '../../../shell/planes/agent-context-map';
import {
  CIO_DECISIONS,
  FRONTIER_ROSTER,
  FRONTIER_HOSPITALS,
  NINETY_DAY_PHASES,
  START_SECTIONS,
  WORK_MODES,
} from './start-content';

function collectLocaleStrings(value: unknown): string[] {
  if (typeof value === 'string') return [value];
  if (Array.isArray(value)) return value.flatMap(collectLocaleStrings);
  if (value && typeof value === 'object') return Object.values(value).flatMap(collectLocaleStrings);
  return [];
}

function frontierLocaleText(locale: unknown): string {
  return collectLocaleStrings(
    (locale as { start: { frontier?: unknown } }).start.frontier,
  ).join(' ');
}

function staticFrontierLocale(locale: unknown) {
  return (
    locale as {
      start: {
        frontier?: {
          workChart?: { modes?: Record<string, unknown> };
          cioWhyNow?: { decisions?: Record<string, unknown> };
          hospitals?: {
            sites?: Record<string, unknown>;
            roster?: { entries?: Record<string, unknown> };
          };
          ninetyDay?: { phases?: Record<string, unknown> };
        };
      };
    }
  ).start.frontier;
}

describe('START_SECTIONS', () => {
  it('defines the approved Sprint 37 frontier section order', () => {
    expect(START_SECTIONS.map(({ id }) => id)).toEqual([
      'hero',
      'challenger',
      'vision',
      'work-chart',
      'cio-why-now',
      'hospitals',
      'patient-path',
      'ninety-day',
      'bva',
    ]);
  });

  it('keeps the German frontier locale content localized instead of mirroring English', () => {
    expect(frontierLocaleText(de)).not.toBe(frontierLocaleText(en));
  });

  it.each([
    ['en', en],
    ['de', de],
    ['fr', fr],
    ['it', itLocale],
  ])('keeps %s start.frontier locale content free of PHI-shaped strings', (_language, locale) => {
    expect(frontierLocaleText(locale)).not.toMatch(/patient name|birth|mrn|ssn/i);
  });

  it.each([
    ['en', en],
    ['de', de],
    ['fr', fr],
    ['it', itLocale],
  ])('provides complete %s static Frontier content', (_language, locale) => {
    const frontier = staticFrontierLocale(locale);
    expect(Object.keys(frontier?.workChart?.modes ?? {})).toEqual([
      'humans',
      'agents',
      'on-demand',
    ]);
    expect(Object.keys(frontier?.cioWhyNow?.decisions ?? {})).toEqual([
      'bed-allocation',
      'or-slots',
      'staffing',
      'discharge',
      'transfers',
      'crisis',
      'data-quality',
    ]);
    expect(Object.keys(frontier?.hospitals?.sites ?? {})).toEqual([
      'curanova',
      'curalp',
      'vialta',
    ]);
    expect(Object.keys(frontier?.hospitals?.roster?.entries ?? {})).toEqual([
      'ooa',
      'dca',
      'bmca',
      'csa',
      'orsa',
      'sba',
      'data-quality',
      'po',
    ]);
    expect(Object.keys(frontier?.ninetyDay?.phases ?? {})).toEqual([
      'frame-ground',
      'build-prove',
      'operate-scale',
    ]);
  });

  it('defines typed static content with the required cardinality and no PHI-shaped strings', () => {
    expect(WORK_MODES).toHaveLength(3);
    expect(CIO_DECISIONS).toHaveLength(7);
    expect(FRONTIER_HOSPITALS).toHaveLength(3);
    expect(FRONTIER_ROSTER).toHaveLength(8);
    expect(NINETY_DAY_PHASES).toHaveLength(3);
    expect(
      JSON.stringify({
        workModes: WORK_MODES,
        cioDecisions: CIO_DECISIONS,
        hospitals: FRONTIER_HOSPITALS,
        roster: FRONTIER_ROSTER,
        roadmap: NINETY_DAY_PHASES,
      }),
    ).not.toMatch(/patient name|date of birth|birth date|mrn|ssn/i);
  });

  it('keeps the seven approved CIO decisions in BOM order', () => {
    expect(CIO_DECISIONS.map(({ id }) => id)).toEqual([
      'bed-allocation',
      'or-slots',
      'staffing',
      'discharge',
      'transfers',
      'crisis',
      'data-quality',
    ]);
  });

  it('uses stable semantic IDs in every static Frontier translation path', () => {
    expect(WORK_MODES.map(({ titleKey }) => titleKey)).toEqual([
      'start.frontier.workChart.modes.humans.title',
      'start.frontier.workChart.modes.agents.title',
      'start.frontier.workChart.modes.on-demand.title',
    ]);
    expect(CIO_DECISIONS.map(({ decisionKey }) => decisionKey)).toEqual(
      CIO_DECISIONS.map(
        ({ id }) => `start.frontier.cioWhyNow.decisions.${id}.decision`,
      ),
    );
    expect(FRONTIER_HOSPITALS.map(({ nameKey }) => nameKey)).toEqual(
      FRONTIER_HOSPITALS.map(
        ({ id }) => `start.frontier.hospitals.sites.${id}.name`,
      ),
    );
    expect(FRONTIER_ROSTER.map(({ abbrKey }) => abbrKey)).toEqual(
      FRONTIER_ROSTER.map(
        ({ id }) => `start.frontier.hospitals.roster.entries.${id}.abbr`,
      ),
    );
    expect(NINETY_DAY_PHASES.map(({ titleKey }) => titleKey)).toEqual(
      NINETY_DAY_PHASES.map(
        ({ id }) => `start.frontier.ninetyDay.phases.${id}.title`,
      ),
    );
    NINETY_DAY_PHASES.flatMap(({ outcomeKeys }) => outcomeKeys).forEach((outcomeKey) => {
      expect(outcomeKey).not.toMatch(/\.outcomes\.\d+$/);
    });
  });
});

describe('agentForRoute', () => {
  it('docks /start to the Product Owner Agent rail', () => {
    expect(agentForRoute('/start')).toBe('product-owner-agent');
  });
});
