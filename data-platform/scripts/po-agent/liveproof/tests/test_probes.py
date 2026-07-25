"""WS-B Class B live-proof: probe + liveProof orchestration tests.

Covers the acceptance gate: all five reference questions answered,
strictly read-only, and snapshot degradation on probe failure.
"""

from pathlib import Path

import pytest

import probes
import reconcile

REPO_ROOT = Path(__file__).resolve().parents[5]

READ_ONLY_METHODS = {"query", "list_workspaces", "list_agents"}


class _RecordingResourceGraph:
    """Fake Resource Graph that only answers read-only KQL queries."""

    def __init__(self, sku="F2", location="westus2", subscription=""):
        self.sku = sku
        self.location = location
        self.subscription = subscription
        self.calls = []

    def query(self, kql):
        self.calls.append(("query", kql))
        low = kql.lower()
        if "sku" in low:
            return [{"sku": self.sku}]
        if "location" in low:
            return [{"location": self.location}]
        if "subscriptionid" in low:
            return [{"subscriptionId": self.subscription}]
        return []

    # Any mutating attribute access is a hard failure in tests.
    def __getattr__(self, name):
        raise AttributeError(f"read-only client: {name!r} not permitted")


class _FakeFabricRest:
    def __init__(self, workspace_count=1):
        self._workspaces = [{"id": i} for i in range(workspace_count)]
        self.calls = []

    def list_workspaces(self):
        self.calls.append(("list_workspaces",))
        return self._workspaces

    def __getattr__(self, name):
        raise AttributeError(f"read-only client: {name!r} not permitted")


class _FakeFoundryAgents:
    def __init__(self, running=8):
        self._agents = [{"status": "Running"} for _ in range(running)]
        self.calls = []

    def list_agents(self):
        self.calls.append(("list_agents",))
        return self._agents

    def __getattr__(self, name):
        raise AttributeError(f"read-only client: {name!r} not permitted")


def _matching_clients():
    """Fakes wired to return exactly the recorded baseline values."""

    sku = reconcile.baseline_for("q-fabric-capacity-sku", REPO_ROOT).value
    region = reconcile.baseline_for("q-deploy-region", REPO_ROOT).value
    sub = reconcile.baseline_for("q-subscription-scope", REPO_ROOT).value
    ws_count = int(reconcile.baseline_for("q-fabric-workspace-count", REPO_ROOT).value)
    running = int(reconcile.baseline_for("q-foundry-agents-running", REPO_ROOT).value)
    return {
        "resource_graph": _RecordingResourceGraph(
            sku=sku, location=region, subscription=sub
        ),
        "fabric_rest": _FakeFabricRest(workspace_count=ws_count),
        "foundry_agents": _FakeFoundryAgents(running=running),
    }


def test_all_five_reference_questions_are_covered():
    assert len(probes.REFERENCE_QUESTION_IDS) == 5

    clients = _matching_clients()
    for qid in probes.REFERENCE_QUESTION_IDS:
        chunks = probes.liveProof(qid, "sub-scope", clients=clients, repo_root=REPO_ROOT)
        assert len(chunks) == 1, qid
        chunk = chunks[0]
        assert chunk["classId"] == "B"
        # Baseline-matching probe -> verified, live.
        assert chunk["status"] == "verified", qid
        assert chunk["liveness"] == "live", qid


def test_probes_are_read_only():
    clients = _matching_clients()
    for qid in probes.REFERENCE_QUESTION_IDS:
        probes.liveProof(qid, "sub-scope", clients=clients, repo_root=REPO_ROOT)

    rg = clients["resource_graph"]
    fab = clients["fabric_rest"]
    foundry = clients["foundry_agents"]
    for name, _ in rg.calls:
        assert name in READ_ONLY_METHODS
    for call in fab.calls + foundry.calls:
        assert call[0] in READ_ONLY_METHODS


def test_probe_failure_degrades_to_snapshot():
    class _Boom:
        def query(self, _):
            raise RuntimeError("resource graph unreachable")

        def __getattr__(self, name):
            raise AttributeError(name)

    clients = {"resource_graph": _Boom()}
    chunks = probes.liveProof(
        "q-fabric-capacity-sku", "sub-scope", clients=clients, repo_root=REPO_ROOT
    )
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["liveness"] == "snapshot"
    assert chunk["status"] == "partial"
    # Falls back to the recorded baseline value (F2).
    baseline = reconcile.baseline_for("q-fabric-capacity-sku", REPO_ROOT).value
    assert baseline in chunk["text"]


def test_free_text_question_resolves():
    clients = _matching_clients()
    chunks = probes.liveProof(
        "In which region is the platform deployed?",
        "sub-scope",
        clients=clients,
        repo_root=REPO_ROOT,
    )
    assert len(chunks) == 1
    assert chunks[0]["citation"]["anchor"]


def test_unknown_question_returns_empty():
    chunks = probes.liveProof(
        "what is the meaning of life?", "sub-scope", clients={}, repo_root=REPO_ROOT
    )
    assert chunks == []
