"""WS-A Class A corpus: chunking + tagging (Sprint 28, issue #377).

Splits a source Markdown document into chunks at heading / ADR / contract
boundaries and tags each chunk with the provenance metadata the citation layer
and the PHI gate need: ``classification`` / ``residency`` / ``status`` /
``version`` / ``commit`` / ``date`` / ``language`` (FR-POA-004). Interviews under
``docs/reviews/`` are **first-order**: they carry ``is_interview=True`` and their
own ``interview`` tag so publish can rank them ahead of secondary material.

Chunks produced here are the internal ``TaggedChunk`` shape; ``publish`` converts
the survivors into the frozen ``GroundedChunk`` contract.
"""
from __future__ import annotations

import re

import phi_gate

# Heading boundary: a Markdown ATX heading line (#..######) starts a new chunk.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
# Version / Date rows in the conventional doc header table (| Version | x.y.z |).
_VERSION_RE = re.compile(r"\|\s*\*\*Version\*\*\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|", re.I)
_DATE_RE = re.compile(r"\|\s*\*\*Date\*\*\s*\|\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.I)

# A few high-signal German tokens for language detection (source-language parity).
_DE_TOKENS = {
    "und", "der", "die", "das", "nicht", "mit", "für", "ist", "auch", "werden",
    "eine", "einen", "kapazität", "krankenhaus", "sprache", "zusammenfassung",
}
_EN_TOKENS = {
    "the", "and", "of", "to", "is", "for", "with", "not", "this", "that",
    "capacity", "hospital", "summary", "language", "answer",
}


def detect_language(text: str) -> str:
    """Return ``de`` or ``en`` by simple stopword voting (defaults to ``en``)."""
    words = re.findall(r"[a-zäöüß]+", text.lower())
    if not words:
        return "en"
    de = sum(1 for w in words if w in _DE_TOKENS)
    en = sum(1 for w in words if w in _EN_TOKENS)
    # German-only characters are a strong signal even without stopword hits.
    if re.search(r"[äöüß]", text.lower()):
        de += 1
    return "de" if de > en else "en"


def _extract_version(text: str) -> str | None:
    m = _VERSION_RE.search(text)
    return m.group(1) if m else None


def _extract_date(text: str) -> str | None:
    m = _DATE_RE.search(text)
    return m.group(1) if m else None


def _residency_for(source_path: str) -> str:
    """All corpus documents are Swiss-resident synthetic material."""
    return "ch"


def _is_interview(source_path: str) -> bool:
    norm = source_path.replace("\\", "/").lower()
    return "/docs/reviews/" in norm or norm.startswith("docs/reviews/")


def chunk_document(source_path: str, text: str, commit: str) -> list[dict]:
    """Split ``text`` into TaggedChunks at heading boundaries.

    A document with no headings yields a single chunk (anchor ``None``). The
    conventional doc-header ``Version`` / ``Date`` rows, if present anywhere in
    the document, are propagated to every chunk as provenance.
    """
    doc_version = _extract_version(text)
    doc_date = _extract_date(text)
    interview = _is_interview(source_path)

    sections: list[tuple[str | None, list[str]]] = []
    current_anchor: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            if current_lines:
                sections.append((current_anchor, current_lines))
            current_anchor = m.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_anchor, current_lines))

    chunks: list[dict] = []
    for anchor, lines in sections:
        body = "\n".join(lines).strip()
        if not body:
            continue
        chunks.append({
            "text": body,
            "source_path": source_path,
            "commit": commit,
            "anchor": anchor,
            "classification": phi_gate.classify_text(body, default="public"),
            "residency": _residency_for(source_path),
            "status": "verified",
            "version": doc_version,
            "date": doc_date,
            "language": detect_language(body),
            "is_interview": interview,
        })
    return chunks
