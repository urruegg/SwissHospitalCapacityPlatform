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
 * 1. The "Curavias" brand wordmark — a constant proper noun that is identical
 *    in every locale, so de/fr/it omit that single leaf on purpose
 *    (VISION_BILINGUAL). The vision/mission statements, the time-currency line
 *    and the three guarantee pills are now fully localised per locale and are
 *    therefore asserted, not exempted.
 * 2. Challenger persona deep-narrative — verbatim dated review-session quotes
 *    and reviewer proper nouns (name/org/meta/quote/gloss/addressed/value/
 *    adapted/evidence) are never translated; only each persona's `tag`/`sub`
 *    chrome is localised (isChallengerDeepProse).
 */
const VISION_BILINGUAL = new Set<string>([
  'start.frontier.vision.brand.name',
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
