"""Pure PO-BVA fan-out composer for onboarding/value-fit questions.

The default route is onboarding because composing both peer agents is the
safest fallback when intent is ambiguous.
"""

from __future__ import annotations

import re
from typing import Any, Optional

import audit
from authz import CallerContext, filter_chunks
from orchestrator import (
    _ADVISORY_PREFIX,
    _PARTIAL_NOTE,
    _SOURCE_LANG_NOTE,
    _is_cited,
    _resolve_language,
    looks_like_injection,
)

_ROUTE_PATTERNS = {
    "onboarding": (
        r"\bonboard",
        r"should we onboard",
        r"\bbusiness case\b",
        r"\bvalue case\b",
        r"\bvalue[- ]fit\b",
        r"\bworth it\b",
        r"\bgo/no-go\b",
        r"\bgo or no-go\b",
        r"\baufnehmen\b",
        r"\blohnt\b",
    ),
    "strategic": (
        r"\bstrateg",
        r"\bfit\b",
        r"\bpriorit",
        r"\bcompetitor",
        r"\broadmap\b",
    ),
    "financial": (
        r"\broi\b",
        r"\btco\b",
        r"\bpayback\b",
        r"\bnpv\b",
        r"\bchf\b",
        r"\bcost",
        r"\bbudget\b",
        r"\bkosten\b",
        r"\bamortis",
    ),
}

_VALID_VERDICTS = {"go", "no-go", "conditional"}
_STATUS_RANK = {"verified": 0, "requires-validation": 1, "partial": 2}


def classify_intent(question: str) -> str:
    """Classify the question into financial, strategic, or onboarding intent.

    Patterns are word-boundary anchored so a strategic token such as ``fit``
    does not misfire on financial words like ``benefit`` or ``profit``.
    """

    q = question.lower()
    for intent in ("onboarding", "strategic", "financial"):
        if any(re.search(pattern, q) for pattern in _ROUTE_PATTERNS[intent]):
            return intent
    return "onboarding"


