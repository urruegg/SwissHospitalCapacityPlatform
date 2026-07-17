import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import de from './de.json';
import en from './en.json';
import fr from './fr.json';
import it from './it.json';

/**
 * Sprint 20 M6 — four-language i18n (EN / DE / FR / IT) per design spec §2.1.
 * DE default, EN fallback, language choice persisted to `localStorage`
 * (`curavias.lang`).
 */
export const supportedLanguages = ['de', 'en', 'fr', 'it'] as const;
export type SupportedLanguage = (typeof supportedLanguages)[number];

const LANG_STORAGE_KEY = 'curavias.lang';
const saved =
  typeof localStorage !== 'undefined' ? localStorage.getItem(LANG_STORAGE_KEY) : null;

void i18n.use(initReactI18next).init({
  resources: {
    de: { translation: de },
    en: { translation: en },
    fr: { translation: fr },
    it: { translation: it },
  },
  lng: saved ?? 'de',
  fallbackLng: 'en',
  supportedLngs: [...supportedLanguages],
  interpolation: { escapeValue: false },
  returnNull: false,
});

i18n.on('languageChanged', (lng) => {
  if (typeof localStorage !== 'undefined') localStorage.setItem(LANG_STORAGE_KEY, lng);
});

export default i18n;
