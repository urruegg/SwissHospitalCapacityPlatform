import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Sprint 13 T7 — Vite build for the Rayfin PoC placeholder shell.
export default defineConfig({
  plugins: [react()],
  server: { port: 5273 },
  build: { outDir: 'dist', sourcemap: true },
});
