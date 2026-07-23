#!/usr/bin/env python3
"""Add a semantic-model data source to a Fabric Data Agent via the Items REST API.

Adds a ``semantic_model`` grounding source (all tables/columns selected) to both
the ``draft`` and ``published`` stages of a Data Agent item, and appends one
instruction line to the stage_config ``aiInstructions``. The source schema is
parsed from the semantic model's TMDL table definitions so the element list
mirrors what the portal ``Add data`` dialog would produce.

Used for Sprint 21 M3 (signal Fabric evidence, Task 8): ground
``da_hospital_capacity`` on the ``external-signals`` Direct Lake model so the
ontology/data-agent layer can answer ``DC-EXT-SIGNAL-v1`` questions.

This performs a **transactional** ``updateDefinition`` (Fabric validates before
applying). A full pre-change backup of the definition is always written first.
The apply itself is a governed action (AGENTS.md Section 4) - run with
``--apply`` only after an ``approved-to-apply`` comment on the governing issue.

Auth: uses ``az account get-access-token`` for the Fabric resource; run
``az login`` first. Non-mutating by default (``--dry-run`` assembles the parts
and writes them to ``--out`` without calling ``updateDefinition``).
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
API = "https://api.fabric.microsoft.com/v1"

# TMDL dataType -> Data Agent element data_type token.
_DTYPE = {
    "string": "String",
    "int64": "Int64",
    "double": "Double",
    "boolean": "Boolean",
    "dateTime": "DateTime",
    "decimal": "Double",
}

_COL_RE = re.compile(r"^\s*column\s+('([^']+)'|(\S+))")
_DTYPE_RE = re.compile(r"^\s*dataType:\s*(\S+)")
_REL_FROM_RE = re.compile(r"^\s*fromColumn:\s*(\S+)\.(\S+)")
_REL_TO_RE = re.compile(r"^\s*toColumn:\s*(\S+)\.(\S+)")


def _token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource", FABRIC_RESOURCE,
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def _req(method: str, url: str, token: str, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req)


def _poll_lro(resp, token: str) -> dict:
    """Follow a 202 Long-Running-Operation to its result body."""
    loc = resp.headers.get("Location")
    if resp.status != 202 or not loc:
        return json.loads(resp.read().decode())
    while True:
        time.sleep(3)
        p = _req("GET", loc, token)
        st = json.loads(p.read().decode()).get("status")
        if st in ("Succeeded", "Failed"):
            break
    if st == "Failed":
        raise RuntimeError(f"LRO failed: {loc}")
    return json.loads(_req("GET", f"{loc}/result", token).read().decode())


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _decode(part: dict) -> str:
    return base64.b64decode(part["payload"]).decode("utf-8")


def _parse_tables(model_dir: Path) -> list[dict]:
    """Return [{name, columns:[{name, data_type}]}] from TMDL table files."""
    tables: list[dict] = []
    for tmdl in sorted((model_dir / "definition" / "tables").glob("*.tmdl")):
        cols: list[dict] = []
        pending: str | None = None
        for line in tmdl.read_text(encoding="utf-8").splitlines():
            m = _COL_RE.match(line)
            if m:
                pending = m.group(2) or m.group(3)
                continue
            d = _DTYPE_RE.match(line)
            if d and pending is not None:
                cols.append({"name": pending, "data_type": _DTYPE.get(d.group(1), "String")})
                pending = None
        tables.append({"name": tmdl.stem, "columns": cols})
    return tables


def _parse_relationships(model_dir: Path) -> list[dict]:
    rels: list[dict] = []
    rf = model_dir / "definition" / "relationships.tmdl"
    if not rf.exists():
        return rels
    frm: tuple[str, str] | None = None
    for line in rf.read_text(encoding="utf-8").splitlines():
        f = _REL_FROM_RE.match(line)
        if f:
            frm = (f.group(1), f.group(2))
            continue
        t = _REL_TO_RE.match(line)
        if t and frm is not None:
            rels.append({
                "FromTable": frm[0], "FromColumn": frm[1],
                "ToTable": t.group(1), "ToColumn": t.group(2),
                "IsActive": True, "IsBidirectional": False, "Cardinality": "ManyToOne",
            })
            frm = None
    return rels


def build_datasource(artifact_id: str, workspace_id: str, display_name: str,
                     model_dir: Path) -> dict:
    tables = _parse_tables(model_dir)
    rels = _parse_relationships(model_dir)
    elements = []
    for tbl in tables:
        elements.append({
            "id": str(uuid.uuid4()),
            "is_selected": True,
            "display_name": tbl["name"],
            "type": "semantic_model.table",
            "description": None,
            "children": [
                {
                    "id": str(uuid.uuid4()),
                    "is_selected": True,
                    "display_name": col["name"],
                    "type": "semantic_model.column",
                    "data_type": col["data_type"],
                    "description": None,
                    "children": [],
                }
                for col in tbl["columns"]
            ],
        })
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/dataAgent/definition/dataSource/1.0.0/schema.json",
        "artifactId": artifact_id,
        "workspaceId": workspace_id,
        "dataSourceInstructions": None,
        "displayName": display_name,
        "type": "semantic_model",
        "userDescription": None,
        "metadata": {"csdl_relationships": json.dumps(rels, separators=(",", ":"))},
        "elements": elements,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace-id", required=True)
    ap.add_argument("--data-agent-id", required=True)
    ap.add_argument("--artifact-id", required=True, help="semantic model dataset id")
    ap.add_argument("--display-name", required=True, help="source display name, e.g. external-signals")
    ap.add_argument("--source-key", required=True, help="folder key, e.g. semantic-model-external-signals")
    ap.add_argument("--model-dir", required=True, type=Path, help="path to *.SemanticModel dir")
    ap.add_argument("--instruction", default=None, help="instruction line appended to aiInstructions")
    ap.add_argument("--backup", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="write assembled parts JSON (dry-run)")
    ap.add_argument("--apply", action="store_true", help="call updateDefinition (governed)")
    args = ap.parse_args()

    token = _token()

    # 1. Fetch + back up current definition.
    print("Fetching current definition ...", flush=True)
    resp = _req("POST", f"{API}/workspaces/{args.workspace_id}/items/{args.data_agent_id}/getDefinition", token)
    definition = _poll_lro(resp, token)["definition"]
    args.backup.write_text(json.dumps({"definition": definition}, indent=2), encoding="utf-8")
    print(f"Backup written: {args.backup}")

    parts = {p["path"]: p for p in definition["parts"]}
    src_folder = args.source_key
    draft_path = f"Files/Config/draft/{src_folder}/datasource.json"
    pub_path = f"Files/Config/published/{src_folder}/datasource.json"
    if draft_path in parts:
        print(f"NOTE: {draft_path} already exists - will overwrite", flush=True)

    # 2. Build the datasource part.
    ds = build_datasource(args.artifact_id, args.workspace_id, args.display_name, args.model_dir)
    n_tables = len(ds["elements"])
    n_cols = sum(len(t["children"]) for t in ds["elements"])
    n_rels = len(json.loads(ds["metadata"]["csdl_relationships"]))
    print(f"Built datasource: {n_tables} tables, {n_cols} columns, {n_rels} relationships")
    ds_b64 = _b64(json.dumps(ds, indent=2))
    parts[draft_path] = {"path": draft_path, "payload": ds_b64, "payloadType": "InlineBase64"}
    parts[pub_path] = {"path": pub_path, "payload": ds_b64, "payloadType": "InlineBase64"}

    # 3. Append instruction line to draft + published stage_config.
    if args.instruction:
        for scp in ("Files/Config/draft/stage_config.json", "Files/Config/published/stage_config.json"):
            cfg = json.loads(_decode(parts[scp]))
            if args.instruction.strip() not in cfg.get("aiInstructions", ""):
                cfg["aiInstructions"] = cfg.get("aiInstructions", "").rstrip() + "\n\n" + args.instruction.strip()
            parts[scp] = {"path": scp, "payload": _b64(json.dumps(cfg, indent=2)), "payloadType": "InlineBase64"}
            print(f"Updated aiInstructions in {scp}")

    new_parts = list(parts.values())
    print(f"Assembled {len(new_parts)} parts (was {len(definition['parts'])})")

    if args.out:
        args.out.write_text(json.dumps({"parts": [p["path"] for p in new_parts]}, indent=2), encoding="utf-8")
        print(f"Part manifest written: {args.out}")

    if not args.apply:
        print("\nDRY-RUN: no updateDefinition call made. Re-run with --apply after approval.")
        return 0

    # 4. updateDefinition (governed apply).
    body = {"definition": {"parts": new_parts}}
    print("\nCalling updateDefinition (transactional) ...", flush=True)
    resp = _req("POST",
                f"{API}/workspaces/{args.workspace_id}/items/{args.data_agent_id}/updateDefinition?updateMetadata=false",
                token, body)
    if resp.status in (200, 201):
        print("updateDefinition: applied synchronously (200/201)")
    else:
        _poll_lro(resp, token)
        print("updateDefinition: applied via LRO")
    print("DONE. Verify grounding with a probe query.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        sys.exit(2)
