import { describe, it, expect } from 'vitest';
import i18n from '../../src/i18n';

describe('i18n', () => {
  it('supports EN/DE/FR/IT with DE default and EN fallback', () => {
    expect(i18n.options.supportedLngs).toEqual(
      expect.arrayContaining(['de', 'en', 'fr', 'it']),
    );
    expect(i18n.options.fallbackLng).toContain('en');
  });

  it('has the nav keys in every language', async () => {
    for (const lng of ['de', 'en', 'fr', 'it']) {
      await i18n.changeLanguage(lng);
      expect(i18n.t('nav.start')).not.toBe('nav.start');
      expect(i18n.t('nav.settings')).not.toBe('nav.settings');
    }
  });
});
