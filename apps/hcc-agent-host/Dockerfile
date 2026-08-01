# Sprint 13 T5 — agent-host container (Python 3.11 + FastAPI/uvicorn).
# Multi-stage: build wheels, then a slim runtime image. Runs as non-root.
#
# Build context: **repo root** (not this directory). The Dockerfile must copy
# both app source (under apps/hcc-agent-host/) AND the repo-root agents/
# folder that holds the Sprint 11 prompt packs. See ci-build-agent-host.yml
# and the repo-root .dockerignore allowlist for the exact paths permitted.
FROM python:3.11-slim AS build
WORKDIR /app
COPY apps/hcc-agent-host/pyproject.toml ./
COPY apps/hcc-agent-host/src ./src
RUN pip install --no-cache-dir --upgrade pip build \
    && pip wheel --no-cache-dir --wheel-dir /wheels ".[runtime]"

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/data-platform/decision \
    PORT=8080
WORKDIR /app
COPY --from=build /wheels /wheels
COPY apps/hcc-agent-host/pyproject.toml ./
COPY apps/hcc-agent-host/src ./src
# Sprint 39 P2 - the in-host operational loop (loop/*, api /worklist,/decisions,
# /evidence) reuses the sim-capacity closedloop package. Vendor it under src/ so
# `import closedloop` resolves via --app-dir src; impact/coordination come from
# data-platform/decision on PYTHONPATH (copied below). Without this the app
# crashes on startup (ModuleNotFoundError / the loop path bootstrap is a no-op
# in the container).
COPY apps/sim-capacity/src/closedloop ./src/closedloop
COPY agents ./agents
# Sprint 26 WS-C — decision-lane apply CLIs (coordination.seed_live,
# foundry.register_decision_tier) for the in-VNet apply job. NOT imported by the
# serving api; run on-demand from /app/data-platform/decision via the
# caj-decision-apply Container Apps Job (`az containerapp job start`).
COPY data-platform/decision ./data-platform/decision
RUN pip install --no-cache-dir /wheels/* \
    && useradd --create-home --uid 10001 appuser
ENV AGENTS_ROOT=/app/agents
USER appuser
EXPOSE 8080
# The Sprint 11 agent packs (bmca-agent, ooa-agent, dca-agent, orsa-agent,
# sba-agent, csa-agent, data-quality-agent) plus the Sprint 32 signal-agent
# (SGA) are baked into the image at /app/agents via the whole-folder COPY above;
# AGENTS_ROOT is set so api/app.py's _agents_root() picks them up. Any
# agents/<name>/ pack declaring `runtime: agent-host` is auto-discovered by the
# manifest loader — no Dockerfile change is needed when a new pack lands.
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]
