// Sprint 20 M8 — build-time app version, injected by Vite `define`.
// Falls back to '0.0.0' when the define is absent (e.g. some test contexts).
declare const __APP_VERSION__: string;

export const APP_VERSION =
  typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '0.0.0';
