#!/usr/bin/env python3
"""List a lakehouse's ``gold`` schema tables via the OneLake DFS API.

Writes one table name per line to stdout (or ``--out``), for feeding into
``verify_gold_schema.py --produced``. Schemas-enabled lakehouses store tables
at ``Tables/<schema>/<table>``; this lists ``Tables/gold``.

Coordinates come from ``data-platform/fabric/environments.yml``. ``requests`` is
imported lazily so the pure parse helper imports without the package installed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"
ONELAKE_DFS = "https://onelake.dfs.fabric.microsoft.com"


def parse_table_names(paths_json: dict) -> list[str]:
    """Extract the leaf table names from a DFS filesystem list response.

    Each ``paths`` entry ``name`` is like ``<lh>/Tables/gold/<table>``; the
    table name is the final path segment. Directories only.
    """
    names = []
    for entry in paths_json.get("paths", []):
        if entry.get("isDirectory") in (True, "true"):
            names.append(entry["name"].rstrip("/").rsplit("/", 1)[-1])
    return sorted(set(names))


def load_env(environment: str) -> dict:
    envs = yaml.safe_load(ENV_FILE.read_text(encoding="utf-8"))["environments"]
    if environment not in envs:
        raise SystemExit(f"unknown environment '{environment}'")
    return envs[environment]


def get_token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource",
         "https://storage.azure.com/", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def list_gold(workspace_id: str, lakehouse_id: str, schema: str,
              token: str) -> list[str]:
    import requests
    url = (f"{ONELAKE_DFS}/{workspace_id}?resource=filesystem&recursive=false"
           f"&directory={lakehouse_id}/Tables/{schema}")
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return parse_table_names(r.json())


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", required=True, choices=["SIT", "PROD"])
    p.add_argument("--schema", default="gold")
    p.add_argument("--out", default=None)
    return p.parse_args(argv)


def main(argv=None) -> int:
    ns = parse_args(argv)
    env = load_env(ns.environment)
    names = list_gold(env["workspace_id"], env["lakehouse_id"], ns.schema,
                      get_token())
    text = "\n".join(names) + ("\n" if names else "")
    if ns.out:
        Path(ns.out).write_text(text, encoding="utf-8")
        print(f"Wrote {len(names)} {ns.schema} table name(s) to {ns.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
