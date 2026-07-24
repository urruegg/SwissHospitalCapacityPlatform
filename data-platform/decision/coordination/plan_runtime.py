"""The golden-thread lifecycle: open -> propose -> approve (HITL) -> live-sync.

Pure orchestration over an injected :class:`~coordination.store.PlanStore` and
the deterministic :func:`impact.compute_expected_impact.compute_expected_impact`
tool (Sprint 26 WS-B). No randomness, no wall-clock reads: every function that
records a timestamp accepts an injectable ``now`` that defaults to a fixed
sentinel, so tests and the seed script are fully deterministic.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from impact.compute_expected_impact import compute_expected_impact

#: Fixed sentinel used when no ``now`` is supplied, so timestamps never leak
#: wall-clock nondeterminism into computed values or persisted records.
DEFAULT_NOW = "1970-01-01T00:00:00Z"

#: Word-boundary match for the "bot" token, delimited by string start/end or
#: ``-``/``_``/``[``/``]``. Catches ``github-actions[bot]``, ``dependabot[bot]``,
#: a bare ``bot`` handle, etc., WITHOUT matching human handles that merely
#: contain the substring "bot" (e.g. "Talbot", "Abbott", "talbot-anna").
_BOT_TOKEN_RE = re.compile(r"(^|[-_\[])bot([-_\]]|$)")


def _is_bot_approver(approver: Optional[str]) -> bool:
    """Refuse bot/service identities as HITL approvers (AGENTS.md Sec 5 refusal
    rules: agents must not approve their own deploy/delete-ceiling actions).

    An approver is treated as a bot if any of the following hold (case
    insensitive):

    * it is falsy (``None`` / empty string) — no approver is never a human;
    * it ends with the GitHub App suffix ``"[bot]"`` (e.g. ``"github-actions[bot]"``);
    * it exactly equals ``"copilot"``;
    * it contains a word-boundary-delimited ``"bot"`` token (e.g.
      ``dependabot[bot]``, ``ci-bot``, ``bot_runner``) — but NOT a mere
      substring match, so human handles like "Talbot" or "Abbott" are accepted.
    """
    if not approver:
        return True
    lowered = approver.lower()
    if lowered.endswith("[bot]"):
        return True
    if lowered == "copilot":
        return True
    if _BOT_TOKEN_RE.search(lowered):
        return True
    return False


def open_plan(
    store,
    *,
    episode_key: str,
    ward: str,
    bed_capacity: float,
    baseline_occupied_beds: float,
    target_pct: float,
    now: str = DEFAULT_NOW,
) -> Dict[str, Any]:
    """Open a new coordination plan for ``episode_key`` and persist it.

    ``plan_id`` is derived deterministically from ``episode_key`` (no
    randomness). ``baseline_pct`` / ``current_pct`` are both
    ``round(baseline_occupied_beds / bed_capacity * 100)`` at open time.
    """
    plan_id = f"plan-{episode_key}"
    baseline_pct = round(baseline_occupied_beds / bed_capacity * 100)
    plan = {
        "id": plan_id,
        "episode_key": episode_key,
        "ward": ward,
        "bed_capacity": bed_capacity,
        "baseline_occupied_beds": baseline_occupied_beds,
        "baseline_pct": baseline_pct,
        "current_pct": baseline_pct,
        "target_pct": target_pct,
        "actions": [],
        "forecast_deltas": [],
        "handoffs": [],
        "opened_at": now,
    }
    return store.create_plan(plan)


def propose_action(
    store,
    *,
    plan_id: str,
    role: str,
    lever_id: str,
    params: Dict[str, Any],
    gold: Dict[str, Any],
    catalog: Optional[List[Dict[str, Any]]] = None,
    proposed_by: Optional[str] = None,
    now: str = DEFAULT_NOW,
) -> Dict[str, Any]:
    """Propose a lever-backed action against ``plan_id``.

    Computes ``expected_impact`` via the deterministic impact tool, appends the
    new action id to ``plan.actions``, and persists both the action and the
    plan. ``proposed_by`` defaults to ``role`` and is the identity checked for
    self-approval in :func:`approve_action`.
    """
    plan = store.get_plan(plan_id)
    if plan is None:
        raise ValueError(f"unknown plan_id: {plan_id!r}")

    expected_impact = compute_expected_impact(lever_id, params, gold, catalog=catalog)

    action_index = len(store.list_actions(plan_id))
    action_id = f"{plan_id}-action-{action_index}"
    action = {
        "id": action_id,
        "plan_id": plan_id,
        "role": role,
        "proposed_by": proposed_by if proposed_by is not None else role,
        "lever_id": lever_id,
        "params": params,
        "expected_impact": expected_impact,
        "owner_role": expected_impact.get("owner_role"),
        "status": "proposed",
        "hitl_approver": None,
        "approved_at": None,
        "proposed_at": now,
    }
    store.create_action(action)

    plan["actions"].append(action_id)
    store.upsert_plan(plan)

    return store.get_action(action_id)


def approve_action(
    store,
    *,
    action_id: str,
    approver: str,
    gold: Dict[str, Any],
    catalog: Optional[List[Dict[str, Any]]] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """HITL-approve a proposed action and live-sync its plan.

    Refuses (raises) when:

    * ``approver`` is falsy;
    * ``approver`` resolves to a bot identity (see :func:`_is_bot_approver`);
    * ``approver`` is the same identity that proposed the action (self-approval);
    * the action is not currently in status ``"proposed"`` (double-approval guard).

    On success: re-validates ``expected_impact`` by re-calling
    :func:`compute_expected_impact.compute_expected_impact` against the
    supplied ``gold``/``catalog`` (never trusting the stored value blindly, per
    AGENTS.md's "re-validate untrusted values at every tool boundary" rule),
    marks the action ``"applied"``, appends a cumulative forecast-delta entry
    and updates ``plan.current_pct``, and records a cross-role handoff edge
    when ``owner_role != role``. Returns the updated plan.
    """
    if now is None:
        now = DEFAULT_NOW

    action = store.get_action(action_id)
    if action is None:
        raise ValueError(f"unknown action_id: {action_id!r}")

    if not approver:
        raise ValueError("approver is required")
    if _is_bot_approver(approver):
        raise PermissionError(f"bot approver refused: {approver!r}")

    proposer = action.get("proposed_by") or action.get("role")
    if str(approver).lower() == str(proposer).lower():
        raise PermissionError(
            f"self-approval refused: approver {approver!r} == proposing identity {proposer!r}"
        )

    if action["status"] != "proposed":
        raise ValueError(
            f"action {action_id!r} is not in status 'proposed' "
            f"(status={action['status']!r}); double-approval refused"
        )

    # Re-validate at this tool boundary rather than trusting the stored value.
    expected_impact = compute_expected_impact(
        action["lever_id"], action["params"], gold, catalog=catalog
    )

    action["expected_impact"] = expected_impact
    action["owner_role"] = expected_impact.get("owner_role")
    action["status"] = "applied"
    action["hitl_approver"] = approver
    action["approved_at"] = now
    store.upsert_action(action)

    plan = store.get_plan(action["plan_id"])
    if plan is None:
        raise ValueError(f"unknown plan_id: {action['plan_id']!r}")

    delta = expected_impact["delta"]
    applied_total = sum(entry["delta"] for entry in plan["forecast_deltas"]) + delta
    # Clamp at zero: a ward cannot go below empty, however many beds are
    # recovered by cumulative approved actions.
    current_occupied = max(0, plan["baseline_occupied_beds"] - applied_total)
    current_pct = round(current_occupied / plan["bed_capacity"] * 100)

    plan["forecast_deltas"].append(
        {
            "action_id": action_id,
            "lever_id": action["lever_id"],
            "delta": delta,
            "resulting_pct": current_pct,
        }
    )
    plan["current_pct"] = current_pct

    owner_role = expected_impact.get("owner_role")
    from_role = action["role"]
    if owner_role and owner_role != from_role:
        handoff = {
            "from_role": from_role,
            "to_role": owner_role,
            "action_id": action_id,
            "lever_id": action["lever_id"],
        }
        if handoff not in plan["handoffs"]:
            plan["handoffs"].append(handoff)

    return store.upsert_plan(plan)


def reject_action(
    store,
    *,
    action_id: str,
    approver: str,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """Reject a proposed action. No plan mutation — symmetric with
    :func:`approve_action`'s double-approval guard: only actions currently in
    status ``"proposed"`` may be rejected.

    For parity with :func:`approve_action`, a falsy ``approver`` is refused.
    (Bot/self-approval checks are intentionally not enforced here — rejecting
    an action has no side effect ceiling to gate.)
    """
    if now is None:
        now = DEFAULT_NOW

    if not approver:
        raise ValueError("approver is required")

    action = store.get_action(action_id)
    if action is None:
        raise ValueError(f"unknown action_id: {action_id!r}")
    if action["status"] != "proposed":
        raise ValueError(
            f"action {action_id!r} is not in status 'proposed' (status={action['status']!r})"
        )

    action["status"] = "rejected"
    action["hitl_approver"] = approver
    action["approved_at"] = now
    return store.upsert_action(action)
