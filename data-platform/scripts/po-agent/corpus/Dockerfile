FROM python:3.11-slim
WORKDIR /app
COPY data-platform/scripts/po-agent/corpus/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY data-platform/scripts/po-agent/corpus/ .
# The corpus refresh job snapshots docs/** (snapshot.py's CORPUS_SOURCES) - bake
# the current docs tree into the image so there's real content to index. This
# ties corpus freshness to how often this image is rebuilt (the CI workflow
# triggers on docs/** changes too, see po-agent-corpus-build.yml). get_commit()
# gracefully falls back to "unknown" since .git isn't copied into the image
# (too heavy, unnecessary - document_id() doesn't depend on a real commit sha
# for stability, only citation.sourceRef's freshness stamp uses it).
COPY docs/ /app/repo/docs/
ENV CORPUS_REPO_ROOT=/app/repo
CMD ["python", "refresh_job.py"]
