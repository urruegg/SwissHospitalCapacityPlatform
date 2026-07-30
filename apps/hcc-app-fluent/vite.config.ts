/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import pkg from './package.json';

// Sprint 13 T1 — Vite build for the Fluent UI baseline app.
export default defineConfig({
  plugins: [react()],
  define: { __APP_VERSION__: JSON.stringify(pkg.version) },
  server: { port: 5173 },
  build: { outDir: 'dist', sourcemap: true },
  test: {
    globals: true,
    environment: './tests/vitest-environment-jsdom-compatible.ts',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/unit/**/*.{test,spec}.{ts,tsx}', 'src/**/*.{test,spec}.{ts,tsx}'],
    css: false,
  },
});
