# apps/sim-capacity/src/closedloop/actuation.py
"""ActuationConsumer (Sprint 38 M2, design spec Sec 6). Applies HITL-approved
decision-tier actions to SimState. It never approves anything: it only acts on
actions the decision-tier already moved to status 'applied' via approve_action
(which enforces the bot/self-approval refusal). Idempotent per action id via a
'sim_applied_at' stamp."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from closedloop.effect import apply_effect
from closedloop.outcome import build_sim_outcome


class ActuationConsumer:
    def __init__(self, plan_store: Any, effect_by_lever: Dict[str, Dict[str, Any]]) -> None:
        self._store = plan_store
        self._effects = effect_by_lever

    def apply_approved(self, plan_id: str, state, now: str | None = None) -> List[Dict[str, Any]]:
        """Apply every approved-but-not-yet-actuated action for ``plan_id``.
        Returns the list of DC-SIM-OUTCOME-v1 records produced."""
        stamp = now or datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        outcomes: List[Dict[str, Any]] = []
        for action in self._store.list_actions(plan_id):
            if action.get("status") != "applied":
                continue  # only HITL-approved actions
            if action.get("sim_applied_at"):
                continue  # idempotency guard
            effect = self._effects.get(action["lever_id"])
            if effect is None:
                continue
            pre = state.snapshot()
            realised = apply_effect(state, effect, action["params"])
            post = state.snapshot()
            outcomes.append(build_sim_outcome(action, pre, post, realised, applied_ts=stamp))
            action["sim_applied_at"] = stamp
            self._store.upsert_action(action)
        return outcomes
