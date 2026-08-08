"""Sprint 41 WS-RET Task RET.2: real Fabric Data Agent client-builder test.

``_openai_assistants_client`` is monkeypatched so no network call is ever
made; it is a factory name (mirrors the OpenAI Assistants protocol the
published Fabric Data Agent endpoint speaks) not the ``openai`` SDK - see
``data_agent.py`` for why.
"""

from data_agent import build_production_client


def test_build_production_client_reuses_agent_host_connection(monkeypatch):
    calls = {}

    def fake_openai_client(**kwargs):
        calls.update(kwargs)
        return object()

    monkeypatch.setattr("data_agent._openai_assistants_client", fake_openai_client)
    build_production_client()
    assert "endpoint" in calls
