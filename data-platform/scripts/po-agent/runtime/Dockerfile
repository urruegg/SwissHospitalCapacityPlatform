FROM python:3.11-slim
WORKDIR /app
COPY runtime/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY runtime/ .
# Sibling class modules import via sys.path in orchestrator/tools; copy them in.
COPY corpus ./corpus
COPY liveproof ./liveproof
COPY cost ./cost
COPY ontology ./ontology
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
