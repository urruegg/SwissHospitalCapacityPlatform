"""Parse ``docs/region-availability.yaml`` into ``region_availability.json``.

Every availability fact must carry ``verifiedBy`` + ``asOf`` provenance
(design spec §3 / §11 GA-evidence curation-drift mitigation).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .common import resolve_commit

_SOURCE_REL = "docs/region-availability.yaml"


def parse_region_availability(path: Path, source_commit: str | None = None) -> list[dict]:
    """Return sorted region-availability rows from ``path``."""
    commit = source_commit or resolve_commit(path.parent)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    rows: list[dict] = []
    for fact in data.get("facts", []):
        row = {
            "bomId": fact["bomId"],
            "region": fact["region"],
            "maturity": fact["maturity"],
            "verifiedBy": fact["verifiedBy"],
            "asOf": str(fact["asOf"]),
            "sourceUrl": fact.get("sourceUrl"),
            "sourcePath": _SOURCE_REL,
            "sourceCommit": commit,
        }
        rows.append(row)

    return sorted(rows, key=lambda r: (r["bomId"], r["region"]))
