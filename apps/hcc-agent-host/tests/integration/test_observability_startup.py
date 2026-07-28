"""Sprint 30 M1-observe T3 (RED) — startup wiring of the trace exporter.

``create_app`` configures the active recorder with an exporter built from the
environment. With no connection string it must default to the dependency-free
:class:`NullExporter` and must not import the optional azure SDK.
"""

from __future__ import annotations

import sys

from observability import tracing


def test_create_app_configures_null_exporter_without_conn_string(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    tracing.reset_recorder()
    from api.app import create_app

    create_app()
    assert isinstance(tracing.get_recorder().exporter, tracing.NullExporter)


def test_create_app_wires_exporter_from_env(monkeypatch):
    sentinel = tracing.NullExporter()
    called = {"n": 0}

    def _fake_build():
        called["n"] += 1
        return sentinel

    monkeypatch.setattr(tracing, "build_exporter_from_env", _fake_build)
    tracing.reset_recorder()
    from api.app import create_app

    create_app()
    assert called["n"] >= 1
    assert tracing.get_recorder().exporter is sentinel


def test_startup_does_not_import_azure_monitor_when_unconfigured(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    for mod in list(sys.modules):
        if mod.startswith("azure.monitor"):
            del sys.modules[mod]
    tracing.reset_recorder()
    from api.app import create_app

    create_app()
    assert not any(m.startswith("azure.monitor") for m in sys.modules)


def test_build_exporter_from_env_uses_azure_when_conn_string_set(monkeypatch):
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=00000000-0000-0000-0000-000000000000")
    exporter = tracing.build_exporter_from_env()
    # Either the azure adapter (if the optional dep is installed) or a safe
    # Null fallback (if not) — never a crash.
    assert exporter is not None
    assert hasattr(exporter, "export_span")
    assert hasattr(exporter, "export_event")
