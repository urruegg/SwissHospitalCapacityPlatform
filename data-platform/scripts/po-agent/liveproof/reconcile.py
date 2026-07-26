"""WS-B Class B live-proof: reconcile-and-flag.

Compares a *read-only* live observation (see :mod:`probes`) against the
curated baseline recorded in ``docs/bom.yaml``,
``docs/region-availability.yaml`` and ``AGENTS.md``, then emits a
frozen ``GroundedChunk`` (classId ``B``).

Reconcile outcomes
------------------
* **match**   -> ``liveness=live``, ``status=verified``.
* **drift**   -> ``liveness=live``, ``status=requires-validation``; the
  text surfaces BOTH the live and the recorded value flagged ``drift``.
* **degrade** -> when the live probe failed (``ok=False``) the answer
  falls back to the recorded baseline with ``liveness=snapshot`` and
  ``status=partial`` (NFR-POA-004 snapshot transparency).

This module performs no network I/O: probes are executed in
:mod:`probes`; here we only load repo-local baseline documents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

CLASS_ID = "B"


@dataclass
class Observation:
    """A single read-only live measurement for a reference question."""

    question_id: str
    observed: Optional[str]
    feed: str
    as_of: str
    ok: bool = True


@dataclass
class Baseline:
    """The recorded/expected value plus its provenance in the repo."""

    value: str
    source_ref: str
    anchor: str


# --------------------------------------------------------------------------
# Baseline loaders (repo-local documents, read-only)
# --------------------------------------------------------------------------

def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_bom(repo_root: Path) -> dict:
    return _read_yaml(repo_root / "docs" / "bom.yaml")


def bom_fabric_capacity_sku(repo_root: Path) -> str:
    bom = load_bom(repo_root)
    for item in bom.get("items", []):
        if item.get("type") == "Microsoft.Fabric/capacities":
            return str(item.get("sku", ""))
    return ""


def bom_fabric_workspace_count(repo_root: Path) -> str:
    bom = load_bom(repo_root)
    count = sum(
        1
        for item in bom.get("items", [])
        if item.get("type") == "Microsoft.Fabric/workspaces"
    )
    return str(count)


def _read_agents(repo_root: Path) -> str:
    return (repo_root / "AGENTS.md").read_text(encoding="utf-8")


def agents_deploy_region(repo_root: Path) -> str:
    text = _read_agents(repo_root)
    m = re.search(r"deployed in `([a-z0-9]+)`", text)
    return m.group(1) if m else ""


def agents_subscription(repo_root: Path) -> str:
    text = _read_agents(repo_root)
    m = re.search(
        r"subscription `([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        r"[0-9a-f]{4}-[0-9a-f]{12})`",
        text,
    )
    return m.group(1) if m else ""


def agents_agent_count(repo_root: Path) -> str:
    text = _read_agents(repo_root)
    m = re.search(r"The (\d+) platform agents", text)
    return m.group(1) if m else ""


# --------------------------------------------------------------------------
# Reference-question -> baseline registry
# --------------------------------------------------------------------------

# Each entry: question text, resolver(repo_root) -> value, source ref + anchor.
BASELINE_RESOLVERS = {
    "q-fabric-capacity-sku": {
        "question": "Which SKU is the Fabric capacity deployed with?",
        "resolver": bom_fabric_capacity_sku,
        "source_ref": "docs/bom.yaml",
        "anchor": "bom-fabric-capacity",
    },
    "q-fabric-workspace-count": {
        "question": "How many Fabric workspaces are provisioned?",
        "resolver": bom_fabric_workspace_count,
        "source_ref": "docs/bom.yaml",
        "anchor": "Microsoft.Fabric/workspaces",
    },
    "q-deploy-region": {
        "question": "In which Azure region is the platform deployed?",
        "resolver": agents_deploy_region,
        "source_ref": "AGENTS.md",
        "anchor": "Tenant migration authoritative",
    },
    "q-subscription-scope": {
        "question": "Which Azure subscription hosts the platform?",
        "resolver": agents_subscription,
        "source_ref": "AGENTS.md",
        "anchor": "Tenant migration authoritative",
    },
    "q-foundry-agents-running": {
        "question": "How many platform agents are registered and running?",
        "resolver": agents_agent_count,
        "source_ref": "AGENTS.md",
        "anchor": "Foundry Agents (eastus2)",
    },
}

REFERENCE_QUESTION_IDS = tuple(BASELINE_RESOLVERS.keys())


def baseline_for(question_id: str, repo_root: Path) -> Baseline:
    spec = BASELINE_RESOLVERS.get(question_id)
    if spec is None:
        raise KeyError(f"unknown reference question: {question_id!r}")
    value = spec["resolver"](repo_root)
    return Baseline(
        value=str(value),
        source_ref=spec["source_ref"],
        anchor=spec["anchor"],
    )


# --------------------------------------------------------------------------
# Reconcile
# --------------------------------------------------------------------------

def _grounded_chunk(
    *,
    text: str,
    source_ref: str,
    anchor: str,
    as_of: str,
    liveness: str,
    status: str,
    confidence: float,
    language: str = "en",
) -> dict[str, Any]:
    """Assemble a GroundedChunk dict (frozen WS-G0 contract, classId B)."""

    return {
        "classId": CLASS_ID,
        "text": text,
        "citation": {"sourceRef": source_ref, "anchor": anchor},
        "asOf": _as_datetime(as_of),
        "liveness": liveness,
        "status": status,
        "confidence": confidence,
        "language": language,
    }


def _as_datetime(value: str) -> str:
    """Normalise a date-only string to an RFC3339 date-time (schema wants date-time)."""

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return f"{value}T00:00:00Z"
    return value


def reconcile(observation: Observation, repo_root: Path) -> dict[str, Any]:
    """Reconcile one live observation against the recorded baseline.

    Returns a single GroundedChunk (classId ``B``). Never raises for a
    failed probe: an ``ok=False`` observation degrades to a snapshot
    answer from the baseline document.
    """

    baseline = baseline_for(observation.question_id, repo_root)
    question = BASELINE_RESOLVERS[observation.question_id]["question"]

    # Degrade to snapshot when the live probe was unavailable.
    if not observation.ok or observation.observed is None:
        text = (
            f"{question} Recorded value: {baseline.value} "
            f"(snapshot; live probe unavailable, showing last recorded "
            f"baseline from {baseline.source_ref})."
        )
        return _grounded_chunk(
            text=text,
            source_ref=f"{baseline.source_ref} (snapshot)",
            anchor=baseline.anchor,
            as_of=observation.as_of,
            liveness="snapshot",
            status="partial",
            confidence=0.6,
        )

    live_ref = f"{observation.feed} @ {observation.as_of}"

    # Live value matches the recorded baseline -> verified.
    if str(observation.observed) == baseline.value:
        text = (
            f"{question} Live value {observation.observed} matches the "
            f"recorded baseline in {baseline.source_ref}."
        )
        return _grounded_chunk(
            text=text,
            source_ref=live_ref,
            anchor=baseline.anchor,
            as_of=observation.as_of,
            liveness="live",
            status="verified",
            confidence=0.9,
        )

    # Mismatch -> flag drift, surfacing BOTH values.
    text = (
        f"{question} DRIFT detected: live value {observation.observed} "
        f"(feed {observation.feed}) does not match the recorded baseline "
        f"{baseline.value} in {baseline.source_ref}. Human validation "
        f"required to determine which value is authoritative [drift]."
    )
    return _grounded_chunk(
        text=text,
        source_ref=live_ref,
        anchor=baseline.anchor,
        as_of=observation.as_of,
        liveness="live",
        status="requires-validation",
        confidence=0.5,
    )
