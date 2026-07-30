// #447 runtime config placeholder (dev + build default).
//
// In a deployed container this file is OVERWRITTEN at startup by
// docker-entrypoint.d/30-env-config.sh, which injects per-env values (e.g.
// AGENT_HOST_URL) from the container environment. During `npm run dev` /
// `vite preview` / tests this placeholder leaves window.__ENV__ empty so the app
// falls back to build-time import.meta.env.VITE_* values.
window.__ENV__ = window.__ENV__ || {};
