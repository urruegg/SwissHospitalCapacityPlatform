"""Sprint 30 M1-observe T1 (RED) — OTel-shaped tracing facade.

Dependency-free, deterministic. The recorder buffers spans + customEvents in
memory (default) so tests + CI never touch network/Azure; a real exporter is an
injectable seam wired at runtime.
"""

import time

import pytest

from observability import tracing


@pytest.fixture(autouse=True)
def _fresh_recorder():
    tracing.reset_recorder()
    yield
    tracing.reset_recorder()


def test_span_records_name_and_duration():
    rec = tracing.get_recorder()
    with rec.span("agent.model", agent="ooa-agent") as span:
        time.sleep(0.001)
        span.set_attribute("model.name", "MockChatModel")
    assert len(rec.spans) == 1
    s = rec.spans[0]
    assert s.name == "agent.model"
    assert s.attributes["agent"] == "ooa-agent"
    assert s.attributes["model.name"] == "MockChatModel"
    assert s.duration_ms >= 0
    assert s.status == "ok"


def test_span_records_error_status_on_exception():
    rec = tracing.get_recorder()
    with pytest.raises(ValueError):
        with rec.span("agent.retrieve"):
            raise ValueError("boom")
    assert rec.spans[0].status == "error"


def test_nested_spans_preserve_order_and_parent():
    rec = tracing.get_recorder()
    with rec.span("agent.turn") as root:
        with rec.span("agent.retrieve"):
            pass
        with rec.span("agent.model"):
            pass
    names = [s.name for s in rec.spans]
    # children close before the root; root recorded last
    assert names == ["agent.retrieve", "agent.model", "agent.turn"]
    assert rec.spans[0].parent == "agent.turn"
    assert root.parent is None


def test_emit_event_records_properties_and_measurements():
    rec = tracing.get_recorder()
    rec.emit_event(
        "AgentTurn",
        properties={"agent": "ooa-agent", "refused": "false"},
        measurements={"latencyMs": 12.0, "citationCount": 2.0},
    )
    assert len(rec.events) == 1
    ev = rec.events[0]
    assert ev.name == "AgentTurn"
    assert ev.properties["agent"] == "ooa-agent"
    assert ev.measurements["citationCount"] == 2.0


def test_null_exporter_is_default_and_noop():
    rec = tracing.get_recorder()
    assert isinstance(rec.exporter, tracing.NullExporter)
    # exporting through the null exporter must not raise
    with rec.span("agent.turn"):
        pass
    rec.emit_event("AgentTurn", properties={}, measurements={})


def test_configure_swaps_exporter_and_receives_span_and_event():
    class _Capture(tracing.Exporter):
        def __init__(self):
            self.spans = []
            self.events = []

        def export_span(self, span):
            self.spans.append(span)

        def export_event(self, event):
            self.events.append(event)

    cap = _Capture()
    tracing.configure(cap)
    rec = tracing.get_recorder()
    with rec.span("agent.turn"):
        pass
    rec.emit_event("AgentTurn", properties={}, measurements={})
    assert len(cap.spans) == 1
    assert len(cap.events) == 1


def test_build_exporter_from_env_defaults_to_null(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    exporter = tracing.build_exporter_from_env()
    assert isinstance(exporter, tracing.NullExporter)
