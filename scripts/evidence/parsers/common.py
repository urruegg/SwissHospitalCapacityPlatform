"""Shared helpers for the evidence parsers.

Design invariants (see design spec §3 and plan T1):

* **Byte-stable output** — parser output must be deterministic for a fixed input
  state so CI can diff it. We never embed wall-clock time; provenance uses the
  source commit + input ``asOf`` fields instead. JSON is dumped with sorted keys
  and a trailing newline.
* **Provenance on every row** — callers attach ``sourcePath`` / ``sourceCommit``
  (and ``asOf`` / ``sourceUrl`` where the source carries them).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

UNKNOWN_COMMIT = "UNKNOWN"


def resolve_commit(repo_root: Path | None = None) -> str:
    """Return the current git HEAD sha, or ``UNKNOWN`` when unavailable.

    Kept out of the row payload builders so tests can inject a fixed commit and
    assert byte-stable output.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root) if repo_root else None,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or UNKNOWN_COMMIT
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return UNKNOWN_COMMIT


def sort_rows(rows: Iterable[dict], key: str = "id") -> list[dict]:
    """Return rows sorted by a stable composite key for deterministic output."""

    def _key(row: dict) -> tuple:
        if key in row:
            return (str(row.get(key, "")),)
        # Fall back to a stable ordering over all values when no single id.
        return tuple(str(row.get(k, "")) for k in sorted(row))

    return sorted(rows, key=_key)


def dumps(rows: Any) -> str:
    """Serialise rows to byte-stable JSON with a trailing newline."""
    return json.dumps(rows, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, rows: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(rows), encoding="utf-8")
