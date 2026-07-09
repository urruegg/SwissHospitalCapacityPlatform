# Sprint 13 T5 — agent-host container (Python 3.11 + FastAPI/uvicorn).
# Multi-stage: build wheels, then a slim runtime image. Runs as non-root.
FROM python:3.11-slim AS build
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip build \
    && pip wheel --no-cache-dir --wheel-dir /wheels ".[runtime]"

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080
WORKDIR /app
COPY --from=build /wheels /wheels
COPY pyproject.toml ./
COPY src ./src
COPY agents ./agents
RUN pip install --no-cache-dir /wheels/* \
    && useradd --create-home --uid 10001 appuser
ENV AGENTS_ROOT=/app/agents
USER appuser
EXPOSE 8080
# The repo agents/ dir is mounted or copied at deploy time; AGENTS_ROOT points to it.
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]
