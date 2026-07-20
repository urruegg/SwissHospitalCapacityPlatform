#!/usr/bin/env python3
"""Reproducibly (re)build the operational medallion in a Fabric workspace.

For a chosen ``--environment`` this:

1. create-or-updates each modernized master-data + eventstream notebook in the
   target workspace from its canonical git ``.ipynb`` (Fabric REST
   ``createNotebook`` / ``updateDefinition``), and
2. runs them in dependency order, injecting the target lakehouse as the
   **default lakehouse at run time** (the git notebooks carry no lakehouse
   binding, so the same source runs against SIT or PROD by env only), and
3. polls each on-demand run to a terminal state.

Coordinates come from ``data-platform/fabric/environments.yml`` (SIT/PROD
workspace + lakehouse GUIDs — deployment coordinates, not secrets).

Plan-first: with no ``--apply`` the script only prints the ordered plan and the
create-vs-update decision per notebook (a live read of the workspace notebook
list). Live writes (create/update/run) require ``--apply`` **and** the
``approved-to-apply`` deploy gate per AGENTS.md §4.

``requests`` is imported lazily so the network-free parts (payload building,
ordering, arg-parse) import without the package installed.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"
FABRIC_API = "https://api.fabric.microsoft.com/v1"
NOTEBOOKS_ROOT = REPO_ROOT / "data-platform" / "notebooks"
POLL_SECONDS = 15
POLL_TIMEOUT = 60 * 30  # 30 minutes per notebook run


@dataclass(frozen=True)
class Notebook:
    display_name: str
    path: Path


# Dependency order: bronze -> silver -> gold master data -> OR samples ->
# gold eventstream (reads the same schemas-enabled lakehouse).
_ORDER = [
    ("01_bronze_master_data", "reference/01_bronze_master_data.ipynb"),
    ("02_silver_master_data", "reference/02_silver_master_data.ipynb"),
    ("03_gold_master_data", "reference/03_gold_master_data.ipynb"),
    ("04_load_or_samples", "reference/04_load_or_samples.ipynb"),
    ("03_gold_eventstream", "eventstream/03_gold_eventstream.ipynb"),
]


def ordered_notebooks() -> list[Notebook]:
    return [Notebook(name, NOTEBOOKS_ROOT / rel) for name, rel in _ORDER]


# --------------------------------------------------------------------------- #
# Pure payload builders (network-free, unit-tested)                           #
# --------------------------------------------------------------------------- #
def ipynb_to_base64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def inject_lakehouse(raw: bytes, lakehouse_id: str, lakehouse_name: str,
                     workspace_id: str) -> bytes:
    """Bind the target lakehouse as the notebook's default lakehouse.

    The canonical git ``.ipynb`` carries no lakehouse binding (env-agnostic);
    Fabric needs ``metadata.dependencies.lakehouse`` so ``saveAsTable`` and
    ``CREATE SCHEMA`` resolve against the right schemas-enabled lakehouse. This
    makes the same source bind to SIT or PROD by ``--environment`` only.
    """
    nb = json.loads(raw.decode("utf-8"))
    nb.setdefault("metadata", {})["dependencies"] = {
        "lakehouse": {
            "default_lakehouse": lakehouse_id,
            "default_lakehouse_name": lakehouse_name,
            "default_lakehouse_workspace_id": workspace_id,
        }
    }
    return json.dumps(nb, ensure_ascii=False, indent=1).encode("utf-8")


def build_platform_part(display_name: str, source_rel: str) -> str:
    return json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/"
                   "gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "Notebook",
            "displayName": display_name,
            "description": f"Imported from {source_rel}",
        },
        "config": {
            "version": "2.0",
            "logicalId": "00000000-0000-0000-0000-000000000000",
        },
    }, indent=2)


def build_definition(ipynb_b64: str, platform_b64: str) -> dict:
    return {
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": ipynb_b64,
                    "payloadType": "InlineBase64",
                },
                {
                    "path": ".platform",
                    "payload": platform_b64,
                    "payloadType": "InlineBase64",
                },
            ],
        }
    }


def build_create_body(display_name: str, ipynb_b64: str,
                      platform_b64: str) -> dict:
    body = {"displayName": display_name}
    body.update(build_definition(ipynb_b64, platform_b64))
    return body


def build_run_config(lakehouse_name: str, lakehouse_id: str,
                     workspace_id: str) -> dict:
    return {
        "executionData": {
            "configuration": {
                "defaultLakehouse": {
                    "name": lakehouse_name,
                    "id": lakehouse_id,
                    "workspaceId": workspace_id,
                }
            }
        }
    }


def load_env(environment: str) -> dict:
    envs = yaml.safe_load(ENV_FILE.read_text(encoding="utf-8"))["environments"]
    if environment not in envs:
        raise SystemExit(f"unknown environment '{environment}'; "
                         f"known: {', '.join(sorted(envs))}")
    return envs[environment]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", required=True, choices=["SIT", "PROD"])
    p.add_argument("--apply", action="store_true",
                   help="Perform live create/update/run calls. Requires the "
                        "approved-to-apply deploy gate. Omit for a plan-only "
                        "dry run.")
    p.add_argument("--only", default=None,
                   help="Run a single notebook by display name (debug).")
    return p.parse_args(argv)


# --------------------------------------------------------------------------- #
# Live Fabric REST (deploy-class; only reached with --apply)                  #
# --------------------------------------------------------------------------- #
def get_token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource",
         "https://api.fabric.microsoft.com", "--query", "accessToken",
         "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json"}


def list_notebooks(workspace_id: str, token: str) -> dict[str, str]:
    import requests
    r = requests.get(f"{FABRIC_API}/workspaces/{workspace_id}/notebooks",
                     headers=_headers(token))
    r.raise_for_status()
    return {n["displayName"]: n["id"] for n in r.json().get("value", [])}


def _wait_lro(response, token: str) -> None:
    """Poll a Fabric long-running-operation until it succeeds."""
    import requests
    if response.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    if response.status_code != 202:
        return
    location = response.headers.get("Location")
    if not location:
        return
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        time.sleep(POLL_SECONDS)
        s = requests.get(location, headers=_headers(token))
        s.raise_for_status()
        status = s.json().get("status")
        # Item-definition LROs report "Succeeded"; on-demand job instances
        # report "Completed" (and "Deduped" when a matching run already ran).
        if status in ("Succeeded", "Completed", "Deduped"):
            return
        if status in ("Failed", "Cancelled"):
            raise RuntimeError(f"LRO {status}: {s.text}")
    raise TimeoutError("LRO did not complete within timeout")


def create_or_update(env: dict, existing: dict[str, str],
                     nb: Notebook, token: str) -> str:
    import requests
    workspace_id = env["workspace_id"]
    source_rel = nb.path.relative_to(REPO_ROOT).as_posix()
    bound = inject_lakehouse(nb.path.read_bytes(), env["lakehouse_id"],
                             env["lakehouse_name"], workspace_id)
    ipynb_b64 = ipynb_to_base64(bound)
    platform_b64 = ipynb_to_base64(
        build_platform_part(nb.display_name, source_rel).encode("utf-8"))
    if nb.display_name in existing:
        item_id = existing[nb.display_name]
        r = requests.post(
            f"{FABRIC_API}/workspaces/{workspace_id}/notebooks/{item_id}/"
            "updateDefinition?updateMetadata=true",
            headers=_headers(token),
            json=build_definition(ipynb_b64, platform_b64))
        _wait_lro(r, token)
        return item_id
    r = requests.post(
        f"{FABRIC_API}/workspaces/{workspace_id}/notebooks",
        headers=_headers(token),
        json=build_create_body(nb.display_name, ipynb_b64, platform_b64))
    _wait_lro(r, token)
    if r.status_code == 201:
        return r.json()["id"]
    return list_notebooks(workspace_id, token)[nb.display_name]


def run_notebook(workspace_id: str, item_id: str, run_config: dict,
                 token: str) -> None:
    import requests
    r = requests.post(
        f"{FABRIC_API}/workspaces/{workspace_id}/items/{item_id}/jobs/"
        "instances?jobType=RunNotebook",
        headers=_headers(token), json=run_config)
    _wait_lro(r, token)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    env = load_env(ns.environment)
    notebooks = ordered_notebooks()
    if ns.only:
        notebooks = [n for n in notebooks if n.display_name == ns.only]
        if not notebooks:
            raise SystemExit(f"no notebook named '{ns.only}'")

    print(f"Environment : {ns.environment}")
    print(f"Workspace   : {env['workspace_name']} ({env['workspace_id']})")
    print(f"Lakehouse   : {env['lakehouse_name']} ({env['lakehouse_id']})")
    print(f"Mode        : {'APPLY (live)' if ns.apply else 'PLAN (dry-run)'}")
    print("Order       :")
    for i, nb in enumerate(notebooks, 1):
        print(f"  {i}. {nb.display_name}")

    if not ns.apply:
        print("\nPlan only. Re-run with --apply (approved-to-apply gate) to "
              "create/update and run.")
        return 0

    token = get_token()
    existing = list_notebooks(env["workspace_id"], token)
    run_config = build_run_config(env["lakehouse_name"], env["lakehouse_id"],
                                  env["workspace_id"])
    for nb in notebooks:
        action = "update" if nb.display_name in existing else "create"
        print(f"\n[{action}] {nb.display_name} ...", flush=True)
        item_id = create_or_update(env, existing, nb, token)
        print(f"[run]    {nb.display_name} ({item_id}) ...", flush=True)
        run_notebook(env["workspace_id"], item_id, run_config, token)
        print(f"[ok]     {nb.display_name}", flush=True)
    print("\nMedallion rebuild complete.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
