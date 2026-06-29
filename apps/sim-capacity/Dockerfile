FROM python:3.11-slim

WORKDIR /app

COPY src/ /app/src/

ENV PYTHONPATH=/app/src

# Thin-slice runtime emits one envelope payload and exits.
CMD ["python", "/app/src/producer.py"]
