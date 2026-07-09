"""Parse ``docs/adr/*.md`` into ADR rows plus requirement/ADR map edges.

ADR front-matter is inconsistent across the repo: some files use a bullet list
(``- Status: **Accepted**``), others a Markdown table (``| **Status** | ... |``).
Both shapes are handled by scanning field labels rather than a fixed grammar.
"""

from __future__ import annotations

import re
from pathlib import Path

from .common import resolve_commit, sort_rows

ADR_REF_RE = re.compile(r"ADR-(\d{4})")
REQ_ID_RE = re.compile(r"(?:FR|NFR)-[A-Z-]+-\d{3}")
FILENAME_ID_RE = re.compile(r"^(\d{4})")
TITLE_RE = re.compile(r"^#\s+ADR-\d{4}\s*[—:-]\s*(.+?)\s*$")

_STATUS_KEYWORDS = [
    ("supersed", "Superseded"),
    ("deprecat", "Deprecated"),
    ("reject", "Rejected"),
    ("accept", "Accepted"),
    ("propos", "Proposed"),
]


def parse_adrs(adr_dir: Path, source_commit: str | None = None) -> tuple[list[dict], list[dict]]:
    """Return ``(adr_rows, req_adr_map_rows)`` for every ADR under ``adr_dir``."""
    commit = source_commit or resolve_commit(adr_dir)
    adr_rows: list[dict] = []
    map_rows: list[dict] = []

    for adr_path in sorted(adr_dir.glob("*.md")):
        id_match = FILENAME_ID_RE.match(adr_path.name)
        if not id_match:
            continue
        adr_id = f"ADR-{id_match.group(1)}"
        text = adr_path.read_text(encoding="utf-8")
        source_rel = f"docs/adr/{adr_path.name}"

        title = _extract_title(text, adr_path.name)
        status = _extract_status(text)
        status_line = _field_value(text, "Status")
        supersedes = _refs(_field_value(text, "Supersedes"))
        superseded_by = _refs(status_line if "supersed" in status_line.lower() else "")
        superseded_by += _refs(_field_value(text, "Superseded by"))
        superseded_by = [ref for ref in superseded_by if ref != adr_id]

        adr_row = {
            "id": adr_id,
            "title": title,
            "status": status,
            "decisionSummary": _extract_decision(text),
            "sourcePath": source_rel,
            "sourceCommit": commit,
        }
        if supersedes:
            adr_row["supersedes"] = sorted(set(supersedes))
        if superseded_by:
            adr_row["supersededBy"] = sorted(set(superseded_by))
        adr_rows.append(adr_row)

        for req_id in _requirements(text):
            map_rows.append(
                {
                    "requirementId": req_id,
                    "adrId": adr_id,
                    "relationship": "governs",
                    "sourcePath": source_rel,
                    "sourceCommit": commit,
                }
            )

    adr_rows = sort_rows(adr_rows, key="id")
    map_rows = _dedupe_map(map_rows)
    return adr_rows, map_rows


def _extract_title(text: str, filename: str) -> str:
    for line in text.splitlines():
        match = TITLE_RE.match(line)
        if match:
            return match.group(1)
    # Fall back to the humanised filename slug.
    slug = re.sub(r"^\d{4}(?:-\d{4})?-", "", filename)
    slug = slug.rsplit(".", 1)[0]
    return slug.replace("-", " ").strip().title() or filename


def _field_value(text: str, label: str) -> str:
    label_re = re.escape(label)
    # Bullet form: - Label: value
    bullet = re.search(rf"^-\s*{label_re}\s*:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if bullet:
        return bullet.group(1).strip()
    # Table form: | **Label** | value |
    table = re.search(
        rf"^\|\s*\*{{0,2}}{label_re}\*{{0,2}}\s*\|\s*(.+?)\s*\|\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if table:
        return table.group(1).strip()
    return ""


def _extract_status(text: str) -> str:
    value = _field_value(text, "Status").lower()
    for needle, canonical in _STATUS_KEYWORDS:
        if needle in value:
            return canonical
    return "Accepted"


def _extract_decision(text: str) -> str:
    match = re.search(r"^##\s+Decision\s*$(.+?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    body = match.group(1).strip()
    # First non-empty paragraph, whitespace-normalised.
    for para in re.split(r"\n\s*\n", body):
        cleaned = " ".join(para.split())
        if cleaned:
            return cleaned
    return ""


def _refs(value: str) -> list[str]:
    return [f"ADR-{num}" for num in ADR_REF_RE.findall(value)]


def _requirements(text: str) -> list[str]:
    values = " ".join(
        _field_value(text, label)
        for label in ("Related Requirements", "Related requirements", "Realises")
    )
    return REQ_ID_RE.findall(values)


def _dedupe_map(rows: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for row in rows:
        key = (row["requirementId"], row["adrId"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return sorted(unique, key=lambda r: (r["requirementId"], r["adrId"]))
