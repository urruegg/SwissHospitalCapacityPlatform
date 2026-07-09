"""Evidence parsers for the Sprint 14 Showcase Evidence data product.

Each parser reads a canonical repo source (PRD, ADRs, BOM catalog,
region-availability catalog, infra tree) and emits byte-stable JSON rows with
provenance. See ``docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md``.
"""

from .common import (
    UNKNOWN_COMMIT,
    dumps,
    resolve_commit,
    sort_rows,
    write_json,
)

__all__ = [
    "UNKNOWN_COMMIT",
    "dumps",
    "resolve_commit",
    "sort_rows",
    "write_json",
]
