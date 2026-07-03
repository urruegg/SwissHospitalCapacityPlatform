"""Tests for the Event Hubs emitter (T3.5).

The emitter is exercised fully offline: a ``producer_client_factory`` returns a
:class:`~unittest.mock.MagicMock` that behaves as a context-manager producer,
so no real ``azure.eventhub`` connection is opened.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from emitters.eventhub_emitter import EventHubEmitter


def _make_producer_mock() -> MagicMock:
    """Build a MagicMock that behaves like an EventHubProducerClient context."""
    producer = MagicMock()
    producer.__enter__ = MagicMock(return_value=producer)
    producer.__exit__ = MagicMock(return_value=False)
    return producer


def test_send_single_envelope_ok():
    producer = _make_producer_mock()
    emitter = EventHubEmitter(
        fully_qualified_namespace="test.servicebus.windows.net",
        eventhub_name="test-hub",
        producer_client_factory=lambda: producer,
    )
    envelope = {
        "eventKind": "encounter.admitted",
        "eventId": "e1",
        "hospitalId": "H_USZ",
        "payload": {},
    }
    emitter.send(envelope)
    producer.send_batch.assert_called_once()
    sent = producer.send_batch.call_args.args[0]
    assert isinstance(sent, list) and len(sent) == 1
    assert sent[0]["properties"]["eventKind"] == "encounter.admitted"


def test_send_envelope_body_is_json_encoded():
    producer = _make_producer_mock()
    emitter = EventHubEmitter(
        "test.servicebus.windows.net",
        "test-hub",
        producer_client_factory=lambda: producer,
    )
    envelope = {
        "eventKind": "bed.state_changed",
        "eventId": "e2",
        "hospitalId": "H_LUKS",
        "simulatedAt": "2027-01-15T10:00:00Z",
        "emittedAt": "2026-07-03T15:00:00Z",
        "simRunId": "run-1",
        "seed": 42,
        "payload": {"bedId": "B-001", "newState": "occupied"},
    }
    emitter.send(envelope)
    sent = producer.send_batch.call_args.args[0][0]
    body_dict = json.loads(sent["body"].decode("utf-8"))
    assert body_dict["eventKind"] == "bed.state_changed"
    assert body_dict["payload"]["bedId"] == "B-001"
    assert body_dict["seed"] == 42


def test_send_retries_on_transient_error_then_succeeds():
    """Two transient failures then one success = 3 attempts total, one send_batch."""
    producer_ok = _make_producer_mock()
    call_count = [0]

    class FakeError(Exception):
        pass

    def factory() -> MagicMock:
        call_count[0] += 1
        if call_count[0] <= 2:
            p = _make_producer_mock()
            p.send_batch.side_effect = FakeError("transient")
            return p
        return producer_ok

    # Monkey-patch the EventHubError class the emitter's except clause resolves
    # via LOAD_GLOBAL so our FakeError is treated as retryable.
    import emitters.eventhub_emitter as ee

    original = ee.EventHubError
    ee.EventHubError = FakeError
    try:
        emitter = EventHubEmitter(
            "test.servicebus.windows.net",
            "test-hub",
            producer_client_factory=factory,
            max_retries=3,
        )
        emitter.send({"eventKind": "test", "payload": {}})
    finally:
        ee.EventHubError = original

    assert call_count[0] == 3
    producer_ok.send_batch.assert_called_once()


def test_send_raises_after_max_retries_exhausted():
    call_count = [0]

    class FakeError(Exception):
        pass

    def factory() -> MagicMock:
        call_count[0] += 1
        p = _make_producer_mock()
        p.send_batch.side_effect = FakeError("permanent")
        return p

    import emitters.eventhub_emitter as ee

    original = ee.EventHubError
    ee.EventHubError = FakeError
    try:
        emitter = EventHubEmitter(
            "test.servicebus.windows.net",
            "test-hub",
            producer_client_factory=factory,
            max_retries=2,
        )
        try:
            emitter.send({"eventKind": "test", "payload": {}})
            raise AssertionError("expected FakeError")
        except FakeError as e:
            assert str(e) == "permanent"
    finally:
        ee.EventHubError = original

    # max_retries=2 → up to 3 attempts (initial + 2 retries).
    assert call_count[0] == 3


def test_send_many_counts_and_dispatches_each():
    producer = _make_producer_mock()
    emitter = EventHubEmitter(
        "test.servicebus.windows.net",
        "test-hub",
        producer_client_factory=lambda: producer,
    )
    envelopes = [
        {
            "eventKind": "encounter.admitted",
            "eventId": f"e{i}",
            "hospitalId": "H_USZ",
            "payload": {},
        }
        for i in range(5)
    ]
    count = emitter.send_many(envelopes)
    assert count == 5
    assert producer.send_batch.call_count == 5


def test_get_producer_raises_when_sdk_missing_and_no_factory(monkeypatch):
    """Without the SDK installed and no factory, calling _get_producer should raise."""
    import emitters.eventhub_emitter as ee

    monkeypatch.setattr(ee, "_AZURE_AVAILABLE", False)
    emitter = EventHubEmitter(
        "test.servicebus.windows.net",
        "test-hub",
    )
    try:
        emitter._get_producer()
        raise AssertionError("expected RuntimeError")
    except RuntimeError as e:
        assert "azure-eventhub" in str(e)