def bva_chunks_from_result(bva_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract Class-C GroundedChunks from a BvaSimulationResult."""

    chunks = bva_result.get("chunks", []) if isinstance(bva_result, dict) else []
    return list(chunks) if isinstance(chunks, list) else []


def _source_ref(chunk: dict[str, Any]) -> str:
    return str(chunk.get("citation", {}).get("sourceRef", ""))


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item and item not in out:
            out.append(item)
    return out


def _cite_sentence(text: str, refs: list[str]) -> str:
    citation = "; ".join(refs)
    clean = text.strip()
    if clean.endswith("."):
        clean = clean[:-1]
    return f"{clean} [{citation}]."


def _status_of(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "partial"
    return max((str(c.get("status", "partial")) for c in chunks), key=lambda s: _STATUS_RANK.get(s, 2))


def _confidence_of(chunks: list[dict[str, Any]]) -> float:
    if not chunks:
        return 0.0
    return round(sum(float(c.get("confidence", 0.0)) for c in chunks) / len(chunks), 4)


def _partial_result(
    *,
    question: str,
    caller: CallerContext,
    language: str,
    chunks: list[dict[str, Any]],
    audit_store: Any,
) -> dict[str, Any]:
    confidence = _confidence_of(chunks)
    audit.audit_log(
        audit_store,
        audit.build_bundle(
            question=question,
            caller_identity=caller.identity,
            caller_tier=caller.tier,
            chunks=chunks,
            confidence=confidence,
            status="partial",
            language=language,
        ),
    )
    return {
        "answer": f"{_ADVISORY_PREFIX[language]} {_PARTIAL_NOTE[language]}",
        "verdict": None,
        "chunks": chunks,
        "citations": _dedupe([_source_ref(c) for c in chunks]),
        "status": "partial",
        "confidence": confidence,
        "language": language,
    }


def _usable_chunks(
    chunks: list[dict[str, Any]],
    caller: CallerContext,
    threshold: float,
) -> list[dict[str, Any]]:
    permitted = filter_chunks(chunks, caller)
    return [
        c
        for c in permitted
        if _is_cited(c)
        and float(c.get("confidence", 0.0)) >= threshold
        and not looks_like_injection(str(c.get("text", "")))
    ]


def compose_onboarding_answer(
    question: str,
    bva_result: dict[str, Any],
    po_verdict: Optional[dict[str, Any]],
    caller: CallerContext,
    tools: Optional[dict[str, Any]] = None,
    threshold: float = 0.6,
    audit_store: Any = None,
) -> dict[str, Any]:
    """Compose the frozen PO verdict first, then cited BVA financial evidence."""

    del tools
    language = _resolve_language(caller, question)
    if looks_like_injection(question):
        return _partial_result(
            question=question,
            caller=caller,
            language=language,
            chunks=[],
            audit_store=audit_store,
        )

    verdict = str((po_verdict or {}).get("verdict", "")).lower()
    if verdict not in _VALID_VERDICTS:
        return _partial_result(
            question=question,
            caller=caller,
            language=language,
            chunks=[],
            audit_store=audit_store,
        )

    raw_po_chunks = list((po_verdict or {}).get("chunks", []) or [])
    raw_bva_chunks = bva_chunks_from_result(bva_result)
    po_chunks = _usable_chunks(raw_po_chunks, caller, threshold)
    bva_chunks = _usable_chunks(raw_bva_chunks, caller, threshold)
    usable = po_chunks + bva_chunks

    verdict_refs = _dedupe(
        list((po_verdict or {}).get("citations", []) or []) + [_source_ref(c) for c in po_chunks]
    )
    if not verdict_refs or not bva_chunks:
        return _partial_result(
            question=question,
            caller=caller,
            language=language,
            chunks=usable,
            audit_store=audit_store,
        )

    rationale = str((po_verdict or {}).get("rationale", "")).strip()
    verdict_text = f"Verdict: {verdict}" + (f" - {rationale}" if rationale else "")
    sentences = [_cite_sentence(verdict_text, verdict_refs)]
    for chunk in bva_chunks:
        sentences.append(_cite_sentence(str(chunk.get("text", "")), [_source_ref(chunk)]))

    source_langs = {str(c.get("language", language)) for c in usable}
    lang_note = ""
    foreign = source_langs - {language}
    if foreign:
        lang_note = " " + _SOURCE_LANG_NOTE[language].format(
            langs=", ".join(sorted(foreign)), answer_lang=language
        )

    answer = f"{_ADVISORY_PREFIX[language]} {' '.join(sentences)}{lang_note}"
    citations = _dedupe(verdict_refs + [_source_ref(c) for c in bva_chunks])
    status = _status_of(usable)
    confidence = _confidence_of(usable)

    audit.audit_log(
        audit_store,
        audit.build_bundle(
            question=question,
            caller_identity=caller.identity,
            caller_tier=caller.tier,
            chunks=usable,
            confidence=confidence,
            status=status,
            language=language,
        ),
    )
    return {
        "answer": answer,
        "verdict": verdict,
        "chunks": usable,
        "citations": citations,
        "status": status,
        "confidence": confidence,
        "language": language,
    }


def build_opportunity_writeback(
    *,
    hospital_name: str,
    archetype: str,
    question: str,
    language: str,
    bva_result: dict[str, Any],
    po_verdict: dict[str, Any],
    composed: Optional[dict[str, Any]] = None,
    at: str,
    created_by: str,
) -> dict[str, Any]:
    """Build kwargs for OpportunityStore.record_ask without calling Cosmos."""

    verdict_snapshot = {
        "verdict": po_verdict.get("verdict"),
        "rationale": po_verdict.get("rationale", ""),
        "citations": list(po_verdict.get("citations", []) or []),
    }
    return {
        "hospitalName": hospital_name,
        "archetype": archetype,
        "askText": question,
        "language": language,
        "createdBy": created_by,
        "at": at,
        "status": "new",
        "bvaResult": bva_result,
        "poVerdict": verdict_snapshot,
        "inputs": {"composed": composed} if composed is not None else None,
        "historyEvent": "PO-BVA fan-out ask composed",
    }


__all__ = [
    "_ROUTE_PATTERNS",
    "bva_chunks_from_result",
    "build_opportunity_writeback",
    "classify_intent",
    "compose_onboarding_answer",
]
