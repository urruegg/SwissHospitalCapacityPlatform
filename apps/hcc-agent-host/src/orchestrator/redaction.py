"""Sprint 13 T5 — redaction of PHI-ish and secret-like tokens.

Agents must never echo PHI or secrets (AGENTS.md §5, copilot-instructions §4).
This is a defence-in-depth pass over any text the host is about to return or
persist; the demo scope is synthetic-only (ADR-0016) so this guards against
accidental leakage rather than real PHI handling.
"""

from __future__ import annotations

import re

# Secret-like patterns: JWTs, bearer tokens, connection strings, GitHub PATs.
_SECRET_PATTERNS = [
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(?:AccountKey|SharedAccessKey|password)=[^;\s]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"),
]

# Swiss AHV social-insurance number (756.xxxx.xxxx.xx) — a PHI identifier.
_AHV_PATTERN = re.compile(r"\b756\.\d{4}\.\d{4}\.\d{2}\b")

REDACTED = "[redacted]"


def redact(text: str) -> str:
    """Return ``text`` with secret-like and AHV-like tokens masked."""
    if not text:
        return text
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(REDACTED, text)
    text = _AHV_PATTERN.sub(REDACTED, text)
    return text


def contains_sensitive(text: str) -> bool:
    """True when ``text`` matches any secret- or AHV-like pattern."""
    if not text:
        return False
    if _AHV_PATTERN.search(text):
        return True
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)
