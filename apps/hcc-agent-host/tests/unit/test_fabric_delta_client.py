"""Unit tests for FabricDeltaClient (Sprint 43 WS-2).

No cloud calls -- token_provider and table_reader are injected fakes.
"""

from __future__ import annotations

import pytest

from tools.fabric_delta_client import FabricDeltaClient


def _client(fake_reader):
    return FabricDeltaClient(
        workspace_id="ws-1",
        lakehouse_id="lh-1",
        token_provider=lambda: "fake-token",
        table_reader=fake_reader,
    )


def test_query_builds_correct_onelake_uri_and_passes_token():
    captured = {}

    def fake_reader(uri, token):
        captured["uri"] = uri
        captured["token"] = token
        return [{"ward": "B", "occupied": 46, "capacity": 50}]

    rows = _client(fake_reader).query("gold.bed_assignment")

    assert rows == [{"ward": "B", "occupied": 46, "capacity": 50}]
    assert captured["uri"] == (
        "abfss://ws-1@onelake.dfs.fabric.microsoft.com/lh-1/Tables/gold/bed_assignment"
    )
    assert captured["token"] == "fake-token"


def test_query_handles_schema_other_than_gold():
    captured = {}

    def fake_reader(uri, token):
        captured["uri"] = uri
        return []

    _client(fake_reader).query("ops.data_quality_runs")

    assert captured["uri"] == (
        "abfss://ws-1@onelake.dfs.fabric.microsoft.com/lh-1/Tables/ops/data_quality_runs"
    )


def test_query_raises_on_malformed_table_name():
    def fake_reader(uri, token):
        return []

    with pytest.raises(ValueError):
        _client(fake_reader).query("no_dot_in_this_name")


def test_query_returns_empty_list_when_table_missing():
    def fake_reader(uri, token):
        raise RuntimeError("Generic delta kernel error: No files in log segment")

    rows = _client(fake_reader).query("gold.seasonality")

    assert rows == []


def test_query_returns_empty_list_on_any_reader_exception():
    def fake_reader(uri, token):
        raise ValueError("boom -- some other unexpected error")

    rows = _client(fake_reader).query("gold.anaesthesia_status")

    assert rows == []
