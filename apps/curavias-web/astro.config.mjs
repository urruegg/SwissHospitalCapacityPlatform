// @ts-check
import { defineConfig } from 'astro/config';

// Curavias product landing page.
// Multilingual: DE-CH primary (unprefixed), EN/FR/IT secondary (prefixed).
// Deployed as a static site to Azure Static Web Apps -> curavias.ch / www.curavias.ch.
// Sitemap is maintained as a static file at public/sitemap.xml (the @astrojs/sitemap
// i18n builder is incompatible with prefixDefaultLocale:false in this Astro version).
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
