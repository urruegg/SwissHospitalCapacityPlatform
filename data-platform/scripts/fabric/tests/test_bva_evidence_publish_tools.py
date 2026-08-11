"""Sprint 44 follow-up: BVA evidence notebook + semantic model publish tooling."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

FABRIC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, FABRIC_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


notebook_mod = _load("publish_bva_evidence_notebook")
tmdl_mod = _load("generate_bva_evidence_tmdl")
sm_mod = _load("publish_sm_bva")


# ---------------------------------------------------------------------------
# publish_bva_evidence_notebook.py
# ---------------------------------------------------------------------------

def test_build_notebook_source_embeds_transform_module_verbatim():
    source = notebook_mod.build_notebook_source("LH_ID", "lh_name", "WS_ID")
    transform_code = notebook_mod.TRANSFORM_MODULE.read_text(encoding="utf-8")
    assert transform_code in source


def test_build_notebook_source_has_lakehouse_metadata_and_two_cells():
    source = notebook_mod.build_notebook_source("LH_ID", "lh_name", "WS_ID")
    assert '"default_lakehouse": "LH_ID"' in source
    assert '"default_lakehouse_name": "lh_name"' in source
    assert '"default_lakehouse_workspace_id": "WS_ID"' in source
    assert source.count("# CELL ********************") == 2


def test_build_notebook_source_cell2_reads_master_and_writes_gold():
    source = notebook_mod.build_notebook_source("LH_ID", "lh_name", "WS_ID")
    assert "build_evidence_gold_tables(Path(MASTER))" in source
    assert 'saveAsTable(f"gold.{name}")' in source


def test_publish_dry_run_lists_every_part_without_network(capsys):
    notebook_mod.publish("WS_ID", "LH_ID", "lh_name", dry_run=True)
    out = capsys.readouterr().out
    assert "[DRY-RUN] Would publish build_gold_bva_evidence" in out


# ---------------------------------------------------------------------------
# generate_bva_evidence_tmdl.py
# ---------------------------------------------------------------------------

def test_build_tmdl_marks_known_numeric_columns_as_double():
    tmdl = tmdl_mod.build_tmdl("fact_build_cost_actual")
    # amount_chf is numeric per _NUMERIC_COLUMNS -> dataType double.
    idx = tmdl.index("column amount_chf")
    assert "dataType: double" in tmdl[idx: idx + 120]


def test_build_tmdl_marks_id_column_as_string():
    tmdl = tmdl_mod.build_tmdl("fact_build_cost_actual")
    idx = tmdl.index("column build_cost_id")
    assert "dataType: string" in tmdl[idx: idx + 120]


def test_build_tmdl_uses_the_gold_table_name_and_direct_lake_partition():
    tmdl = tmdl_mod.build_tmdl("fact_build_cost_actual")
    assert "table bva_evidence_build_cost_actual_fact" in tmdl
    assert "mode: directLake" in tmdl
    assert "schemaName: gold" in tmdl
    assert "entityName: bva_evidence_build_cost_actual_fact" in tmdl


def test_build_tmdl_column_order_matches_the_real_csv_header():
    tmdl = tmdl_mod.build_tmdl("fact_roi_scenario")
    header = tmdl_mod._read_header("fact_roi_scenario")
    # Trailing newline disambiguates prefix-overlapping names, e.g.
    # "column scenario" is itself a substring of "column scenario_id".
    positions = [tmdl.index(f"column {col}\n") for col in header]
    assert positions == sorted(positions)


def test_every_master_file_stem_has_a_gold_table_name_and_numeric_entry():
    for stem in tmdl_mod._GOLD_TABLE_NAMES:
        assert stem in tmdl_mod._NUMERIC_COLUMNS
        assert stem in tmdl_mod._DESCRIPTIONS


# ---------------------------------------------------------------------------
# publish_sm_bva.py
# ---------------------------------------------------------------------------

def test_collect_parts_finds_every_committed_tmdl_and_platform_file():
    parts = sm_mod.collect_parts()
    paths = {p["path"] for p in parts}
    assert ".platform" in paths
    assert "definition.pbism" in paths
    assert "definition/model.tmdl" in paths
    assert "definition/tables/bva_evidence_build_cost_actual_fact.tmdl" in paths
    assert "definition/roles/BvaReadOnly.tmdl" in paths


def test_collect_parts_paths_use_forward_slashes_only():
    parts = sm_mod.collect_parts()
    assert all("\\" not in p["path"] for p in parts)


def test_model_tmdl_registers_every_evidence_table():
    model_text = (sm_mod.MODEL_DIR / "definition" / "model.tmdl").read_text(encoding="utf-8")
    for gold_name in tmdl_mod._GOLD_TABLE_NAMES.values():
        assert f"ref table {gold_name}" in model_text
