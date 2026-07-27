#!/bin/sh
# #447 — runtime env injection for the hcc-app-fluent SPA.
#
# Runs at container start via the nginx image's /docker-entrypoint.d/ hook (as the
# unprivileged uid 101). Regenerates /usr/share/nginx/html/env-config.js from the
# container's per-env variables so ONE image serves every environment — no per-env
# VITE_* bake, so `az acr import`-ing the SIT image to PROD no longer inherits the
# SIT agent-host URL.
#
# Loaded by index.html (classic, non-deferred script) before the module bundle,
# so window.__ENV__ is populated by the time app code reads it.
set -eu

html_dir="${NGINX_HTML_DIR:-/usr/share/nginx/html}"
target="${html_dir}/env-config.js"
agent_host_url="${AGENT_HOST_URL:-}"

cat > "${target}" <<EOF
// Generated at container start by docker-entrypoint.d/30-env-config.sh (#447).
window.__ENV__ = Object.assign(window.__ENV__ || {}, {
  AGENT_HOST_URL: "${agent_host_url}"
});
EOF

echo "[30-env-config] wrote ${target} (AGENT_HOST_URL='${agent_host_url}')"
