"""Upload local files to OneLake Files/ folder in the SIT lakehouse.

Usage:
    python upload_to_onelake.py <local-file-or-glob> <remote-folder>

Examples:
    python upload_to_onelake.py "docs/reviews/2026-06-29-ama-capacity-metadata-review/*.csv" master-data
    python upload_to_onelake.py "data/synthetic/or-samples/*.json" or-samples
"""
from __future__ import annotations

import glob
import subprocess
import sys
from pathlib import Path

import requests

WORKSPACE_ID = "f3af9733-9503-4e92-98f9-a901d96f1c87"
LAKEHOUSE_ID = "30594c20-46ba-40ea-91fa-4701b105e0b9"
ONELAKE_HOST = "https://onelake.dfs.fabric.microsoft.com"


def get_token() -> str:
    out = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://storage.azure.com/", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    )
    return out.strip()


def upload_file(local_path: Path, remote_folder: str, token: str) -> None:
    remote_name = local_path.name
    base = f"{ONELAKE_HOST}/{WORKSPACE_ID}/{LAKEHOUSE_ID}/Files/{remote_folder}/{remote_name}"
    headers = {"Authorization": f"Bearer {token}"}

    # Create empty file (PUT ?resource=file)
    r = requests.put(f"{base}?resource=file", headers=headers)
    if r.status_code not in (201, 200):
        raise RuntimeError(f"Create failed for {remote_name}: {r.status_code} {r.text}")

    # Append the content (PATCH ?action=append&position=0)
    with open(local_path, "rb") as fh:
        content = fh.read()
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

    # Flush (PATCH ?action=flush&position=<total>)
    r = requests.patch(
        f"{base}?action=flush&position={length}",
        headers=headers,
    )
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Flush failed for {remote_name}: {r.status_code} {r.text}")

    print(f"  uploaded {remote_name} ({length} bytes) -> Files/{remote_folder}/")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    pattern = sys.argv[1]
    remote_folder = sys.argv[2]

    paths = [Path(p) for p in glob.glob(pattern) if Path(p).is_file()]
    if not paths:
        print(f"No files match {pattern}")
        return 1

    token = get_token()
    print(f"Uploading {len(paths)} file(s) to Files/{remote_folder}/ ...")
    for p in paths:
        upload_file(p, remote_folder, token)

    print(f"Done. {len(paths)} files uploaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
