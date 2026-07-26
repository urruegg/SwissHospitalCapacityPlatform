"""WS-RT orchestrator: route -> ground -> synthesise -> cite (advisory-only).

Implements the frozen ``answer(question, caller)`` contract
(2026-07-25 PO Agent contracts, Section 4):

* routes a question to one or more Class A/B/C/D read-only tools,
* applies the authorisation-aware filter (:mod:`authz`, partner tier),
* enforces the **grounded-answer contract** - emits an answer only when
  at least ``min_chunks`` chunks clear the confidence threshold,
  otherwise degrades to a transparent ``partial``; never an uncited
  claim (NFR-POA-001),
* answers in **DE or EN** with source-language transparency (FR-POA-008),
* logs the full audit bundle (:mod:`audit`, NFR-POA-002).

The class tools are injected (``tools=``) so CI mocks them; this module
performs no network I/O.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import audit
from authz import CallerContext, filter_chunks

Tool = Callable[[str], list[dict[str, Any]]]

# --- transparency phrasing (DE/EN) ---------------------------------------
_PARTIAL_NOTE = {
    "en": "This is a partial, transparently-degraded answer: insufficient "
    "high-confidence grounded sources were available.",
    "de": "Dies ist eine teilweise, transparent abgestufte Antwort: es lagen "
    "nicht genug hoch-vertrauenswuerdige belegte Quellen vor.",
}
_ADVISORY_PREFIX = {
    "en": "Advisory only.",
    "de": "Nur zur Beratung.",
}
_SOURCE_LANG_NOTE = {
    "en": "Some sources are in {langs}; answered in {answer_lang}.",
    "de": "Einige Quellen sind in {langs}; beantwortet auf {answer_lang}.",
}

# --- routing keywords -> class -------------------------------------------
_ROUTE_KEYWORDS = {
    "C": ("cost", "budget", "chf", "tco", "bva", "spend", "kosten"),
    "B": ("region", "sku", "subscription", "capacity", "deployed", "workspace", "running"),
    "D": ("concept", "ontology", "occupancy", "forecast", "gold", "data model", "belegung"),
}


def route(question: str) -> list[str]:
    """Pick the knowledge classes a question should be grounded on."""

    q = question.lower()
    classes = [cid for cid, kws in _ROUTE_KEYWORDS.items() if any(k in q for k in kws)]
    # Class A corpus is the always-on default (product/PRD/design questions).
    if "A" not in classes:
        classes.insert(0, "A")
    return classes


def looks_like_injection(text: str) -> bool:
    """Heuristic prompt-injection detector for untrusted question/chunk text."""

    t = text.lower()
    signals = (
        "ignore previous",
        "ignore the above",
        "disregard your instructions",
        "system prompt",
        "reveal your",
        "you are now",
        "jailbreak",
    )
    return any(s in t for s in signals)


def _is_cited(chunk: dict[str, Any]) -> bool:
    return bool(chunk.get("citation", {}).get("sourceRef"))


def _resolve_language(caller: CallerContext, question: str) -> str:
    if caller.language in ("de", "en"):
        return caller.language
    # Fall back to a light DE signal in the question, else EN.
    return "de" if any(u in question for u in "äöüßÄÖÜ") else "en"


def answer(
    question: str,
    caller: CallerContext,
    tools: Optional[dict[str, Tool]] = None,
    threshold: float = 0.6,
    min_chunks: int = 1,
    audit_store: Any = None,
) -> dict[str, Any]:
    """Answer a product question under the frozen grounded-answer contract."""

    tools = tools or {}
    language = _resolve_language(caller, question)

    # Injection defence: never let untrusted question text steer behaviour.
    if looks_like_injection(question):
        result = {
            "answer": f"{_ADVISORY_PREFIX[language]} {_PARTIAL_NOTE[language]}",
            "chunks": [],
            "status": "partial",
            "confidence": 0.0,
            "language": language,
        }
        audit.audit_log(
            audit_store,
            audit.build_bundle(
                question=question,
                caller_identity=caller.identity,
                caller_tier=caller.tier,
                chunks=[],
                confidence=0.0,
                status="partial",
                language=language,
            ),
        )
        return result

    # Route -> ground (read-only tool calls).
    gathered: list[dict[str, Any]] = []
    for class_id in route(question):
        tool = tools.get(class_id)
        if tool is None:
            continue
        try:
            gathered.extend(tool(question) or [])
        except Exception:
            continue  # a failing tool degrades grounding, never crashes

    # Authorisation-aware filter (partner tier drops cost/security).
    permitted = filter_chunks(gathered, caller)

    # Grounded-answer contract: only cited chunks that clear the threshold
    # may contribute to the synthesised answer. Ignore injected chunk text.
    usable = [
        c
        for c in permitted
        if _is_cited(c)
        and float(c.get("confidence", 0.0)) >= threshold
        and not looks_like_injection(str(c.get("text", "")))
    ]

    if len(usable) < min_chunks:
        # Transparent partial - never an uncited claim.
        result_answer = f"{_ADVISORY_PREFIX[language]} {_PARTIAL_NOTE[language]}"
        result = {
            "answer": result_answer,
            "chunks": usable,
            "status": "partial",
            "confidence": (
                max((float(c.get("confidence", 0.0)) for c in usable), default=0.0)
            ),
            "language": language,
        }
        audit.audit_log(
            audit_store,
            audit.build_bundle(
                question=question,
                caller_identity=caller.identity,
                caller_tier=caller.tier,
                chunks=usable,
                confidence=result["confidence"],
                status="partial",
                language=language,
            ),
        )
        return result

    # Synthesise an advisory, fully-cited answer.
    sentences = []
    source_langs = set()
    for c in usable:
        source_langs.add(str(c.get("language", language)))
        ref = c["citation"]["sourceRef"]
        sentences.append(f"{c['text']} [{ref}]")
    body = " ".join(sentences)

    lang_note = ""
    foreign = source_langs - {language}
    if foreign:
        lang_note = " " + _SOURCE_LANG_NOTE[language].format(
            langs=", ".join(sorted(foreign)), answer_lang=language
        )
    result_answer = f"{_ADVISORY_PREFIX[language]} {body}{lang_note}"

    # Status: drift in any used chunk propagates as requires-validation.
    if any(c.get("status") == "requires-validation" for c in usable):
        status = "requires-validation"
    elif all(c.get("status") == "verified" for c in usable):
        status = "verified"
    else:
        status = "partial"

    confidence = sum(float(c.get("confidence", 0.0)) for c in usable) / len(usable)

    result = {
        "answer": result_answer,
        "chunks": usable,
        "status": status,
        "confidence": round(confidence, 4),
        "language": language,
    }
    audit.audit_log(
        audit_store,
        audit.build_bundle(
            question=question,
            caller_identity=caller.identity,
            caller_tier=caller.tier,
            chunks=usable,
            confidence=result["confidence"],
            status=status,
            language=language,
        ),
    )
    return result
