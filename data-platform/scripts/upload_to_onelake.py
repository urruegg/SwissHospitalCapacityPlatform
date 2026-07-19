"""Upload local files to a OneLake Files/ folder in a target lakehouse.

Environment-parameterized: workspace and lakehouse IDs are explicit arguments so
SIT and PROD load identically. IDs come from data-platform/fabric/environments.yml.

Usage:
    python upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> \
        --source-root data/master-data/capacity --target master-data/capacity
    python upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> \
        --source data/synthetic/or-samples/*.json --target or-samples
"""
from __future__ import annotations

import argparse
import glob
import subprocess
import sys
from pathlib import Path

import requests

ONELAKE_HOST = "https://onelake.dfs.fabric.microsoft.com"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload files to a OneLake Files/ folder.")
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--lakehouse-id", required=True)
    p.add_argument("--target", required=True, help="Remote Files/<target>/ folder")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--source-root", help="Upload every *.csv under this folder")
    src.add_argument("--source", help="Glob of specific files to upload")
    return p.parse_args(argv)


def get_token() -> str:
    out = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://storage.azure.com/", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    )
    return out.strip()


def upload_file(local_path: Path, workspace_id: str, lakehouse_id: str,
                remote_folder: str, token: str) -> None:
    remote_name = local_path.name
    base = f"{ONELAKE_HOST}/{workspace_id}/{lakehouse_id}/Files/{remote_folder}/{remote_name}"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.put(f"{base}?resource=file", headers=headers)
    if r.status_code not in (201, 200):
        raise RuntimeError(f"Create failed for {remote_name}: {r.status_code} {r.text}")

    content = local_path.read_bytes()
    length = len(content)
    if length > 0:
        r = requests.patch(
            f"{base}?action=append&position=0",
            headers={**headers, "Content-Length": str(length),
                     "Content-Type": "application/octet-stream"},
            data=content,
        )
        if r.status_code not in (200, 202):
            raise RuntimeError(f"Append failed for {remote_name}: {r.status_code} {r.text}")

    r = requests.patch(f"{base}?action=flush&position={length}", headers=headers)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Flush failed for {remote_name}: {r.status_code} {r.text}")

    print(f"  uploaded {remote_name} ({length} bytes) -> Files/{remote_folder}/")


def resolve_paths(ns: argparse.Namespace) -> list[Path]:
    if ns.source_root:
        return sorted(p for p in Path(ns.source_root).glob("*.csv") if p.is_file())
    return [Path(p) for p in glob.glob(ns.source) if Path(p).is_file()]


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv if argv is not None else sys.argv[1:])
    paths = resolve_paths(ns)
    if not paths:
        print("No files matched.")
        return 1
    token = get_token()
    print(f"Uploading {len(paths)} file(s) to Files/{ns.target}/ in {ns.lakehouse_id} ...")
    for p in paths:
        upload_file(p, ns.workspace_id, ns.lakehouse_id, ns.target, token)
    print(f"Done. {len(paths)} files uploaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
