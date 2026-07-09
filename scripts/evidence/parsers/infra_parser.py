"""Walk ``infra/**`` Bicep modules into a lightweight ``deployed_bom.json`` stub.

This is intentionally a **stub** — the full ARG-based deployed BOM is out of
scope for Sprint 14 (design spec §2.2). We map each declared Bicep ``resource``
to its module path so a later sprint can reconcile it against ARG actuals.
"""

from __future__ import annotations

import re
from pathlib import Path

from .common import resolve_commit

# resource <symbolicName> 'Microsoft.Foo/bars@2023-01-01' = { ... }
RESOURCE_RE = re.compile(
    r"^resource\s+(?P<name>\w+)\s+'(?P<type>[^'@]+)@[^']+'\s*=", re.MULTILINE
)


def parse_infra(infra_dir: Path, repo_root: Path | None = None, source_commit: str | None = None) -> list[dict]:
    """Return sorted infra-snapshot rows from Bicep modules under ``infra_dir``."""
    root = repo_root or infra_dir.parent
    commit = source_commit or resolve_commit(root)

    rows: list[dict] = []
    for bicep_path in sorted(infra_dir.rglob("*.bicep")):
        module_rel = _repo_relative(bicep_path, root)
        text = bicep_path.read_text(encoding="utf-8")
        for match in RESOURCE_RE.finditer(text):
            symbolic = match.group("name")
            res_type = match.group("type")
            rows.append(
                {
                    "resourceId": f"{module_rel}#{symbolic}",
                    "resourceType": res_type,
                    "modulePath": module_rel,
                    "sourcePath": module_rel,
                    "sourceCommit": commit,
                }
            )

    return sorted(rows, key=lambda r: r["resourceId"])


def _repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name
