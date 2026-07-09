"""Parse ``docs/bom.yaml`` into ``bom.json`` items and ``dependencies.json`` edges."""

from __future__ import annotations

from pathlib import Path

import yaml

from .common import resolve_commit, sort_rows

_SOURCE_REL = "docs/bom.yaml"
_ITEM_FIELDS = ("sku", "realisesRequirements", "governedByAdrs")


def parse_bom(bom_path: Path, source_commit: str | None = None) -> tuple[list[dict], list[dict]]:
    """Return ``(bom_rows, dependency_rows)`` from ``bom_path``."""
    commit = source_commit or resolve_commit(bom_path.parent)
    data = yaml.safe_load(bom_path.read_text(encoding="utf-8")) or {}
    items = data.get("items", [])

    bom_rows: list[dict] = []
    dep_rows: list[dict] = []

    for item in items:
        bom_id = item["id"]
        row = {
            "id": bom_id,
            "name": item["name"],
            "type": item["type"],
            "category": item["category"],
            "sourcePath": _SOURCE_REL,
            "sourceCommit": commit,
        }
        for field in _ITEM_FIELDS:
            if field in item and item[field] is not None:
                row[field] = item[field]
        bom_rows.append(row)

        for dep in item.get("dependsOn", []) or []:
            dep_rows.append(
                {
                    "fromId": bom_id,
                    "toId": dep["to"],
                    "type": dep["type"],
                    "sourcePath": _SOURCE_REL,
                    "sourceCommit": commit,
                }
            )

    bom_rows = sort_rows(bom_rows, key="id")
    dep_rows = sorted(dep_rows, key=lambda r: (r["fromId"], r["toId"], r["type"]))
    return bom_rows, dep_rows
