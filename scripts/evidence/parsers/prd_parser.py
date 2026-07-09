"""Parse ``docs/PRD.md`` into one evidence row per FR-*/NFR-* requirement.

Requirements live in Markdown tables under ``### <letter>) <Family>`` headings,
one per row: ``| `FR-OM-001` | The solution shall ... |``.
"""

from __future__ import annotations

import re
from pathlib import Path

from .common import resolve_commit, sort_rows

REQ_ID_RE = re.compile(r"^(FR|NFR)-[A-Z]+(?:-[A-Z]+)*-\d{3}$")
# Table row: | `FR-OM-001` | description text |
ROW_RE = re.compile(r"^\|\s*`((?:FR|NFR)-[A-Z-]+-\d{3})`\s*\|\s*(.+?)\s*\|\s*$")
# Family heading: ### A) Operating Model And Product Scope
FAMILY_RE = re.compile(r"^###\s+[A-Z]\)\s+(.+?)\s*$")
MVP_TOKEN_RE = re.compile(r"\bMVP\b", re.IGNORECASE)


def parse_prd(prd_path: Path, source_commit: str | None = None) -> list[dict]:
    """Return sorted requirement rows extracted from ``prd_path``."""
    text = prd_path.read_text(encoding="utf-8")
    commit = source_commit or resolve_commit(prd_path.parent)
    source_rel = _repo_relative(prd_path)

    rows: list[dict] = []
    seen: set[str] = set()
    current_family = "Unclassified"

    for line_no, line in enumerate(text.splitlines(), start=1):
        family_match = FAMILY_RE.match(line)
        if family_match:
            current_family = family_match.group(1)
            continue

        row_match = ROW_RE.match(line)
        if not row_match:
            continue
        req_id, title = row_match.group(1), row_match.group(2).strip()
        if not REQ_ID_RE.match(req_id) or req_id in seen:
            continue
        seen.add(req_id)
        rows.append(
            {
                "id": req_id,
                "kind": req_id.split("-", 1)[0],
                "family": current_family,
                "title": title,
                "mvp": bool(MVP_TOKEN_RE.search(title) or MVP_TOKEN_RE.search(current_family)),
                "sourcePath": source_rel,
                "sourceLine": line_no,
                "sourceCommit": commit,
            }
        )

    return sort_rows(rows, key="id")


def _repo_relative(path: Path) -> str:
    parts = path.resolve().parts
    if "docs" in parts:
        idx = parts.index("docs")
        return "/".join(parts[idx:])
    return path.name
