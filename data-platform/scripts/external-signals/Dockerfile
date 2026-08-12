# Provider-runner image (Sprint 44 Layer 2). Build context = repo root.
# Replaces the placeholder mcr.microsoft.com/azure-cli:latest the Container App
# ships with. Discovers provider manifests and publishes DC-EXT-SIGNAL-v1 to
# Event Hub. Live bindings (e.g. Web IQ) activate only when their credential is
# present; otherwise they fall back to the simulator.
FROM python:3.11-slim

WORKDIR /app

COPY data-platform/scripts/external-signals/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY data-platform/scripts/external-signals/ /app/

ENV PYTHONPATH=/app

CMD ["python", "/app/run.py"]
