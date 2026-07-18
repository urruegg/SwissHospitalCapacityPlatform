# syntax=docker/dockerfile:1

# Sprint 13 T1 — multi-stage build for the Fluent UI baseline app.
# Stage 1: build the static bundle. Stage 2: serve via nginx-unprivileged.

FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# Vite bakes VITE_* vars into the static bundle at build time. Pass the agent-host
# base URL so the Copilot Drawer calls the live agents instead of the built-in
# mock (empty => mock, see src/copilot-drawer/agent-manifest.ts).
ARG VITE_AGENT_HOST_URL=""
ENV VITE_AGENT_HOST_URL=$VITE_AGENT_HOST_URL
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
