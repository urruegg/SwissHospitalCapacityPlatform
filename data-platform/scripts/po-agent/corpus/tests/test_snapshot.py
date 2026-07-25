"""WS-A snapshot tests (Sprint 28, issue #377).

Verifies the corpus snapshot reads the docs tree, attributes each document to its
most-specific source root (ADR over PRD), and includes the first-order interview
transcripts under ``docs/reviews/``.

    python -m pytest data-platform/scripts/po-agent/corpus/tests/test_snapshot.py -v
"""
from __future__ import annotations

from pathlib import Path

import snapshot


def _write(base: Path, rel: str, text: str) -> None:
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_snapshot_tree_attributes_most_specific_source(tmp_path: Path) -> None:
    _write(tmp_path, "docs/PRD.md", "# PRD\n\nproduct requirements")
    _write(tmp_path, "docs/adr/0001-x.md", "# ADR\n\ndecision")
    _write(tmp_path, "docs/reviews/2026-01-01-interview.md", "# Interview\n\nquote")

    docs = snapshot.snapshot_tree(tmp_path, "deadbee")
    by_path = {d["path"]: d for d in docs}

    assert by_path["docs/adr/0001-x.md"]["source"] == "adr"
    assert by_path["docs/PRD.md"]["source"] == "prd"
    assert by_path["docs/reviews/2026-01-01-interview.md"]["source"] == "interview"
    assert all(d["commit"] == "deadbee" for d in docs)


def test_snapshot_tree_skips_missing_roots(tmp_path: Path) -> None:
    _write(tmp_path, "docs/PRD.md", "# PRD\n\nonly this exists")
    docs = snapshot.snapshot_tree(tmp_path, "deadbee")
    assert len(docs) == 1
    assert docs[0]["source"] == "prd"
