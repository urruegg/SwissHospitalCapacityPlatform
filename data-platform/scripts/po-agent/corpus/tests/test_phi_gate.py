"""PHI-gate test (WS-A step 1, TDD). Sprint 28, issue #377.

The Class A corpus is synthetic and PHI-excluded (FR-POA-004, NFR-POA-001).
Any tagged chunk classified `phi` MUST be dropped before publish -- it may never
reach the Foundry IQ knowledge source. This test is written before the
implementation and is expected to FAIL until phi_gate + publish exist.

    python -m pytest data-platform/scripts/po-agent/corpus/tests/test_phi_gate.py -v
"""
from __future__ import annotations

import phi_gate
import publish


def _tagged(classification: str, text: str = "example chunk text") -> dict:
    """A minimal internal TaggedChunk as produced by chunk_tag."""
    return {
        "text": text,
        "source_path": "docs/PRD.md",
        "commit": "abc1234",
        "anchor": "## Personas",
        "classification": classification,
        "residency": "ch",
        "status": "verified",
        "version": "1.15.0",
        "date": "2026-07-25T08:00:00Z",
        "language": "en",
        "is_interview": False,
    }


def test_phi_gate_drops_phi_chunks() -> None:
    chunks = [_tagged("public"), _tagged("phi"), _tagged("internal")]
    kept = phi_gate.drop_phi(chunks)
    assert all(c["classification"] != "phi" for c in kept)
    assert len(kept) == 2


def test_publish_never_emits_phi() -> None:
    chunks = [_tagged("public"), _tagged("phi", text="secret patient note")]
    published = publish.publish(chunks)
    texts = [c["text"] for c in published]
    assert "secret patient note" not in texts
    assert all(c["classId"] == "A" for c in published)
