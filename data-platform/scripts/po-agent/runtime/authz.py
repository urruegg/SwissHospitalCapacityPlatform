"""WS-RT authorisation-aware filter: caller entitlement + domain + partner tier.

The orchestrator (see :mod:`orchestrator`) calls :func:`filter_chunks` after
grounding so a caller only ever sees chunks their entitlement permits. The
**partner tier** never sees internal **cost** (Class C) or **security** detail
(FR-POA-009).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Domain each knowledge class maps to.
CLASS_DOMAINS = {
    "A": "corpus",
    "B": "live-proof",
    "C": "cost",
    "D": "ontology",
}

# Classes each tier is entitled to see.
_INTERNAL_CLASSES = {"A", "B", "C", "D"}
_PARTNER_CLASSES = {"A", "B", "D"}  # partner never sees cost (C)

# Text markers that indicate internal-only (cost/security) detail a partner
# caller must never receive, even inside an otherwise-allowed class.
_PARTNER_FORBIDDEN_MARKERS = (
    "cost",
    "chf",
    "budget",
    "tco",
    "bva",
    "secret",
    "credential",
    "rbac",
    "security",
    "vulnerab",
)


@dataclass
class CallerContext:
    """Identity + entitlement of the caller asking a question."""

    identity: str
    tier: str = "internal"  # "internal" | "partner"
    language: str = "en"  # preferred UI language "de" | "en"
    entitlements: set[str] = field(default_factory=set)


def is_partner(caller: CallerContext) -> bool:
    return caller.tier.lower() == "partner"


def allowed_classes(caller: CallerContext) -> set[str]:
    """Knowledge classes this caller's tier is entitled to receive."""

    return set(_PARTNER_CLASSES if is_partner(caller) else _INTERNAL_CLASSES)


def _partner_safe(chunk: dict[str, Any]) -> bool:
    """A partner-visible chunk must not carry internal cost/security detail."""

    text = str(chunk.get("text", "")).lower()
    return not any(marker in text for marker in _PARTNER_FORBIDDEN_MARKERS)


def filter_chunks(
    chunks: list[dict[str, Any]], caller: CallerContext
) -> list[dict[str, Any]]:
    """Drop chunks the caller's entitlement does not permit.

    Internal callers keep all classes. Partner callers keep only the
    partner-visible classes AND only chunks free of internal
    cost/security markers.
    """

    permitted = allowed_classes(caller)
    out = []
    for chunk in chunks:
        if chunk.get("classId") not in permitted:
            continue
        if is_partner(caller) and not _partner_safe(chunk):
            continue
        out.append(chunk)
    return out
