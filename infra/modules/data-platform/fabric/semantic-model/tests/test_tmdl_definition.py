import json
import re
from pathlib import Path

MODEL_ROOT = Path(__file__).parent.parent / "sm_capacity_data_product"
DEFINITION = MODEL_ROOT / "definition"


def _read(rel: str) -> str:
    return (MODEL_ROOT / rel).read_text(encoding="utf-8")


def test_platform_metadata_declares_semantic_model():
    obj = json.loads(_read(".platform"))
    assert obj["metadata"]["type"] == "SemanticModel"
    assert obj["metadata"]["displayName"] == "sm_capacity_data_product"
    assert obj["config"]["logicalId"], "logicalId must be set and stable"


def test_pbism_pointer_names_the_model():
    obj = json.loads(_read("definition.pbism"))
    assert obj["name"] == "sm_capacity_data_product"


def test_database_pins_tabular_compatibility_level():
    txt = _read("definition/database.tmdl")
    assert "database sm_capacity_data_product" in txt
    assert "compatibilityLevel: 1604" in txt


def test_model_references_the_one_table():
    txt = _read("definition/model.tmdl")
    assert "model Model" in txt
    assert "culture: en-US" in txt
    assert "ref table demand_encounter" in txt


def test_datasources_keep_substitutable_placeholders():
    txt = _read("definition/dataSources.tmdl")
    assert "[WORKSPACE_GUID]" in txt
    assert "[LAKEHOUSE_GUID]" in txt
    assert "onelake.dfs.fabric.microsoft.com" in txt


def test_table_binds_to_gold_demand_encounter():
    txt = _read("definition/tables/demand_encounter.tmdl")
    assert "mode: directLake" in txt
    assert "source = entity 'gold.demand_encounter'" in txt


def test_table_declares_episode_id_as_key():
    txt = _read("definition/tables/demand_encounter.tmdl")
    assert "column episode_id" in txt
    assert "isKey: true" in txt


def test_table_has_exactly_one_measure_named_encounter_count():
    txt = _read("definition/tables/demand_encounter.tmdl")
    measures = re.findall(r"^\s*measure\s+'([^']+)'", txt, flags=re.MULTILINE)
    assert measures == ["Encounter Count"], measures
    assert "COUNTROWS('demand_encounter')" in txt


def test_no_patient_id_in_any_tmdl_least_disclosure():
    for tmdl in DEFINITION.rglob("*.tmdl"):
        text = tmdl.read_text(encoding="utf-8")
        assert "patient_id" not in text, (
            f"{tmdl} exposes patient_id; semantic model must omit pseudonym per W1.4 "
            "least-disclosure stance (see README §Why patient_id is intentionally NOT exposed)"
        )
