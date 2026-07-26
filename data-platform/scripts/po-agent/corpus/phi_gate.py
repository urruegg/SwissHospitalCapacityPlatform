"""WS-A Class A corpus: PHI exclusion gate (Sprint 28, issue #377).

The Product Owner Agent's Class A corpus is synthetic and PHI-excluded
(FR-POA-004, NFR-POA-001). This gate is the last line of defence before publish:
any tagged chunk classified ``phi`` is dropped and never reaches the Foundry IQ
knowledge source. ``classify_text`` is the (conservative) detector chunk_tag uses
to assign the ``phi`` classification in the first place.
"""
from __future__ import annotations

import re

# Conservative PHI markers. The corpus is synthetic/no-PHI by construction; these
# patterns exist so the gate is *provably* effective if a PHI-looking string ever
# slips into a source document. Kept deliberately broad (fail-closed).
_PHI_PATTERNS = [
    re.compile(r"\b756\.\d{4}\.\d{4}\.\d{2}\b"),          # Swiss AHV/AVS number
    re.compile(r"\bpatient\s+(?:name|id|record)\b", re.I),
    re.compile(r"\b(?:date\s+of\s+birth|geburtsdatum)\b", re.I),
    re.compile(r"\bmedical\s+record\s+number\b", re.I),
    re.compile(r"\bfallnummer\b", re.I),
]

PHI = "phi"


def classify_text(text: str, default: str = "public") -> str:
    """Return ``phi`` if the text matches any PHI marker, else ``default``."""
    for pattern in _PHI_PATTERNS:
        if pattern.search(text):
            return PHI
    return default


def is_phi(chunk: dict) -> bool:
    """A chunk is PHI if tagged ``phi`` OR its text still matches a PHI marker."""
    if chunk.get("classification") == PHI:
        return True
    return classify_text(chunk.get("text", "")) == PHI


def drop_phi(chunks: list[dict]) -> list[dict]:
    """Drop every PHI chunk. Fail-closed: re-checks text, not just the tag."""
    return [c for c in chunks if not is_phi(c)]
