"""Sprint 30 M1-observe — OTel-shaped agent-turn tracing facade.

The Observe stage of the closed-loop foundation (design §4/§5/§10 M1). Every
agent turn emits **retrieve -> model -> assemble** spans and one ``AgentTurn``
``customEvents``-shaped event.

Design goals
------------
- **Dependency-free + deterministic in CI.** The default :class:`TraceRecorder`
  buffers spans + events in memory and exports through a :class:`NullExporter`;
  no OpenTelemetry / Azure SDK import and no network are required to run or test.
- **Runtime seam.** A real Azure Monitor / OpenTelemetry exporter is injected at
  startup via :func:`configure` (see :mod:`observability.azure_exporter`),
  mirroring the ChatModel / CosmosPersistence "mock in CI, real in prod" pattern.
- **PHI-safe by construction (ADR-0016 / NFR-LEARN-001).** Callers put only
  hashes, ids, counts and boolean flags into span attributes / event properties
  -- never raw prompt or answer text.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, Protocol, runtime_checkable


@dataclass
class Span:
    """One OTel-shaped span. ``attributes`` carry only non-PHI metadata."""

    name: str
    parent: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    duration_ms: float = 0.0

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value


@dataclass
class CustomEvent:
    """An Application Insights ``customEvents``-shaped record."""

    name: str
    properties: dict[str, str] = field(default_factory=dict)
    measurements: dict[str, float] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@runtime_checkable
class Exporter(Protocol):
    """Sink for spans + events. Runtime implementations mirror to Azure Monitor."""

    def export_span(self, span: Span) -> None: ...

    def export_event(self, event: CustomEvent) -> None: ...


class NullExporter:
    """No-op exporter (default). Keeps CI dependency-free and offline."""

    def export_span(self, span: Span) -> None:  # noqa: D401 - trivial
        return None

    def export_event(self, event: CustomEvent) -> None:
        return None


class TraceRecorder:
    """In-memory span/event buffer with a pluggable downstream exporter."""

    def __init__(self, exporter: Exporter | None = None) -> None:
        self.exporter: Exporter = exporter or NullExporter()
        self.spans: list[Span] = []
        self.events: list[CustomEvent] = []
        self._stack: list[str] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[Span]:
        parent = self._stack[-1] if self._stack else None
        span = Span(name=name, parent=parent, attributes=dict(attributes))
        self._stack.append(name)
        started = time.perf_counter()
        try:
            yield span
        except BaseException:
            span.status = "error"
            raise
        finally:
            span.duration_ms = (time.perf_counter() - started) * 1000
            self._stack.pop()
            self.spans.append(span)
            self.exporter.export_span(span)

    def emit_event(
        self,
        name: str,
        *,
        properties: dict[str, str] | None = None,
        measurements: dict[str, float] | None = None,
    ) -> CustomEvent:
        event = CustomEvent(
            name=name,
            properties=dict(properties or {}),
            measurements=dict(measurements or {}),
        )
        self.events.append(event)
        self.exporter.export_event(event)
        return event


# --- module singleton --------------------------------------------------------

_recorder = TraceRecorder()


def get_recorder() -> TraceRecorder:
    return _recorder


def configure(exporter: Exporter) -> None:
    """Swap the downstream exporter on the active recorder (called at startup)."""
    _recorder.exporter = exporter


def reset_recorder() -> None:
    """Reset buffers + exporter to default. For test isolation."""
    _recorder.exporter = NullExporter()
    _recorder.spans.clear()
    _recorder.events.clear()
    _recorder._stack.clear()


def build_exporter_from_env() -> Exporter:
    """Return an Azure Monitor exporter iff a connection string is configured.

    The azure exporter is imported lazily so unit tests / CI never import the
    optional ``azure-monitor-opentelemetry`` dependency.
    """
    conn = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not conn:
        return NullExporter()
    try:
        from observability.azure_exporter import AzureMonitorExporter
    except Exception:  # pragma: no cover - optional dep not installed
        return NullExporter()
    return AzureMonitorExporter(conn)
