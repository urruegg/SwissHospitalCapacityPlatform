#!/usr/bin/env python3
"""Sprint 42 ST-2b: grant the PO Agent runtime MI a Fabric workspace role.

Fabric workspace role assignments are a Fabric REST API concept
(``POST /v1/workspaces/{id}/roleAssignments``), not an ARM resource — this is
why the fix is a script, not Bicep. Idempotent: checks the existing role
assignments first and skips the POST if the principal already has any role.
Read-only grant by default (``Viewer``), matching Class D's read-only design
(the Data Agent enforces RLS + the PHI gate; this grant only lets the caller
reach it at all).

Auth: ``az account get-access-token --resource https://api.fabric.microsoft.com``
(same pattern as ``add_data_agent_source.py``). Run ``az login`` first.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request

FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
API = "https://api.fabric.microsoft.com/v1"


def _token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource", FABRIC_RESOURCE,
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def _http_get(method: str, url: str, token: str):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req)


def _http_post(method: str, url: str, token: str, body: dict | None = None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req)


def ensure_role_assignment(
    workspace_id: str,
    principal_id: str,
    role: str,
    token: str,
    http_get=_http_get,
    http_post=_http_post,
) -> str:
    """Grant `role` to `principal_id` on the Fabric workspace, unless already granted.

    Returns "already-granted" or "granted".
    """
    list_url = f"{API}/workspaces/{workspace_id}/roleAssignments"
    resp = http_get("GET", list_url, token)
    existing = json.loads(resp.read().decode("utf-8")).get("value", [])
    for assignment in existing:
        if assignment.get("principal", {}).get("id") == principal_id:
            return "already-granted"

    body = {"principal": {"id": principal_id, "type": "ServicePrincipal"}, "role": role}
    http_post("POST", list_url, token, body=body)
    return "granted"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grant a Fabric workspace role to the PO Agent runtime MI.")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--principal-id", required=True, help="objectId of the po-agent runtime MI (Bicep output principalId).")
    parser.add_argument("--role", default="Viewer")
    args = parser.parse_args(argv)

    token = _token()
    result = ensure_role_assignment(args.workspace_id, args.principal_id, args.role, token)
    print(f"grant_po_agent_workspace_role: {result} (workspace={args.workspace_id}, principal={args.principal_id}, role={args.role})")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
