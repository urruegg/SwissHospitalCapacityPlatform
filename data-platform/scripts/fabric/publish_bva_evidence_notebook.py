#!/usr/bin/env python3
"""Publish the BVA evidence & narrative Gold notebook to a Fabric workspace.

Mirrors the already-live ``build_gold_bva_costbasis`` notebook exactly: the
Fabric "notebook-content.py" source format (``# CELL ****`` markers in one
flat .py file), Cell 1 is the entire pure-transform module
(``data-platform/bva/evidence_grounding.py``) pasted verbatim -- Fabric
notebooks cannot ``import`` a repo-local .py without a custom-library upload
(same reasoning as ``bva_medallion_ingest.ipynb``'s own docstring) -- and
Cell 2 reads the ten committed CSVs from the local-mounted
``/lakehouse/default/Files/master-data/bva`` path and writes the ten
``gold.bva_evidence_*`` Delta tables.

Usage:
    python data-platform/scripts/fabric/publish_bva_evidence_notebook.py \
        --workspace-id <ws> --lakehouse-id <lh> --lakehouse-name <name>

Deploy (publish) is a ``deploy``-ceiling action gated by ``approved-to-apply``
(AGENTS.md Section 4).
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

import requests

FABRIC_API = "https://api.fabric.microsoft.com/v1"
REPO_ROOT = Path(__file__).resolve().parents[3]
TRANSFORM_MODULE = REPO_ROOT / "data-platform" / "bva" / "evidence_grounding.py"
DISPLAY_NAME = "build_gold_bva_evidence"

CELL2_SOURCE = '''# BVA evidence & narrative Gold -- self-contained deploy notebook (Sprint 44
# follow-up). Reads the 10 committed master-data CSVs from OneLake Files via
# plain Python (utf-8-sig, byte-stable pure transform inlined above) and
# writes the 10 Gold Delta tables. Overwrite-mode; rollback = re-run from the
# golden-source CSVs.
from pathlib import Path

MASTER = "/lakehouse/default/Files/master-data/bva"
tables = build_evidence_gold_tables(Path(MASTER))

spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
for name, rows in tables.items():
    df = spark.createDataFrame(rows)
    (df.write.format("delta").mode("overwrite")
       .option("overwriteSchema", "true").saveAsTable(f"gold.{name}"))
    print(f"wrote gold.{name} ({df.count()} rows)")
print("BVA evidence & narrative Gold complete (10 tables)")
'''


def build_notebook_source(lakehouse_id: str, lakehouse_name: str, workspace_id: str) -> str:
    transform_code = TRANSFORM_MODULE.read_text(encoding="utf-8")
    metadata = (
        "# Fabric notebook source\n\n"
        "# METADATA ********************\n\n"
        "# META {\n"
        '# META   "dependencies": {\n'
        '# META     "lakehouse": {\n'
        f'# META       "default_lakehouse": "{lakehouse_id}",\n'
        f'# META       "default_lakehouse_name": "{lakehouse_name}",\n'
        f'# META       "default_lakehouse_workspace_id": "{workspace_id}"\n'
        "# META     }\n"
        "# META   }\n"
        "# META }\n\n"
        "# CELL ********************\n\n"
    )
    return metadata + transform_code + "\n# CELL ********************\n\n" + CELL2_SOURCE


def get_token() -> str:
    return subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    ).strip()


def list_notebooks(workspace_id: str, token: str) -> dict[str, str]:
    r = requests.get(f"{FABRIC_API}/workspaces/{workspace_id}/notebooks",
                      headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return {item["displayName"]: item["id"] for item in r.json().get("value", [])}


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
        time.sleep(5)
    raise TimeoutError("LRO did not complete in time")


def publish(workspace_id: str, lakehouse_id: str, lakehouse_name: str, dry_run: bool) -> str:
    source = build_notebook_source(lakehouse_id, lakehouse_name, workspace_id)
    payload_b64 = base64.b64encode(source.encode("utf-8")).decode("ascii")
    definition = {
        "parts": [{
            "path": "notebook-content.py",
            "payload": payload_b64,
            "payloadType": "InlineBase64",
        }],
    }

    if dry_run:
        print(f"[DRY-RUN] Would publish {DISPLAY_NAME} ({len(payload_b64)} b64 chars)")
        return "dry-run-id"

    token = get_token()
    existing = list_notebooks(workspace_id, token)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if DISPLAY_NAME in existing:
        nb_id = existing[DISPLAY_NAME]
        url = f"{FABRIC_API}/workspaces/{workspace_id}/items/{nb_id}/updateDefinition"
        r = requests.post(url, headers=headers, json={"definition": definition})
        if r.status_code == 202:
            _wait_lro(r.headers.get("Location", ""), token)
        elif r.status_code not in (200, 201):
            raise RuntimeError(f"updateDefinition failed {r.status_code}: {r.text}")
        print(f"updated {DISPLAY_NAME} (id={nb_id})")
        return nb_id

    url = f"{FABRIC_API}/workspaces/{workspace_id}/items"
    body = {
        "displayName": DISPLAY_NAME,
        "type": "Notebook",
        "description": "BVA evidence & narrative Gold (Sprint 44 follow-up)",
        "definition": definition,
    }
    r = requests.post(url, headers=headers, json=body)
    if r.status_code == 202:
        _wait_lro(r.headers.get("Location", ""), token)
        # Re-list to get the new item id.
        existing = list_notebooks(workspace_id, token)
        nb_id = existing[DISPLAY_NAME]
    elif r.status_code == 201:
        nb_id = r.json()["id"]
    else:
        raise RuntimeError(f"create failed {r.status_code}: {r.text}")
    print(f"created {DISPLAY_NAME} (id={nb_id})")
    return nb_id


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--lakehouse-id", required=True)
    p.add_argument("--lakehouse-name", required=True)
    p.add_argument("--dry-run", action="store_true")
    ns = p.parse_args(argv if argv is not None else sys.argv[1:])
    publish(ns.workspace_id, ns.lakehouse_id, ns.lakehouse_name, ns.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
