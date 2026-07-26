"""WS-A chunk/tag + conformance tests (Sprint 28, issue #377).

Covers the acceptance gate beyond the PHI gate: chunk-boundary splitting,
DE/EN language tagging, interview first-order ordering, and GroundedChunk
schema conformance of the published Class A output.

    python -m pytest data-platform/scripts/po-agent/corpus/tests/ -v
"""
from __future__ import annotations

import json
from pathlib import Path

import chunk_tag
import publish

REPO_ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"

_ADR_DOC = """# ADR-0099: Example decision

| Field | Value |
| ----- | ----- |
| **Version** | 2.3.1 |
| **Date** | 2026-07-25 |

## Context

The platform runtime is the GitHub Copilot coding agent and this is the context.

## Decision

We decide to ground every answer with a citation and this is the decision body.

## Consequences

There are consequences that follow from the decision described above here.
"""

_DE_DOC = """# Zusammenfassung der Kapazitaetsplanung

Der Krankenhaus-Betrieb und die Kapazitaet werden nicht ohne Sprache geplant,
und das System muss auch die deutsche Sprache unterstuetzen fuer die Nutzer.
"""


def test_chunk_document_splits_on_headings() -> None:
    chunks = chunk_tag.chunk_document("docs/adr/0099-example.md", _ADR_DOC, "abc1234")
    anchors = [c["anchor"] for c in chunks]
    assert "Context" in anchors
    assert "Decision" in anchors
    assert "Consequences" in anchors
    # Version/Date propagated from the header table to every chunk.
    assert all(c["version"] == "2.3.1" for c in chunks)
    assert all(c["date"] == "2026-07-25" for c in chunks)


def test_language_tag_en_and_de() -> None:
    en = chunk_tag.chunk_document("docs/adr/0099-example.md", _ADR_DOC, "abc1234")
    assert all(c["language"] == "en" for c in en)
    de = chunk_tag.chunk_document("docs/PRD.md", _DE_DOC, "abc1234")
    assert de[0]["language"] == "de"


def test_interview_chunks_are_first_order() -> None:
    interview = chunk_tag.chunk_document(
        "docs/reviews/2026-07-17-ama-hospital-ops-lead-review.md",
        "# Review\n\nThe hospital ops lead said capacity answers must be cited.",
        "abc1234",
    )
    secondary = chunk_tag.chunk_document(
        "docs/adr/0099-example.md", _ADR_DOC, "abc1234",
    )
    assert all(c["is_interview"] for c in interview)
    published = publish.publish(secondary + interview)
    # Interview-derived chunk must be published ahead of the secondary material.
    interview_text = interview[0]["text"]
    positions = [i for i, c in enumerate(published) if c["text"] == interview_text]
    assert positions and positions[0] == 0


def test_published_chunks_conform_to_grounded_chunk_schema() -> None:
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    tagged = chunk_tag.chunk_document("docs/adr/0099-example.md", _ADR_DOC, "abc1234")
    tagged += chunk_tag.chunk_document("docs/PRD.md", _DE_DOC, "abc1234")
    for chunk in publish.publish(tagged):
        jsonschema.validate(instance=chunk, schema=schema)
        assert chunk["classId"] == "A"
        assert chunk["liveness"] == "live"
        assert chunk["citation"]["sourceRef"].endswith("@abc1234")
