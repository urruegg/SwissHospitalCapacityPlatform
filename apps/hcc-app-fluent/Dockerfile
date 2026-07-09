# syntax=docker/dockerfile:1

# Sprint 13 T1 — multi-stage build for the Fluent UI baseline app.
# Stage 1: build the static bundle. Stage 2: serve via nginx-unprivileged.

FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
