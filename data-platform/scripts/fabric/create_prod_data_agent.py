#!/usr/bin/env python3
"""Create a Fabric Data Agent in a target workspace by cloning a source agent.

Clones an existing (source, e.g. SIT) Data Agent definition into a new agent in
a target (e.g. PROD) workspace via the Fabric Data Agent REST API
(``POST /v1/workspaces/{ws}/dataAgents``). The clone:

* drops any datasource folders named by ``--drop-source-key`` (e.g. the
  ontology source, when the target workspace has no ontology yet);
* rewrites every remaining datasource ``workspaceId`` to ``--target-workspace-id``;
* rewrites datasource ``artifactId`` per ``--guid-map OLD=NEW`` pairs (map each
  source semantic-model GUID to its target-workspace equivalent);
* replaces the ``aiInstructions`` (draft + published stage_config) from
  ``--instructions-file`` and the ``publish_info`` description from
  ``--description-file`` so the target agent does not over-promise grounding it
  cannot serve (e.g. ontology / forecast) yet;
* resets the ``.platform`` logicalId and sets the new ``displayName``.

Because the source datasource ``elements`` + ``csdl_relationships`` are curated
(the portal-selected table/column set) and the target semantic models are
parity copies of the source, cloning is more faithful than re-deriving the
element list from TMDL.

Governed action (AGENTS.md Section 4): ``--dry-run`` (default) assembles + writes
the definition without creating anything; run ``--apply`` only after an
``approved-to-apply`` comment on the governing issue. The created agent's
coordinates (workspaceId / dataAgentId / consumption endpoint) are printed for
wiring into ``infra/environments/prod-swn.bicepparam``.

Auth: ``az account get-access-token`` for the Fabric resource; run ``az login``
first with an identity that is Contributor on the target workspace.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
API = "https://api.fabric.microsoft.com/v1"


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
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}
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


def _fetch_definition(ws: str, item_id: str, token: str) -> dict:
    resp = _req("POST", f"{API}/workspaces/{ws}/items/{item_id}/getDefinition", token)
    return _poll_lro(resp, token)["definition"]


def transform(definition: dict, *, target_ws: str, display_name: str,
              guid_map: dict[str, str], drop_keys: list[str],
              instructions: str, description: str) -> dict:
    parts = {p["path"]: p for p in definition["parts"]}
    out: dict[str, dict] = {}

    for path, part in parts.items():
        # Drop datasource folders we are not carrying over (e.g. ontology).
        if any(f"/{k}/" in path for k in drop_keys):
            continue

        if path.endswith("datasource.json"):
            ds = json.loads(_decode(part))
            ds["workspaceId"] = target_ws
            if ds.get("artifactId") in guid_map:
                ds["artifactId"] = guid_map[ds["artifactId"]]
            out[path] = {"path": path, "payload": _b64(json.dumps(ds, indent=2)),
                         "payloadType": "InlineBase64"}
        elif path.endswith("stage_config.json"):
            cfg = json.loads(_decode(part))
            cfg["aiInstructions"] = instructions
            out[path] = {"path": path, "payload": _b64(json.dumps(cfg, indent=2)),
                         "payloadType": "InlineBase64"}
        elif path.endswith("publish_info.json"):
            info = json.loads(_decode(part))
            info["description"] = description
            out[path] = {"path": path, "payload": _b64(json.dumps(info, indent=2)),
                         "payloadType": "InlineBase64"}
        elif path == ".platform":
            plat = json.loads(_decode(part))
            plat.setdefault("metadata", {})["type"] = "DataAgent"
            plat["metadata"]["displayName"] = display_name
            plat.setdefault("config", {})["logicalId"] = "00000000-0000-0000-0000-000000000000"
            out[path] = {"path": path, "payload": _b64(json.dumps(plat, indent=2)),
                         "payloadType": "InlineBase64"}
        else:
            out[path] = part

    return {"parts": list(out.values())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-workspace-id", required=True)
    ap.add_argument("--source-data-agent-id", required=True)
    ap.add_argument("--target-workspace-id", required=True)
    ap.add_argument("--display-name", required=True)
    ap.add_argument("--guid-map", action="append", default=[],
                    metavar="OLD=NEW", help="source->target semantic-model GUID (repeatable)")
    ap.add_argument("--drop-source-key", action="append", default=[],
                    metavar="KEY", help="datasource folder key to drop, e.g. ontology-ont_hospital_capacity")
    ap.add_argument("--instructions-file", required=True, type=Path)
    ap.add_argument("--description-file", required=True, type=Path)
    ap.add_argument("--backup", required=True, type=Path, help="write the source definition here")
    ap.add_argument("--out", type=Path, help="write assembled target definition (dry-run)")
    ap.add_argument("--apply", action="store_true", help="POST /dataAgents to create (governed)")
    args = ap.parse_args()

    guid_map = dict(kv.split("=", 1) for kv in args.guid_map)
    instructions = args.instructions_file.read_text(encoding="utf-8").strip()
    description = args.description_file.read_text(encoding="utf-8").strip()

    token = _token()

    print("Fetching source definition ...", flush=True)
    src_def = _fetch_definition(args.source_workspace_id, args.source_data_agent_id, token)
    args.backup.write_text(json.dumps({"definition": src_def}, indent=2), encoding="utf-8")
    print(f"Source backup written: {args.backup} ({len(src_def['parts'])} parts)")

    new_def = transform(
        src_def, target_ws=args.target_workspace_id, display_name=args.display_name,
        guid_map=guid_map, drop_keys=args.drop_source_key,
        instructions=instructions, description=description,
    )
    ds_paths = [p["path"] for p in new_def["parts"] if p["path"].endswith("datasource.json")]
    print(f"Assembled target definition: {len(new_def['parts'])} parts")
    print("Datasource parts:")
    for p in sorted(ds_paths):
        print(f"  - {p}")

    if args.out:
        args.out.write_text(json.dumps(new_def, indent=2), encoding="utf-8")
        print(f"Target definition written: {args.out}")

    if not args.apply:
        print("\nDRY-RUN: no dataAgent created. Re-run with --apply after approval.")
        return 0

    body = {"displayName": args.display_name, "description": description,
            "definition": new_def}
    print("\nCreating Data Agent (POST /dataAgents) ...", flush=True)
    resp = _req("POST", f"{API}/workspaces/{args.target_workspace_id}/dataAgents", token, body)
    if resp.status in (200, 201):
        created = json.loads(resp.read().decode())
    else:
        created = _poll_lro(resp, token)
    da_id = created.get("id") or created.get("objectId")
    print("\nCREATED Data Agent:")
    print(f"  displayName          = {args.display_name}")
    print(f"  workspaceId          = {args.target_workspace_id}")
    print(f"  dataAgentId          = {da_id}")
    print(f"  consumption endpoint = {API}/workspaces/{args.target_workspace_id}"
          f"/aiskills/{da_id}/aiassistant/openai")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        sys.exit(2)
