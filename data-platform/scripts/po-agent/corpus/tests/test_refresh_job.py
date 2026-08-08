import pytest

import snapshot
from refresh_job import build_grounded_chunks, document_id, main


def test_build_grounded_chunks_from_snapshot_docs():
    docs = [
        {"source_path": "docs/PRD.md", "text": "# PRD\nSome product content.", "date": "2026-08-01"},
    ]
    chunks = build_grounded_chunks(docs, commit="abc1234")
    assert len(chunks) >= 1
    assert chunks[0]["classId"] == "A"
    assert chunks[0]["citation"]["sourceRef"].startswith("docs/PRD.md@abc1234")


def test_build_grounded_chunks_applies_doc_level_date_fallback():
    """When the text has no doc-header ``Date`` row, chunk_tag.chunk_document
    extracts ``date: None`` for every chunk. build_grounded_chunks must then
    fall back to the doc dict's own ``date`` so ``asOf`` reflects the real
    date instead of silently defaulting to the epoch (publish.py's _as_of)."""
    docs = [
        {"source_path": "docs/NOTES.md", "text": "# Notes\nNo header table here.", "date": "2026-08-01"},
    ]
    chunks = build_grounded_chunks(docs, commit="abc1234")
    assert len(chunks) == 1
    assert chunks[0]["asOf"] == "2026-08-01T00:00:00Z"


def test_document_id_is_stable_across_commits():
    """The id must NOT change when only the commit changes (sourceRef embeds the
    commit hash) — otherwise every daily refresh would upsert a brand-new
    document instead of overwriting the previous day's version, and the index
    would grow forever instead of staying in sync with the corpus."""
    citation_day1 = {"sourceRef": "docs/PRD.md@abc1234", "anchor": "Overview"}
    citation_day2 = {"sourceRef": "docs/PRD.md@def5678", "anchor": "Overview"}
    assert document_id(citation_day1, text="v1 text") == document_id(citation_day2, text="v2 text")


def test_document_id_differs_for_different_anchors():
    citation_a = {"sourceRef": "docs/PRD.md@abc1234", "anchor": "Overview"}
    citation_b = {"sourceRef": "docs/PRD.md@abc1234", "anchor": "Goals"}
    assert document_id(citation_a, text="x") != document_id(citation_b, text="x")


def test_document_id_falls_back_to_text_hash_when_anchor_missing():
    """Two anchorless chunks from the same doc with different text must not collide."""
    citation = {"sourceRef": "docs/README.md@abc1234"}
    id_1 = document_id(citation, text="first chunk of README")
    id_2 = document_id(citation, text="second chunk of README")
    assert id_1 != id_2


def test_main_raises_runtime_error_when_snapshot_tree_is_empty(monkeypatch):
    """A bad CORPUS_REPO_ROOT mount (or repo not checked out) must fail loudly
    instead of silently "succeeding" with 0 uploaded chunks and a stale index."""
    monkeypatch.setenv("CORPUS_REPO_ROOT", "/app/repo")
    monkeypatch.setattr(snapshot, "get_commit", lambda repo_root: "abc1234")
    monkeypatch.setattr(snapshot, "snapshot_tree", lambda repo_root, commit: [])

    with pytest.raises(RuntimeError, match="snapshot_tree found 0 documents"):
        main()
