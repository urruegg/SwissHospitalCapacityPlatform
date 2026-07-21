// @ts-check
import { defineConfig } from 'astro/config';

// Curavias product landing page.
// Multilingual: DE-CH primary (unprefixed), EN/FR/IT secondary (prefixed).
// Deployed as a static site to Azure Static Web Apps -> curavias.ch / www.curavias.ch.
// NOTE: @astrojs/sitemap is re-enabled in Phase 3 once all locales have pages
// (its i18n alternate-link builder requires every locale to resolve).
export default defineConfig({
  site: 'https://curavias.ch',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
  },
  i18n: {
    defaultLocale: 'de',
    locales: ['de', 'en', 'fr', 'it'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
