#!/usr/bin/env python3
"""Create-or-update and run ONE Fabric notebook by path (plan-first, gated).

A thin driver over the pure REST builders in ``run_medallion.py`` for the case
where a single self-contained notebook (e.g. an evidence notebook) must be
imported into a workspace and executed, outside the fixed medallion order.

The target lakehouse from ``environments.yml`` is injected as the notebook's
default lakehouse at run time, so the same source runs against SIT or PROD by
``--environment`` only.

Plan-first: without ``--apply`` this prints the plan only. Live create/update/run
requires ``--apply`` **and** the ``approved-to-apply`` deploy gate (AGENTS.md §4).

Usage::

    python data-platform/scripts/fabric/run_single_notebook.py \\
        --environment SIT \\
        --notebook data-platform/notebooks/foresight/run_foresight_evidence.ipynb \\
        --display-name run_foresight_evidence --apply
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_RM_PATH = REPO_ROOT / "data-platform" / "scripts" / "fabric" / "run_medallion.py"


def _load_run_medallion():
    import sys
    spec = importlib.util.spec_from_file_location("run_medallion", _RM_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_medallion"] = mod
    spec.loader.exec_module(mod)
    return mod


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", required=True, choices=["SIT", "PROD"])
    p.add_argument("--notebook", required=True,
                   help="Repo-relative or absolute path to the .ipynb.")
    p.add_argument("--display-name", required=True,
                   help="Workspace display name for the notebook item.")
    p.add_argument("--apply", action="store_true",
                   help="Perform live create/update/run. Requires the "
                        "approved-to-apply deploy gate. Omit for a dry run.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    ns = parse_args(argv)
    rm = _load_run_medallion()
    env = rm.load_env(ns.environment)

    nb_path = Path(ns.notebook)
    if not nb_path.is_absolute():
        nb_path = REPO_ROOT / nb_path
    if not nb_path.is_file():
        raise SystemExit(f"notebook not found: {nb_path}")

    nb = rm.Notebook(ns.display_name, nb_path)

    print(f"Environment : {ns.environment}")
    print(f"Workspace   : {env['workspace_name']} ({env['workspace_id']})")
    print(f"Lakehouse   : {env['lakehouse_name']} ({env['lakehouse_id']})")
    print(f"Notebook    : {ns.display_name}  <- {nb_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"Mode        : {'APPLY (live)' if ns.apply else 'PLAN (dry-run)'}")

    if not ns.apply:
        print("\nPlan only. Re-run with --apply (approved-to-apply gate) to "
              "create/update and run.")
        return 0

    token = rm.get_token()
    existing = rm.list_notebooks(env["workspace_id"], token)
    action = "update" if nb.display_name in existing else "create"
    print(f"\n[{action}] {nb.display_name} ...", flush=True)
    item_id = rm.create_or_update(env, existing, nb, token)
    run_config = rm.build_run_config(env["lakehouse_name"], env["lakehouse_id"],
                                     env["workspace_id"])
    print(f"[run]    {nb.display_name} ({item_id}) ...", flush=True)
    rm.run_notebook(env["workspace_id"], item_id, run_config, token)
    print(f"[ok]     {nb.display_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
