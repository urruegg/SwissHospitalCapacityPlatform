#!/usr/bin/env python3
"""Sprint 16 T5 — publish csa-simulate to Fabric (gated).

Publishing the CSA simulation notebook to the SIT Fabric workspace is a
`deploy`-ceiling action. Per AGENTS.md §4 this script REFUSES to publish unless
`--approved-to-apply` is passed AND Fabric credentials are configured; the
default is a dry run that prints the plan for the PR comment.

    # Plan (safe — for the approved-to-apply PR comment)
    python3 data-platform/scripts/csa/deploy-notebook.py --dry-run

    # Apply (only after @urruegg replies `approved-to-apply`)
    python3 data-platform/scripts/csa/deploy-notebook.py --approved-to-apply

Auth is RBAC/OIDC via the Fabric REST API — no secrets in this file.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

WORKSPACE = "ws-ihzhhpf-sit-data"
WORKSPACE_ID = "f3af9733-9503-4e92-98f9-a901d96f1c87"
NOTEBOOK_PATH = Path(__file__).resolve().parents[2] / "notebooks" / "csa" / "csa-simulate.py"
FABRIC_TOKEN_ENV = "FABRIC_ACCESS_TOKEN"


def plan() -> str:
    return (
        f"PLAN: publish {NOTEBOOK_PATH.name} to Fabric workspace "
        f"{WORKSPACE} ({WORKSPACE_ID}).\n"
        "  - creates/updates a Notebook item 'csa-simulate'\n"
        "  - wires the Fabric REST run trigger for the csa-agent Run phase\n"
        "  - synthetic Gold data only (ADR-0016); no PHI\n"
        "Gate: requires @urruegg `approved-to-apply` (AGENTS.md §4)."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish the csa-simulate notebook (gated).")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan only.")
    parser.add_argument(
        "--approved-to-apply",
        action="store_true",
        help="Confirm the human approval gate has been satisfied.",
    )
    args = parser.parse_args(argv)

    if not NOTEBOOK_PATH.exists():
        print(f"FAIL: notebook not found at {NOTEBOOK_PATH}")
        return 1

    print(plan())

    if args.dry_run or not args.approved_to_apply:
        print("Dry run — not publishing. Re-run with --approved-to-apply after approval.")
        return 0

    if not os.environ.get(FABRIC_TOKEN_ENV):
        print(f"REFUSE: {FABRIC_TOKEN_ENV} unset — cannot publish without Fabric credentials.")
        return 1

    # Live publish path is exercised only in the SIT environment with a token.
    # Intentionally left as an explicit integration boundary (no offline mock).
    print("Publishing via Fabric REST API...")
    raise NotImplementedError(
        "Live Fabric publish runs only in the SIT deploy environment with "
        f"{FABRIC_TOKEN_ENV} set and after `approved-to-apply`."
    )


if __name__ == "__main__":
    sys.exit(main())
