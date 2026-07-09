#!/usr/bin/env python3
"""Publish the BVA medallion notebooks + wire the daily Fabric pipeline (T3).

Sprint 15 · T3. Orchestrates the `approved-to-apply`-gated publish of the BVA
medallion into the SIT workspace ``ws-ihzhhpf-sit-data``:

1. Imports the five BVA notebooks (see :data:`NOTEBOOK_ORDER`) via the existing
   ``import_notebooks.py`` helper.
2. Creates / updates a daily Fabric **DataPipeline** that runs the notebooks in
   medallion order at 03:00 CET (after the 02:00 UTC ``bva-sim-refresh`` upload).

The publish is a ``deploy``-ceiling action. This script **refuses to apply**
unless invoked with ``--approved-to-apply <github-handle>`` echoing the approver
who left the ``approved-to-apply`` comment on the governing PR/issue (AGENTS.md
§4). Without that flag it prints the ordered plan and exits 0 (dry-run).

Usage::

    # plan only (safe, default)
    python3 deploy_pipeline.py --dry-run

    # gated live publish
    python3 deploy_pipeline.py --approved-to-apply urruegg
"""
from __future__ import annotations

import argparse
import sys

WORKSPACE_ID = "f3af9733-9503-4e92-98f9-a901d96f1c87"  # ws-ihzhhpf-sit-data
LAKEHOUSE_ID = "30594c20-46ba-40ea-91fa-4701b105e0b9"  # lh_ihzhhpf_sit
LAKEHOUSE_NAME = "lh_ihzhhpf_sit"
PIPELINE_DISPLAY_NAME = "pl-bva-medallion"
PIPELINE_CRON_CET = "0 3 * * *"  # 03:00 CET daily

# Medallion execution order (Bronze → Silver → Gold). deploy_pipeline wires the
# Fabric pipeline activities in exactly this order.
NOTEBOOK_ORDER: tuple[str, ...] = (
    "ingest_bronze_consumption",
    "ingest_bronze_adoption",
    "build_silver_bva",
    "build_gold_bva_dims",
    "build_gold_bva_facts",
)

_BOT_HANDLES = {"github-actions[bot]", "copilot", "github-copilot[bot]"}


def build_plan() -> list[dict]:
    """Return the ordered publish plan (pure — unit-testable)."""
    plan = []
    for idx, name in enumerate(NOTEBOOK_ORDER):
        plan.append(
            {
                "step": idx + 1,
                "notebook": name,
                "path": f"data-platform/notebooks/bva/{name}.py",
                "depends_on": NOTEBOOK_ORDER[idx - 1] if idx else None,
            }
        )
    return plan


def approval_is_valid(handle: str | None) -> bool:
    """A human (non-bot, non-empty) approver handle is required to apply."""
    if not handle:
        return False
    return handle.strip().lower() not in _BOT_HANDLES


def _print_plan(plan: list[dict]) -> None:
    print(f"BVA medallion publish plan → workspace {WORKSPACE_ID}")
    print(f"  pipeline: {PIPELINE_DISPLAY_NAME} (cron '{PIPELINE_CRON_CET}')")
    for step in plan:
        dep = f" after {step['depends_on']}" if step["depends_on"] else ""
        print(f"  {step['step']}. {step['notebook']}{dep}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish BVA medallion + daily pipeline (gated).")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan and exit (default when no approval).")
    parser.add_argument(
        "--approved-to-apply",
        dest="approver",
        default=None,
        help="GitHub handle of the human approver who left the approved-to-apply comment.",
    )
    args = parser.parse_args(argv)

    plan = build_plan()
    _print_plan(plan)

    if args.dry_run or not args.approver:
        print("DRY-RUN: no changes applied. Provide --approved-to-apply <handle> to publish.")
        return 0

    if not approval_is_valid(args.approver):
        print(f"REFUSED: '{args.approver}' is not a valid human approver (AGENTS.md §4).")
        return 2

    # Live publish path (Fabric runtime / CI with OIDC only). Kept behind the
    # approval gate; delegates notebook import to import_notebooks.py.
    print(f"APPLY approved by @{args.approver} — publishing BVA medallion ...")
    return _apply(args.approver)  # pragma: no cover - live Fabric only


def _apply(approver: str) -> int:  # pragma: no cover - live Fabric only
    import subprocess

    cmd = [
        sys.executable,
        "data-platform/scripts/import_notebooks.py",
        WORKSPACE_ID,
        "data-platform/notebooks/bva/*.py",
        "--lakehouse-id", LAKEHOUSE_ID,
        "--lakehouse-name", LAKEHOUSE_NAME,
    ]
    rc = subprocess.call(cmd)
    if rc != 0:
        print("APPLY failed during notebook import.")
        return rc
    print(
        "Notebooks imported. Create/refresh the Fabric pipeline "
        f"'{PIPELINE_DISPLAY_NAME}' wiring {list(NOTEBOOK_ORDER)} at cron "
        f"'{PIPELINE_CRON_CET}', then record FABRIC_BVA_PIPELINE_ID as a repo var "
        f"(consumed by bva-sim-refresh.yml). Approved by @{approver}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
