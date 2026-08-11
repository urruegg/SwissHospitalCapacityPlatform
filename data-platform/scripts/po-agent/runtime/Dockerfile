FROM python:3.11-slim
WORKDIR /app
COPY data-platform/scripts/po-agent/runtime/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY data-platform/scripts/po-agent/runtime/ .
# Sibling class modules import via sys.path in orchestrator/tools; copy them in.
COPY data-platform/scripts/po-agent/corpus ./corpus
COPY data-platform/scripts/po-agent/liveproof ./liveproof
COPY data-platform/scripts/po-agent/cost ./cost
COPY data-platform/scripts/po-agent/ontology ./ontology
# Class C (cost) reads docs/BVA.md + the BVA evidence master data directly
# (Sprint 44 task b) -- neither is otherwise reachable from inside the
# image, so copy just this subset into a repo-shaped mirror. app.py's
# _resolve_repo_root() and reconcile_bva.py's _evidence_grounding_module()
# both look for this path.
COPY docs/BVA.md ./repo/docs/BVA.md
COPY data/master-data/bva ./repo/data/master-data/bva
COPY data-platform/bva ./repo/data-platform/bva
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
