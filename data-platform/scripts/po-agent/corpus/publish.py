"""WS-A Class A corpus: publish to the Foundry IQ knowledge source (Sprint 28).

Converts the surviving internal ``TaggedChunk``s into the frozen ``GroundedChunk``
contract (``docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md``,
classId ``A``) after the PHI gate, and orders **interviews first** (they are
first-order corpus material, FR-POA-004). In production the result is POSTed to
the Foundry IQ knowledge source; here ``publish`` returns the GroundedChunk list
(and can optionally write JSONL) so it is verifiable offline.

Class A invariants (contract Section 3): ``liveness`` is always ``live`` (daily
refresh), ``citation.sourceRef`` is ``doc-path@commit``, ``anchor`` is the section
heading.
"""
from __future__ import annotations

import json
from pathlib import Path

import phi_gate

_CONFIDENCE = {
    "verified": 0.9,
    "partial": 0.7,
    "requires-validation": 0.5,
}


def _as_of(tagged: dict) -> str:
    """Normalise the doc date to an ISO-8601 date-time (contract ``asOf``)."""
    raw = tagged.get("date")
    if not raw:
        return "1970-01-01T00:00:00Z"
    if len(raw) == 10:  # date-only -> midnight UTC
        return f"{raw}T00:00:00Z"
    return raw


def to_grounded_chunk(tagged: dict) -> dict:
    """Map an internal TaggedChunk to the frozen GroundedChunk (classId A)."""
    status = tagged.get("status", "verified")
    citation: dict[str, str] = {
        "sourceRef": f"{tagged['source_path']}@{tagged.get('commit', 'unknown')}",
    }
    if tagged.get("anchor"):
        citation["anchor"] = tagged["anchor"]
    confidence = _CONFIDENCE.get(status, 0.7)
    # Interviews are first-order primary evidence: nudge confidence up (capped).
    if tagged.get("is_interview"):
        confidence = min(1.0, confidence + 0.05)
    return {
        "classId": "A",
        "text": tagged["text"],
        "citation": citation,
        "asOf": _as_of(tagged),
        "liveness": "live",
        "status": status,
        "confidence": confidence,
        "language": tagged.get("language", "en"),
    }


def publish(tagged_chunks: list[dict], out_file: str | Path | None = None) -> list[dict]:
    """PHI-gate, order interviews first, map to GroundedChunks, optionally write.

    Returns the published GroundedChunk list. Never emits a PHI chunk.
    """
    survivors = phi_gate.drop_phi(tagged_chunks)
    # Stable sort: interviews (first-order) ahead of secondary material.
    survivors.sort(key=lambda c: 0 if c.get("is_interview") else 1)
    grounded = [to_grounded_chunk(c) for c in survivors]
    if out_file is not None:
        path = Path(out_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            for chunk in grounded:
                fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    return grounded
