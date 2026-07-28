"""M4 T2 (RED) — interaction source/sink seams for the online-eval job.

In-memory implementation for tests/local; a Cosmos-backed store is a lazy
runtime seam (mirrors the M1 Azure Monitor exporter) that never imports the
azure SDK in CI.
"""

import sys

from lib import online_store


def _rec(iid, agent):
    return {"interactionId": iid, "agent": agent, "eval": {"scored": False}}


def test_in_memory_read_recent_filters_by_agent_and_limit():
    store = online_store.InMemoryStore([
        _rec("AIX-1", "ooa-agent"),
        _rec("AIX-2", "bmca-agent"),
        _rec("AIX-3", "ooa-agent"),
        _rec("AIX-4", "ooa-agent"),
    ])
    ooa = store.read_recent(agent="ooa-agent", limit=10)
    assert {r["interactionId"] for r in ooa} == {"AIX-1", "AIX-3", "AIX-4"}
    limited = store.read_recent(agent="ooa-agent", limit=2)
    assert len(limited) == 2
    all_agents = store.read_recent(agent=None, limit=10)
    assert len(all_agents) == 4


def test_in_memory_update_eval_writes_back():
    store = online_store.InMemoryStore([_rec("AIX-1", "ooa-agent")])
    store.update_eval("AIX-1", {"scored": True, "passedAll": True})
    got = store.read_recent(agent=None, limit=10)[0]
    assert got["eval"]["scored"] is True
    assert got["eval"]["passedAll"] is True


def test_update_eval_unknown_id_raises():
    store = online_store.InMemoryStore([])
    try:
        store.update_eval("AIX-missing", {"scored": True})
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown interactionId")


def test_build_store_from_env_defaults_to_none(monkeypatch):
    for var in ("COSMOS_ENDPOINT", "COSMOS_DATABASE", "COSMOS_CONTAINER"):
        monkeypatch.delenv(var, raising=False)
    assert online_store.build_store_from_env() is None


def test_build_store_from_env_imports_no_azure_when_unconfigured(monkeypatch):
    for var in ("COSMOS_ENDPOINT", "COSMOS_DATABASE", "COSMOS_CONTAINER"):
        monkeypatch.delenv(var, raising=False)
    for mod in list(sys.modules):
        if mod.startswith("azure.cosmos"):
            del sys.modules[mod]
    online_store.build_store_from_env()
    assert not any(m.startswith("azure.cosmos") for m in sys.modules)
