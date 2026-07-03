"""Deploy Fabric Data Agent (T4.6, Sprint 09 v2.0.0).

Region-agnostic — flip --region and --workspace-id at CLI for Swiss GA migration.
Per design spec §5.6 Reference-implementation preservation.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

try:
    from azure.identity import DefaultAzureCredential
    _HAS_AZURE = True
except ImportError:
    _HAS_AZURE = False


FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"


def build_payload(agent_name: str, region: str, workspace_id: str) -> Dict[str, Any]:
    """Build Data Agent definition per design spec §5.1."""
    return {
        "displayName": agent_name,
        "description": (
            "MVO ontology-grounded natural-language query agent. "
            f"Region: {region}. Workspace: {workspace_id}. "
            "Grounding: MVO reference-layer TTL v0.2.0 + capacity-dashboard semantic model. "
            "See agents/fabric-data-agent/AGENT.md for scope and refusal rules."
        ),
        "grounding": {
            "semanticModels": ["capacity-dashboard"],
            "ontologyReferences": [
                "docs/ontology/reference-layer.ttl",
                "docs/ontology/crosswalk.md",
            ],
        },
        "refusalRules": [
            "no synthetic data generation (query-only)",
            "no cross-hospital re-identification queries",
            "no semantic model / ontology mutation",
        ],
        "regionPin": region,
    }


def deploy(workspace_id: str, agent_name: str, region: str, dry_run: bool) -> int:
    payload = build_payload(agent_name, region, workspace_id)
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataAgents"

    if dry_run:
        print(f"[DRY-RUN] Target: POST {url}")
        print(f"[DRY-RUN] Payload:\n{json.dumps(payload, indent=2)}")
        return 0

    if not _HAS_AZURE:
        print(
            "ERROR: azure-identity not installed. `pip install azure-identity requests`",
            file=sys.stderr,
        )
        return 2

    try:
        import requests
    except ImportError:
        print("ERROR: requests not installed. `pip install requests`", file=sys.stderr)
        return 2

    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default").token
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code >= 300:
        print(f"ERROR: {resp.status_code} — {resp.text}", file=sys.stderr)
        return 3
    print(
        f"OK: {resp.status_code} — Agent '{agent_name}' deployed to workspace {workspace_id}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy Fabric Data Agent (T4.6)")
    parser.add_argument(
        "--workspace-id", required=True, help="Fabric workspace ID (GUID)"
    )
    parser.add_argument(
        "--agent-name", default="fabric-data-agent", help="Agent display name"
    )
    parser.add_argument(
        "--region",
        default="westus2",
        choices=["westus2", "switzerlandnorth"],
        help="Region pin per ADR-0013",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print payload without POST"
    )
    args = parser.parse_args()
    return deploy(args.workspace_id, args.agent_name, args.region, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
