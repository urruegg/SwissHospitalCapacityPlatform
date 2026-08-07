import { describe, expect, it } from 'vitest';
import en from './en.json';
import de from './de.json';
import fr from './fr.json';
import itLocale from './it.json';

function keys(obj: unknown, prefix = ''): string[] {
  if (obj === null || typeof obj !== 'object') return [prefix];
  return Object.entries(obj as Record<string, unknown>).flatMap(([k, v]) =>
    keys(v, prefix ? `${prefix}.${k}` : k),
  );
}

/**
 * Coverage guard for the START + BACKSTAGE narrative copy blocks.
 *
 * Two governance-documented EN-fallback exceptions are excluded from every
 * locale comparison (they intentionally resolve via i18next `fallbackLng='en'`):
 *
 * 1. Bilingual brand copy in the vision block — the vision/mission statements,
 *    the time-currency line, the three guarantee pills, and the "Curavias"
 *    brand name carry an identical EN|DE value everywhere, so de/fr/it omit
 *    those leaves on purpose (VISION_BILINGUAL).
 * 2. Challenger persona deep-narrative — verbatim dated review-session quotes
 *    and reviewer proper nouns (name/org/meta/quote/gloss/addressed/value/
 *    adapted/evidence) are never translated; only each persona's `tag`/`sub`
 *    chrome is localised (isChallengerDeepProse).
 */
const VISION_BILINGUAL = new Set<string>([
  'start.frontier.vision.brand.name',
  'start.frontier.vision.vision.primary',
  'start.frontier.vision.vision.echo',
  'start.frontier.vision.mission.primary',
  'start.frontier.vision.mission.echo',
  'start.frontier.vision.timeCurrency',
  'start.frontier.vision.timeCurrencyEcho',
  'start.frontier.vision.pills.advisory.label',
  'start.frontier.vision.pills.advisory.echo',
  'start.frontier.vision.pills.human.label',
  'start.frontier.vision.pills.human.echo',
  'start.frontier.vision.pills.swiss.label',
  'start.frontier.vision.pills.swiss.echo',
]);

const isChallengerDeepProse = (k: string): boolean =>
  /^start\.frontier\.challenger\.personas\.[^.]+\.(name|org|meta|quote|gloss|addressed|value|adapted|evidence)(\.|$)/.test(
    k,
  );

const isDocumentedFallback = (k: string): boolean =>
  VISION_BILINGUAL.has(k) || isChallengerDeepProse(k);

/**
 * de is the DEMO reference locale and must reach full parity across the whole
 * START + BACKSTAGE narrative surface (minus the documented EN-fallback keys).
 */
const DE_SCOPE = (k: string): boolean =>
  (k.startsWith('start.frontier.') || k.startsWith('backstage.story.')) &&
  !isDocumentedFallback(k);

/**
 * fr/it are localised for the vision + top-nav chrome delivered in this change.
 * The remaining START/BACKSTAGE surface is a documented, tracked localisation
 * debt (see plan.md / SQL `followups`) and is intentionally NOT asserted here
 * yet — narrowing the scope keeps this guard honest instead of red-listing the
 * whole backlog.
 */
const FR_IT_SCOPE = (k: string): boolean =>
  (k.startsWith('start.frontier.vision.') ||
    k.startsWith('start.frontier.nav.')) &&
  !isDocumentedFallback(k);

function missingFor(locale: unknown, scope: (k: string) => boolean): string[] {
  const enScoped = keys(en).filter(scope);
  const localeKeys = new Set(keys(locale));
  return enScoped.filter((k) => !localeKeys.has(k));
}

describe('i18n coverage for START + BACKSTAGE', () => {
  it('de has full START + BACKSTAGE parity vs en (minus documented fallbacks)', () => {
    expect(missingFor(de, DE_SCOPE)).toEqual([]);
  });

  it.each([
    ['fr', fr],
    ['it', itLocale],
  ])('%s has vision + nav parity vs en (scoped)', (_name, locale) => {
    expect(missingFor(locale, FR_IT_SCOPE)).toEqual([]);
  });
});
