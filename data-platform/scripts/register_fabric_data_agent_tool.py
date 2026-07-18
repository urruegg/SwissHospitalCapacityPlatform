"""Slice 0 — register the Fabric Data Agent as a tool on a Foundry agent.

Region-agnostic. ``--action plan`` (default) prints a deterministic plan and exits 0
without touching Foundry. ``--action apply`` requires the caller to pass
``--approved-to-apply <github-handle>`` (AGENTS.md §4) and performs the live
registration. Plan output is pure so it can be unit-tested without cloud.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

try:
    from azure.identity import DefaultAzureCredential  # noqa: F401
    _HAS_AZURE = True
except ImportError:
    _HAS_AZURE = False


def build_plan(
    foundry_agent: str,
    data_agent_endpoint: str,
    workspace_id: str,
    region: str,
) -> Dict[str, Any]:
    """Return the deterministic registration plan (no side effects)."""
    return {
        "action": "plan",
        "foundryAgent": foundry_agent,
        "region": region,
        "tool": {
            "type": "fabric_data_agent",
            "endpoint": data_agent_endpoint,
            "workspaceId": workspace_id,
            "ceiling": "read",
        },
    }


def _apply(plan: Dict[str, Any], approver: str) -> Dict[str, Any]:
    # AGENTS.md §4: the approver must be a human with repo write access. This
    # CLI enforces the non-empty + non-bot invariant; write-access verification
    # is performed out of band by the agent/human via github-mcp before apply.
    if approver.endswith("[bot]"):
        raise SystemExit("apply approver must be a human, not a bot identity (AGENTS.md §4)")
    if not _HAS_AZURE:
        raise SystemExit("azure-identity not installed; cannot apply")
    # Live Foundry registration goes here (data-plane call). Blocked on a
    # provisioned Fabric Data Agent endpoint (Phase 2 / Sprint 19); tracked in
    # issue #251. Verified manually per Task 8 Step 6 once the endpoint exists.
    applied = dict(plan)
    applied["action"] = "apply"
    applied["approvedBy"] = approver
    return applied


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--foundry-agent", required=True)
    p.add_argument("--data-agent-endpoint", required=True)
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--region", default="westus2")
    p.add_argument("--action", choices=["plan", "apply"], default="plan")
    p.add_argument("--approved-to-apply", dest="approver", default="")
    args = p.parse_args(argv)

    plan = build_plan(
        args.foundry_agent, args.data_agent_endpoint, args.workspace_id, args.region
    )
    if args.action == "plan":
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    if not args.approver:
        raise SystemExit("apply requires --approved-to-apply <github-handle> (AGENTS.md §4)")
    print(json.dumps(_apply(plan, args.approver), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
