"""Import local .ipynb notebooks into a Fabric workspace via REST.

Usage:
    python import_notebooks.py <workspace-id> <notebook-glob> [--lakehouse-id ID] [--lakehouse-name NAME] [--dry-run]

Example:
    python import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/**/*.ipynb" \
        --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests

FABRIC_API = "https://api.fabric.microsoft.com/v1"


def get_token() -> str:
    return subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    ).strip()


def list_notebooks(workspace_id: str, token: str) -> dict[str, str]:
    """Return {displayName: id} for notebooks in the workspace."""
    r = requests.get(f"{FABRIC_API}/workspaces/{workspace_id}/notebooks",
                     headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return {item["displayName"]: item["id"] for item in r.json().get("value", [])}


def import_notebook(workspace_id: str, local_path: Path, existing_id: Optional[str], token: str, dry_run: bool,
                    lakehouse_id: Optional[str] = None, lakehouse_name: Optional[str] = None) -> str:
    display_name = local_path.stem

    if lakehouse_id and lakehouse_name:
        nb = json.loads(local_path.read_text(encoding="utf-8"))
        nb.setdefault("metadata", {}).setdefault("dependencies", {})["lakehouse"] = {
            "default_lakehouse": lakehouse_id,
            "default_lakehouse_name": lakehouse_name,
            "default_lakehouse_workspace_id": workspace_id,
        }
        content_bytes = json.dumps(nb, indent=1).encode("utf-8")
    else:
        content_bytes = local_path.read_bytes()

    content_b64 = base64.b64encode(content_bytes).decode("ascii")

    body = {
        "displayName": display_name,
        "description": f"Imported from {local_path.as_posix()}",
        "definition": {
            "format": "ipynb",
            "parts": [{
                "path": "notebook-content.ipynb",
                "payload": content_b64,
                "payloadType": "InlineBase64",
            }],
        },
    }

    if dry_run:
        print(f"[DRY-RUN] Would {'update' if existing_id else 'create'} {display_name} "
              f"({len(content_b64)} b64 chars)")
        return existing_id or "dry-run-id"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if existing_id:
        # Update existing definition
        url = f"{FABRIC_API}/workspaces/{workspace_id}/notebooks/{existing_id}/updateDefinition"
        r = requests.post(url, headers=headers, json={"definition": body["definition"]})
        if r.status_code == 202:
            # Long-running operation
            _wait_lro(r.headers.get("Location", r.headers.get("x-ms-operation-id")), token)
        r.raise_for_status()
        print(f"  updated {display_name} (id={existing_id})")
        return existing_id
    else:
        # Create new
        url = f"{FABRIC_API}/workspaces/{workspace_id}/notebooks"
        r = requests.post(url, headers=headers, json=body)
        if r.status_code == 202:
            op_url = r.headers.get("Location") or f"{FABRIC_API}/operations/{r.headers.get('x-ms-operation-id')}"
            result = _wait_lro(op_url, token)
            nb_id = result.get("id") if isinstance(result, dict) else None
            print(f"  created {display_name} (id={nb_id})")
            return nb_id or ""
        r.raise_for_status()
        nb_id = r.json().get("id")
        print(f"  created {display_name} (id={nb_id})")
        return nb_id


def _wait_lro(op_url: str, token: str, timeout_sec: int = 300) -> dict:
    """Poll a long-running operation until it completes."""
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    while time.time() - start < timeout_sec:
        r = requests.get(op_url, headers=headers)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "").lower()
        if status in ("succeeded", "completed"):
            # Try to fetch the result
            if "Location" in r.headers:
                r2 = requests.get(r.headers["Location"], headers=headers)
                if r2.ok:
                    return r2.json()
            return data
        if status in ("failed", "cancelled"):
            raise RuntimeError(f"LRO {status}: {data}")
        time.sleep(2)
    raise TimeoutError(f"LRO did not complete within {timeout_sec}s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import notebooks to Fabric workspace")
    parser.add_argument("workspace_id")
    parser.add_argument("pattern", help="Glob for .ipynb files")
    parser.add_argument("--lakehouse-id", default=None,
                        help="Attach as default lakehouse (id).")
    parser.add_argument("--lakehouse-name", default=None,
                        help="Attach as default lakehouse (display name).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = sorted(Path(p) for p in glob.glob(args.pattern, recursive=True))
    if not paths:
        print(f"No files match {args.pattern}")
        return 1

    token = get_token()
    existing = list_notebooks(args.workspace_id, token) if not args.dry_run else {}
    print(f"Importing {len(paths)} notebook(s) to workspace {args.workspace_id} "
          f"({len(existing)} existing) ...")

    for p in paths:
        display_name = p.stem
        try:
            import_notebook(args.workspace_id, p, existing.get(display_name), token, args.dry_run,
                           lakehouse_id=args.lakehouse_id, lakehouse_name=args.lakehouse_name)
        except Exception as e:
            print(f"  FAILED {display_name}: {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
