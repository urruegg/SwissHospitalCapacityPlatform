"""WS-B Class B live-proof: read-only probes + ``liveProof`` orchestration.

Implements the frozen Class B tool signature::

    liveProof(question: str, subscriptionScope: str) -> GroundedChunk[]

Every probe is **strictly read-only**: Azure Resource Graph queries,
Fabric REST GETs and Foundry Agent API list calls. No probe performs a
mutation. The live clients are injected (``clients=``) so tests supply
fakes and no network call is made in CI.

Each probe returns an :class:`reconcile.Observation`; ``liveProof``
reconciles it against the recorded baseline (see :mod:`reconcile`) and,
on any probe failure, degrades transparently to a ``snapshot`` answer.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import reconcile
from reconcile import Observation

# Repo root: data-platform/scripts/po-agent/liveproof/probes.py -> parents[4].
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]


def _today() -> str:
    return _dt.date.today().isoformat()


# --------------------------------------------------------------------------
# Read-only probe implementations
# --------------------------------------------------------------------------
# A probe is a callable taking the injected ``clients`` mapping and
# returning the observed value as a string. Clients expose read-only
# methods only; a probe MUST NOT call any mutating method.

def _probe_fabric_capacity_sku(clients: dict[str, Any]) -> str:
    rg = clients["resource_graph"]
    rows = rg.query(
        "resources | where type =~ 'microsoft.fabric/capacities' "
        "| project sku = tostring(sku.name) | take 1"
    )
    return str(rows[0]["sku"])


def _probe_fabric_workspace_count(clients: dict[str, Any]) -> str:
    fabric = clients["fabric_rest"]
    workspaces = fabric.list_workspaces()
    return str(len(workspaces))


def _probe_deploy_region(clients: dict[str, Any]) -> str:
    rg = clients["resource_graph"]
    rows = rg.query(
        "resources | where type =~ 'microsoft.fabric/capacities' "
        "| project location | take 1"
    )
    return str(rows[0]["location"])


def _probe_subscription_scope(clients: dict[str, Any]) -> str:
    rg = clients["resource_graph"]
    rows = rg.query(
        "resourcecontainers | where type =~ "
        "'microsoft.resources/subscriptions' | project subscriptionId | take 1"
    )
    return str(rows[0]["subscriptionId"])


def _probe_foundry_agents_running(clients: dict[str, Any]) -> str:
    foundry = clients["foundry_agents"]
    agents = foundry.list_agents()
    running = [a for a in agents if str(a.get("status", "")).lower() == "running"]
    return str(len(running))


@dataclass
class Probe:
    question_id: str
    feed: str
    run: Callable[[dict[str, Any]], str]


# Ordered registry of the five reference questions.
PROBES: dict[str, Probe] = {
    "q-fabric-capacity-sku": Probe(
        "q-fabric-capacity-sku", "Azure Resource Graph", _probe_fabric_capacity_sku
    ),
    "q-fabric-workspace-count": Probe(
        "q-fabric-workspace-count", "Fabric REST", _probe_fabric_workspace_count
    ),
    "q-deploy-region": Probe(
        "q-deploy-region", "Azure Resource Graph", _probe_deploy_region
    ),
    "q-subscription-scope": Probe(
        "q-subscription-scope", "Azure Resource Graph", _probe_subscription_scope
    ),
    "q-foundry-agents-running": Probe(
        "q-foundry-agents-running", "Foundry Agent API", _probe_foundry_agents_running
    ),
}

REFERENCE_QUESTION_IDS = tuple(PROBES.keys())

# Keyword hints to resolve free-text questions to a probe id.
_QUESTION_KEYWORDS = {
    "q-fabric-capacity-sku": ("sku", "capacity"),
    "q-fabric-workspace-count": ("workspace", "how many workspace"),
    "q-deploy-region": ("region", "location", "where"),
    "q-subscription-scope": ("subscription",),
    "q-foundry-agents-running": ("agent", "running", "foundry"),
}


def resolve_question_id(question: str) -> Optional[str]:
    """Best-effort map free-text / id to a known reference-question id."""

    q = question.strip().lower()
    if q in PROBES:
        return q
    for qid, keywords in _QUESTION_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return qid
    return None


def _observe(probe: Probe, clients: dict[str, Any]) -> Observation:
    """Run a single probe read-only; failure -> ok=False (degrade later)."""

    try:
        observed = probe.run(clients)
        return Observation(
            question_id=probe.question_id,
            observed=observed,
            feed=probe.feed,
            as_of=_today(),
            ok=True,
        )
    except Exception:  # any live failure degrades to snapshot, never raises
        return Observation(
            question_id=probe.question_id,
            observed=None,
            feed=probe.feed,
            as_of=_today(),
            ok=False,
        )


def liveProof(
    question: str,
    subscriptionScope: str,
    clients: Optional[dict[str, Any]] = None,
    repo_root: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """Answer a Class B reference question read-only, reconciled + flagged.

    Parameters
    ----------
    question:
        A reference-question id (e.g. ``q-deploy-region``) or free text.
    subscriptionScope:
        The subscription the live probes are scoped to (audit only; the
        injected clients enforce the actual scope).
    clients:
        Read-only live clients ``{resource_graph, fabric_rest,
        foundry_agents}``. Injected so tests supply fakes.
    repo_root:
        Baseline document root (defaults to the repo root).

    Returns a list of GroundedChunk dicts (classId ``B``). An unknown
    question yields an empty list (grounded refusal upstream). A failed
    probe degrades to a ``snapshot`` chunk.
    """

    root = repo_root or DEFAULT_REPO_ROOT
    clients = clients or {}

    qid = resolve_question_id(question)
    if qid is None:
        return []

    probe = PROBES[qid]
    observation = _observe(probe, clients)
    return [reconcile.reconcile(observation, repo_root=root)]
