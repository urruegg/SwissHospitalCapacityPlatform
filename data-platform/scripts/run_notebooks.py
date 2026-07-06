"""Trigger Fabric notebook runs sequentially and wait for completion.

Usage:
    python run_notebooks.py <workspace-id> <notebook-name-1> [<notebook-name-2> ...]

Example:
    python run_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 \
        01_bronze_master_data 02_silver_master_data 03_gold_master_data
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
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
    r = requests.get(f"{FABRIC_API}/workspaces/{workspace_id}/notebooks",
                     headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return {item["displayName"]: item["id"] for item in r.json().get("value", [])}


def trigger_run(workspace_id: str, notebook_id: str, token: str) -> str:
    """Trigger a notebook run; return the job-instance URL."""
    url = (f"{FABRIC_API}/workspaces/{workspace_id}/items/{notebook_id}"
           f"/jobs/instances?jobType=RunNotebook")
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Trigger failed {r.status_code}: {r.text}")
    loc = r.headers.get("Location") or r.headers.get("location")
    if not loc:
        raise RuntimeError(f"No Location header: {r.headers}")
    return loc


def wait_for_completion(job_url: str, token: str, timeout_min: int = 30, poll_sec: int = 15) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    last_status = None
    while time.time() - start < timeout_min * 60:
        r = requests.get(job_url, headers=headers)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "").lower()
        if status != last_status:
            elapsed = int(time.time() - start)
            print(f"    [{elapsed:>4}s] status={status}")
            last_status = status
        if status in ("completed", "succeeded"):
            return data
        if status in ("failed", "cancelled", "deduped"):
            return data
        time.sleep(poll_sec)
    raise TimeoutError(f"Notebook did not complete within {timeout_min}min")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fabric notebooks sequentially")
    parser.add_argument("workspace_id")
    parser.add_argument("notebook_names", nargs="+", help="Display names, in run order")
    parser.add_argument("--timeout-min", type=int, default=30)
    parser.add_argument("--continue-on-failure", action="store_true")
    args = parser.parse_args()

    token = get_token()
    all_notebooks = list_notebooks(args.workspace_id, token)

    missing = [n for n in args.notebook_names if n not in all_notebooks]
    if missing:
        print(f"ERROR: notebooks not found in workspace: {missing}")
        print(f"Available: {list(all_notebooks)}")
        return 1

    for name in args.notebook_names:
        nb_id = all_notebooks[name]
        print(f"\n>>> {name} (id={nb_id})")
        job_url = trigger_run(args.workspace_id, nb_id, token)
        result = wait_for_completion(job_url, token, timeout_min=args.timeout_min)
        status = result.get("status", "").lower()
        if status in ("failed", "cancelled"):
            failure = result.get("failureReason") or result.get("error") or result
            print(f"    FAILED: {failure}")
            if not args.continue_on_failure:
                return 2
        else:
            print(f"    OK: {status}")

    print("\nAll notebooks completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
