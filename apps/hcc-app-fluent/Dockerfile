# syntax=docker/dockerfile:1

# Sprint 13 T1 — multi-stage build for the Fluent UI baseline app.
# Stage 1: build the static bundle. Stage 2: serve via nginx-unprivileged.

FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# Vite bakes VITE_* vars into the static bundle at build time. For the agent-host
# URL we now prefer RUNTIME injection (#447): the entrypoint writes env-config.js
# from the container's AGENT_HOST_URL, so one image is env-agnostic. The build ARG
# is kept only as a local-dev fallback and defaults to empty (=> mock unless the
# runtime value is injected).
ARG VITE_AGENT_HOST_URL=""
ENV VITE_AGENT_HOST_URL=$VITE_AGENT_HOST_URL
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
# SPA history-API fallback so client-side deep-links don't 404 (#299).
COPY nginx-default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# #447 runtime env injection: entrypoint regenerates env-config.js from AGENT_HOST_URL
# at container start (runs as uid 101 via the nginx /docker-entrypoint.d/ hook).
USER root
COPY docker-entrypoint.d/30-env-config.sh /docker-entrypoint.d/30-env-config.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/30-env-config.sh \
    && chmod 0755 /docker-entrypoint.d/30-env-config.sh \
    && chown 101:0 /usr/share/nginx/html/env-config.js \
    && chmod 0664 /usr/share/nginx/html/env-config.js
USER 101
EXPOSE 8080
