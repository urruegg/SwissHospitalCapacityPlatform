"""Slice 0 — register the Fabric Data Agent as a tool on a Foundry agent.

Region-agnostic. ``--action plan`` (default) prints a deterministic plan and exits 0
without touching Foundry. ``--action apply`` requires the caller to pass
``--approved-to-apply <github-handle>`` (AGENTS.md §4) and performs the live
registration. Plan output is pure so it can be unit-tested without cloud.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Callable, Dict, Optional

try:
    from azure.identity import DefaultAzureCredential  # noqa: F401
    _HAS_AZURE = True
except ImportError:
    _HAS_AZURE = False

# Models confirmed in M4 Step 1 (Foundry portal spike, 2026-07-18) against the
# ai-ihzhhpf-sit-eastus2 project. The Fabric Data Agent tool tile is disabled for
# gpt-5-mini ("This tool doesn't work with the model you selected"); gpt-5 enables
# it. Computer Use stays disabled even on gpt-5.
_MODEL_INCOMPATIBLE = ("gpt-5-mini",)
_MODEL_COMPATIBLE = ("gpt-5", "gpt-4o", "gpt-4.1")

_ARTIFACT_RE = re.compile(r"/aiskills/([^/]+)/", re.IGNORECASE)


def derive_artifact_id(data_agent_endpoint: str) -> Optional[str]:
    """Parse the Fabric Data Agent artifact (data agent) id from its endpoint.

    The published endpoint is deterministic:
    ``.../workspaces/{workspaceId}/aiskills/{artifactId}/aiassistant/openai``.
    Returns ``None`` when the segment is absent (e.g. a placeholder endpoint).
    """
    match = _ARTIFACT_RE.search(data_agent_endpoint or "")
    return match.group(1) if match else None


def build_plan(
    foundry_agent: str,
    data_agent_endpoint: str,
    workspace_id: str,
    region: str,
    artifact_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the deterministic registration plan (no side effects).

    Mirrors the Foundry "Connect to Fabric Data Agent" form confirmed in
    M4 Step 1: Connection + Name + Workspace ID + Artifact ID (the data agent
    id), NOT the raw aiskills/openai endpoint URL.
    """
    resolved_artifact = artifact_id or derive_artifact_id(data_agent_endpoint)
    connection_name = "fabric_dataagent_" + re.sub(
        r"[^a-z0-9]+", "_", foundry_agent.lower()
    ).strip("_")
    return {
        "action": "plan",
        "foundryAgent": foundry_agent,
        "region": region,
        "tool": {
            "type": "fabric_data_agent",
            "endpoint": data_agent_endpoint,
            "workspaceId": workspace_id,
            "artifactId": resolved_artifact,
            "ceiling": "read",
            "connectionForm": {
                "connection": "Add a new connection",
                "name": connection_name,
                "workspaceId": workspace_id,
                "artifactId": resolved_artifact,
            },
            "modelRequirement": {
                "incompatible": list(_MODEL_INCOMPATIBLE),
                "compatible": list(_MODEL_COMPATIBLE),
                "note": (
                    "Foundry agent must run a Fabric-Data-Agent-compatible model; "
                    "gpt-5-mini is not supported (M4 Step 1 portal spike)."
                ),
            },
        },
    }


def _default_connection_factory(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Live path: create the Foundry Fabric connection via az rest / SDK using the
    # shape confirmed in M4 Step 1. Requires azure-identity; called only on apply.
    if not _HAS_AZURE:
        raise SystemExit("azure-identity not installed; cannot apply")
    raise SystemExit(
        "connection_factory not provided: pass the M4-confirmed live factory to apply"
    )


def _apply(
    plan: Dict[str, Any],
    approver: str,
    connection_factory: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    # AGENTS.md §4: the approver must be a human with repo write access. This
    # CLI enforces the non-empty + non-bot invariant; write-access verification
    # is performed out of band by the agent/human via github-mcp before apply.
    if not approver:
        raise SystemExit("apply requires a human approver handle")
    if approver.endswith("[bot]"):
        raise SystemExit("apply approver must be a human, not a bot identity (AGENTS.md §4)")
    factory = connection_factory or _default_connection_factory
    payload = {
        "foundryAgent": plan["foundryAgent"],
        "tool": plan["tool"],
        "region": plan["region"],
    }
    connection = factory(payload)
    applied = dict(plan)
    applied["action"] = "apply"
    applied["approvedBy"] = approver
    applied["connection"] = connection
    return applied


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--foundry-agent", required=True)
    p.add_argument("--data-agent-endpoint", required=True)
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--artifact-id", dest="artifact_id", default=None,
                   help="Fabric Data Agent artifact id; derived from the endpoint when omitted")
    p.add_argument("--region", default="westus2")
    p.add_argument("--action", choices=["plan", "apply"], default="plan")
    p.add_argument("--approved-to-apply", dest="approver", default="")
    args = p.parse_args(argv)

    plan = build_plan(
        args.foundry_agent, args.data_agent_endpoint, args.workspace_id, args.region,
        artifact_id=args.artifact_id,
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
