#!/usr/bin/env python3
"""Upload the synthetic FOCUS partitions to a lakehouse Bronze zone (T2).

Targets SIT by default; pass ``--workspace-id``/``--lakehouse-id`` (e.g. the
PROD coordinates from ``data-platform/fabric/environments.yml``) for a gated
PROD load.

Sprint 15 · T2 — the ``bva-sim-refresh`` workflow runs
``bva_synth_focus.py`` to emit a daily-partitioned dataset under a local
``out-dir`` and then calls this helper to push every partition file into
``Files/Bronze/consumption/`` in the SIT lakehouse, **preserving the FOCUS
partition path** (``BillingPeriod=YYYY-MM/ChargePeriodStart=YYYY-MM-DD/``) so the
Fabric medallion (T3) can ingest it as a partitioned source.

Design decisions:

* **Pure planning logic.** :func:`plan_uploads` walks the local partition tree
  and returns an ordered list of ``(local_path, remote_relpath)`` pairs. It does
  no I/O beyond reading the directory tree, so the partition-mapping behaviour is
  unit-testable without Azure credentials (matching the repo convention of
  keeping transform/plan logic framework-agnostic — see
  ``data-platform/notebooks/evidence/readiness_rules.py``).
* **Thin live layer.** :func:`upload_file` performs the OneLake DFS create /
  append / flush dance (same three-step contract as
  ``upload_to_onelake.py``). It is only exercised in the workflow, never in unit
  tests.
* **Idempotent target.** Files are overwritten in place (create with
  ``?resource=file`` truncates), so a re-run for the same seed/day is safe.

Usage::

    python3 bva_upload_bronze.py --src /tmp/bva --remote-root Bronze/consumption

Exit 0 on success, non-zero on failure.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE_ID = "f3af9733-9503-4e92-98f9-a901d96f1c87"
LAKEHOUSE_ID = "30594c20-46ba-40ea-91fa-4701b105e0b9"
ONELAKE_HOST = "https://onelake.dfs.fabric.microsoft.com"
DEFAULT_REMOTE_ROOT = "Bronze/consumption"
_BEARER = "Bearer "

# FOCUS partition part-file names emitted by bva_synth_focus.write_partitioned.
_PART_GLOBS = ("part-00000.parquet", "part-00000.jsonl", "part-00000.csv")


def plan_uploads(src_dir: str | os.PathLike[str]) -> list[tuple[str, str]]:
    """Walk ``src_dir`` and return ordered ``(local_path, remote_relpath)`` pairs.

    ``remote_relpath`` is the partition-preserving path relative to the Bronze
    consumption root, using forward slashes regardless of host OS.
    """
    root = Path(src_dir)
    if not root.is_dir():
        raise NotADirectoryError(f"source directory not found: {root}")

    pairs: list[tuple[str, str]] = []
    for path in sorted(root.rglob("part-00000.*")):
        if path.name not in _PART_GLOBS:
            continue
        rel = path.relative_to(root).as_posix()
        pairs.append((str(path), rel))

    if not pairs:
        raise FileNotFoundError(f"no FOCUS partition files found under {root}")
    return pairs


def _get_token() -> str:
    out = subprocess.check_output(
        [
            "az", "account", "get-access-token",
            "--resource", "https://storage.azure.com/",
            "--query", "accessToken", "-o", "tsv",
        ],
        text=True,
    )
    return out.strip()


def _remote_url(
    workspace_id: str, lakehouse_id: str, remote_root: str, remote_relpath: str
) -> str:
    """Build the OneLake DFS Files/ URL for one partition, environment-parametrized.

    ``workspace_id`` / ``lakehouse_id`` select the target environment (SIT or
    PROD) so the same partition tree can be uploaded to either by passing the
    coordinates from ``data-platform/fabric/environments.yml``. Uses forward
    slashes regardless of host OS.
    """
    return (
        f"{ONELAKE_HOST}/{workspace_id}/{lakehouse_id}/Files/"
        f"{remote_root}/{remote_relpath}"
    )


def upload_file(
    local_path: str,
    remote_relpath: str,
    remote_root: str,
    token: str,
    workspace_id: str = WORKSPACE_ID,
    lakehouse_id: str = LAKEHOUSE_ID,
) -> int:
    """Upload one partition file via the OneLake DFS create/append/flush contract.

    Returns the number of bytes uploaded.
    """
    import requests  # imported lazily so unit tests need no network dependency

    base = _remote_url(workspace_id, lakehouse_id, remote_root, remote_relpath)
    headers = {"Authorization": f"{_BEARER}{token}"}

    r = requests.put(f"{base}?resource=file", headers=headers)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"create failed for {remote_relpath}: {r.status_code} {r.text}")

    content = Path(local_path).read_bytes()
    length = len(content)
    if length > 0:
        r = requests.patch(
            f"{base}?action=append&position=0",
            headers={
                **headers,
                "Content-Length": str(length),
                "Content-Type": "application/octet-stream",
            },
            data=content,
        )
        if r.status_code not in (200, 202):
            raise RuntimeError(f"append failed for {remote_relpath}: {r.status_code} {r.text}")

    r = requests.patch(f"{base}?action=flush&position={length}", headers=headers)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"flush failed for {remote_relpath}: {r.status_code} {r.text}")

    return length


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload FOCUS partitions to lakehouse Bronze.")
    parser.add_argument("--src", required=True, help="Local out-dir produced by bva_synth_focus.py.")
    parser.add_argument(
        "--remote-root",
        default=DEFAULT_REMOTE_ROOT,
        help=f"Remote folder under Files/ (default: {DEFAULT_REMOTE_ROOT}).",
    )
    parser.add_argument(
        "--workspace-id",
        default=WORKSPACE_ID,
        help=f"Target Fabric workspace id (default: SIT {WORKSPACE_ID}). "
        "Pass the PROD workspace id from environments.yml for a PROD load.",
    )
    parser.add_argument(
        "--lakehouse-id",
        default=LAKEHOUSE_ID,
        help=f"Target lakehouse id (default: SIT {LAKEHOUSE_ID}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the upload plan and exit without contacting OneLake.",
    )
    args = parser.parse_args(argv)

    try:
        pairs = plan_uploads(args.src)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(
        f"Planned {len(pairs)} partition upload(s) to Files/{args.remote_root}/ "
        f"in workspace {args.workspace_id} / lakehouse {args.lakehouse_id}"
    )
    if args.dry_run:
        for _, rel in pairs:
            print(f"  DRY-RUN {rel}")
        return 0

    token = _get_token()
    total_bytes = 0
    for local, rel in pairs:
        total_bytes += upload_file(
            local, rel, args.remote_root, token,
            workspace_id=args.workspace_id, lakehouse_id=args.lakehouse_id,
        )
        print(f"  uploaded {rel}")

    print(f"PASS: uploaded {len(pairs)} files ({total_bytes} bytes) to Files/{args.remote_root}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
