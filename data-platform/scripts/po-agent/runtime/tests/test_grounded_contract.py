"""WS-RT Task RT.1: grounded-answer contract tests.

TDD step 1 (RED): ``answer()`` must

* degrade to a **transparent partial** (``status == "partial"``) when
  fewer than ``min_chunks`` clear the confidence threshold, and
* **never emit an uncited claim** - any chunk lacking
  ``citation.sourceRef`` is excluded from the synthesised answer
  (NFR-POA-001).
"""

import orchestrator
from authz import CallerContext


def _chunk(text, conf, class_id="A", source_ref="docs/PRD.md#x", status="verified"):
    return {
        "classId": class_id,
        "text": text,
        "citation": {"sourceRef": source_ref},
        "asOf": "2026-07-25T00:00:00Z",
        "liveness": "snapshot",
        "status": status,
        "confidence": conf,
        "language": "en",
    }


def _caller(tier="internal", language="en"):
    return CallerContext(identity="alice@curavias", tier=tier, language=language)


def test_degrades_to_transparent_partial_below_threshold():
    # The only chunk is below the 0.6 confidence threshold.
    tools = {"A": lambda q: [_chunk("weak grounding", 0.30)]}
    result = orchestrator.answer(
        "What is the MVP scope?",
        _caller(),
        tools=tools,
        threshold=0.6,
        min_chunks=1,
    )
    assert result["status"] == "partial"
    # Transparency: the answer signals a degraded / partial grounding.
    assert "partial" in result["answer"].lower() or "insufficient" in result["answer"].lower()


def test_never_emits_an_uncited_claim():
    # One well-grounded cited chunk + one uncited chunk (empty sourceRef).
    tools = {
        "A": lambda q: [
            _chunk("cited claim", 0.9, source_ref="docs/PRD.md#a"),
            _chunk("uncited claim", 0.9, source_ref=""),
        ]
    }
    result = orchestrator.answer("q", _caller(), tools=tools, threshold=0.6, min_chunks=1)

    # The uncited chunk must not appear in the output chunk set nor the answer.
    for chunk in result["chunks"]:
        assert chunk["citation"]["sourceRef"], "uncited chunk leaked into output"
    assert "uncited claim" not in result["answer"]
    assert "cited claim" in result["answer"]
