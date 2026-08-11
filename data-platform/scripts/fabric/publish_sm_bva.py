#!/usr/bin/env python3
"""Publish the local sm_bva.SemanticModel/ folder as the live Fabric definition.

Walks the committed TMDL project folder and uploads every file as a
``definition.parts[]`` entry, matching the exact path shape Fabric's own
``getDefinition`` returns for this item (confirmed live 2026-08-11):
``definition.pbism``, ``.platform``, and everything under ``definition/``
(``model.tmdl``, ``database.tmdl``, ``expressions.tmdl``, ``roles/*.tmdl``,
``tables/*.tmdl``).

Usage::

    python data-platform/scripts/fabric/publish_sm_bva.py \
        --workspace-id <ws> --item-id <semantic-model-item-id> --dry-run

Publish is a ``deploy``-ceiling action gated by ``approved-to-apply``
(AGENTS.md Section 4).
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import sys
import time
from pathlib import Path

import requests

FABRIC_API = "https://api.fabric.microsoft.com/v1"
REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = REPO_ROOT / "data-platform" / "reports" / "sm_bva.SemanticModel"


def collect_parts() -> list[dict]:
    parts = []
    for path in sorted(MODEL_DIR.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(MODEL_DIR).as_posix()
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        parts.append({"path": rel, "payload": payload, "payloadType": "InlineBase64"})
    return parts


def get_token() -> str:
    return subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    ).strip()


def _wait_lro(location: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(30):
        r = requests.get(location, headers=headers)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "")
        if status == "Succeeded":
            return
        if status == "Failed":
            raise RuntimeError(f"LRO failed: {data}")
        time.sleep(10)
    raise TimeoutError("LRO did not complete in time")


def publish(workspace_id: str, item_id: str, dry_run: bool) -> None:
    parts = collect_parts()
    if dry_run:
        print(f"[DRY-RUN] Would publish {len(parts)} parts to item {item_id}:")
        for p in parts:
            print(f"  {p['path']} ({len(p['payload'])} b64 chars)")
        return

    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{FABRIC_API}/workspaces/{workspace_id}/items/{item_id}/updateDefinition"
    r = requests.post(url, headers=headers, json={"definition": {"parts": parts}})
    if r.status_code == 202:
        _wait_lro(r.headers.get("Location", ""), token)
        print(f"updated semantic model {item_id} ({len(parts)} parts)")
    elif r.status_code in (200, 201):
        print(f"updated semantic model {item_id} ({len(parts)} parts)")
    else:
        raise RuntimeError(f"updateDefinition failed {r.status_code}: {r.text}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--item-id", required=True)
    p.add_argument("--dry-run", action="store_true")
    ns = p.parse_args(argv if argv is not None else sys.argv[1:])
    publish(ns.workspace_id, ns.item_id, ns.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
