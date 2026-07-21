import type { Locale, SiteContent } from './types';
import { de } from './de';

// Registry of available locales. Phase 3 adds en/fr/it here.
// Keep this in sync with astro.config.mjs `i18n.locales`.
export const content: Partial<Record<Locale, SiteContent>> = {
  de,
};

export const defaultLocale: Locale = 'de';

export const localeNames: Record<Locale, string> = {
  de: 'Deutsch',
  en: 'English',
  fr: 'Français',
  it: 'Italiano',
};

/** Locales that currently have published content (drives the language switcher). */
export function availableLocales(): Locale[] {
  return (Object.keys(content) as Locale[]).filter((l) => content[l] !== undefined);
}

export function getContent(locale: Locale): SiteContent {
  return content[locale] ?? de;
}

/** Root-relative URL for a locale's landing page. Default locale is unprefixed. */
export function localeHref(locale: Locale): string {
  return locale === defaultLocale ? '/' : `/${locale}/`;
}
