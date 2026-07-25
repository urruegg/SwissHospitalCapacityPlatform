"""Register the decision-tier coordination tool onto the six Foundry agents.

Sprint 26 WS-C, workstream C. Mirrors the plan/apply shape of
``data-platform/scripts/register_fabric_data_agent_tool.py``: a pure,
unit-testable :func:`build_plan` (no side effects) and a HITL-gated
:func:`apply` that only mutates Foundry when handed an explicit human approver
(``AGENTS.md`` §4) and a live registration factory.

The tool being registered is the deterministic coordination runtime — the
Cosmos ``plans`` / ``proposed_actions`` containers, the
``compute_expected_impact`` tool, and each role's lever catalog — so every
proposing agent can assemble DC-INSIGHT-v1 recommendations and drive the
``open -> propose -> HITL approve -> live-sync`` thread. The Foundry project is
eastus2 per ADR-0032; a real apply runs there via WIF, never from this repo's CI.

Run from ``data-platform/decision``:
``python -m foundry.register_decision_tier --action plan``.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, Dict, List, Optional

from coordination.plan_runtime import _is_bot_approver

#: Foundry project region hosting the eight platform agents (ADR-0032).
DEFAULT_REGION = "eastus2"

#: The six decision-tier *proposing* agents, in a stable order. The other two
#: platform agents (data-quality, onboarding) are not DC-INSIGHT-v1 proposers
#: and are intentionally excluded.
DECISION_TIER_ROLES: List[str] = ["ooa", "dca", "bmca", "orsa", "sba", "csa"]

_ROLE_SET = set(DECISION_TIER_ROLES)

#: Cosmos database + container names, mirroring infra/modules/cosmos/csa.bicep.
_COSMOS = {
    "database": "csa",
    "plans": "plans",
    "proposedActions": "proposed_actions",
}


def _agent_name(role: str) -> str:
    return f"{role}-agent"


def build_plan(role: str, region: str = DEFAULT_REGION) -> Dict[str, Any]:
    """Return the deterministic registration plan for one role (no side effects).

    Raises ``KeyError`` for a role outside :data:`DECISION_TIER_ROLES`.
    """
    if role not in _ROLE_SET:
        raise KeyError(f"unknown decision-tier role: {role!r}")
    return {
        "action": "plan",
        "foundryAgent": _agent_name(role),
        "region": region,
        "tool": {
            "type": "decision_tier_coordination",
            "role": role,
            # `write` in the platform sense: the tool can create plans and
            # *propose* actions autonomously, but applying a proposed action is
            # HITL-gated (see `hitl` below), so no lever takes effect without a
            # human approver.
            "ceiling": "write",
            "cosmos": dict(_COSMOS),
            "impactTool": "compute_expected_impact",
            "leverCatalog": f"data-platform/decision/levers/{role}.yaml",
            "runtime": "data-platform/decision/coordination/plan_runtime.py",
            "hitl": {
                "approvalPhrase": "approved-to-apply",
                "refuseBotApprovers": True,
                "refuseSelfApproval": True,
            },
        },
    }


def build_all_plans(region: str = DEFAULT_REGION) -> List[Dict[str, Any]]:
    """Return the registration plans for all six decision-tier agents, in order."""
    return [build_plan(role, region) for role in DECISION_TIER_ROLES]


def _default_registration_factory(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Live path: register/update the tool on the Foundry agent via the Agents
    # REST API (ADR-0032, api-version 2025-05-15-preview) using WIF creds.
    # Deliberately not implemented here — pass the live factory to apply so a
    # dry run can never accidentally mutate Foundry.
    raise SystemExit(
        "registration_factory not provided: pass the live Foundry factory to apply"
    )


def apply(
    plan: Dict[str, Any],
    approver: str,
    *,
    registration_factory: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Register the tool on one Foundry agent. HITL-gated per ``AGENTS.md`` §4.

    Refuses (``SystemExit``) when ``approver`` is falsy or a bot identity, or
    when no live ``registration_factory`` is supplied. Repo-write-access
    verification of the approver is performed out of band via ``github-mcp``.
    """
    if not approver:
        raise SystemExit("apply requires a human approver handle (AGENTS.md §4)")
    if _is_bot_approver(approver):
        raise SystemExit(
            f"apply approver must be a human, not a bot identity: {approver!r} (AGENTS.md §4)"
        )

    factory = registration_factory or _default_registration_factory
    registration = factory(
        {
            "foundryAgent": plan["foundryAgent"],
            "tool": plan["tool"],
            "region": plan["region"],
        }
    )
    applied = dict(plan)
    applied["action"] = "apply"
    applied["approvedBy"] = approver
    applied["registration"] = registration
    return applied


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--role",
        choices=DECISION_TIER_ROLES,
        default=None,
        help="Register a single role; default registers all six agents.",
    )
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--action", choices=["plan", "apply"], default="plan")
    parser.add_argument("--approved-to-apply", dest="approver", default="")
    args = parser.parse_args(argv)

    if args.action == "plan":
        if args.role is None:
            print(json.dumps(build_all_plans(args.region), indent=2, sort_keys=True))
        else:
            print(json.dumps(build_plan(args.role, args.region), indent=2, sort_keys=True))
        return 0

    if not args.approver:
        raise SystemExit("apply requires --approved-to-apply <github-handle> (AGENTS.md §4)")
    if args.role is None:
        raise SystemExit("apply requires --role <role> (register one agent at a time)")
    # Live apply needs the Foundry factory wired in by the in-VNet caller; the
    # CLI path intentionally has no default factory, so this raises unless the
    # caller imports apply() with a live factory.
    print(json.dumps(apply(build_plan(args.role, args.region), args.approver), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
