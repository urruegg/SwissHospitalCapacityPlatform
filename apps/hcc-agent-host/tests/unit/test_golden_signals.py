"""Sprint 44 live path (Slice 1) — gold.ext_fact_signal -> BoardSignal mapping.

Pure, offline unit tests for the translation that lets the golden surface serve
live external signals (Event Hub -> Fabric gold) to the app's OOA/CSA signal
panels. No Spark, no cloud: the mapping takes plain row dicts (as returned by
``tools.fabric_delta_client.FabricDeltaClient.query``) and emits ``BoardSignal``
dicts matching ``apps/hcc-app-fluent/src/data/roleboard/occupancy-data.ts``.
"""

from __future__ import annotations

from golden.signals import gold_rows_to_board_signals


def _webiq_fact() -> dict:
    return {
        "ext_signal_id": "webiq-epidemic-zh",
        "ext_source_id": "webiq",
        "ext_hazard_type": "epidemic",
        "ext_severity": "Moderate",
        "ext_lage_tier": 2,
        "ext_cantons": ["ZH"],
        "ext_status": "Actual",
    }


def _webiq_source(data_mode: str = "Live") -> dict:
    return {
        "ext_source_id": "webiq",
        "ext_source_authority": "Microsoft Web IQ",
        "ext_trust_tier": "B",
        "ext_data_mode": data_mode,
    }


def test_live_webiq_row_maps_to_board_signal():
    [sig] = gold_rows_to_board_signals([_webiq_fact()], [_webiq_source("Live")])
    assert sig["id"] == "webiq-epidemic-zh"
    assert sig["label"] == "Microsoft Web IQ"
    assert sig["scope"] == "external"
    assert sig["provenance"] == "live"
    assert sig["trustClass"] == "Trust-B"
    assert sig["hazardType"] == "epidemic"
    assert sig["cantons"] == ["ZH"]
    assert sig["iconKey"] == "globe"
    assert sig["statusLabel"] == "Actual"
    assert sig["statusTone"] == "watch"  # Moderate -> watch


def test_simulated_source_yields_simulated_provenance():
    [sig] = gold_rows_to_board_signals([_webiq_fact()], [_webiq_source("Simulated")])
    assert sig["provenance"] == "simulated"


def test_empty_fact_rows_yield_no_signals():
    assert gold_rows_to_board_signals([], [_webiq_source()]) == []


def test_unknown_source_falls_back_without_trust_class():
    fact = {"ext_source_id": "mystery", "ext_signal_id": "m-1", "ext_hazard_type": "heat", "ext_severity": "Severe"}
    [sig] = gold_rows_to_board_signals([fact], [])
    assert sig["label"] == "mystery"          # falls back to source id
    assert "trustClass" not in sig            # no dim row => no trust tier
    assert sig["provenance"] == "simulated"   # no Live data mode => simulated
    assert sig["statusTone"] == "over"        # Severe -> over


def test_severity_tone_mapping():
    def tone(sev: str) -> str:
        fact = {"ext_source_id": "webiq", "ext_signal_id": "s", "ext_severity": sev}
        return gold_rows_to_board_signals([fact], [_webiq_source()])[0]["statusTone"]

    assert tone("Severe") == "over"
    assert tone("Moderate") == "watch"
    assert tone("Minor") == "ok"
    assert tone("Unspecified") == "signal"


def test_web_citations_passed_through_as_list():
    cite = {"title": "Respiratory uptick", "uri": "https://example.invalid/a", "publishedAt": "2026-08-12T06:00:00Z", "snippet": "..."}
    fact = {**_webiq_fact(), "ext_web_citations": [cite]}
    [sig] = gold_rows_to_board_signals([fact], [_webiq_source()])
    assert sig["webCitations"] == [cite]


def test_web_citations_accepts_json_string():
    cite = {"title": "t", "uri": "https://example.invalid/b"}
    import json
    fact = {**_webiq_fact(), "ext_web_citations": json.dumps([cite])}
    [sig] = gold_rows_to_board_signals([fact], [_webiq_source()])
    assert sig["webCitations"] == [cite]


def test_no_web_citations_key_omits_field():
    [sig] = gold_rows_to_board_signals([_webiq_fact()], [_webiq_source()])
    assert "webCitations" not in sig
