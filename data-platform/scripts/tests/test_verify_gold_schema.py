import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_gold_schema.py"
spec = importlib.util.spec_from_file_location("verify_gold_schema", MODULE_PATH)
vgs = importlib.util.module_from_spec(spec)
sys.modules["verify_gold_schema"] = vgs
spec.loader.exec_module(vgs)


def test_parity_ok_when_superset():
    contract = {"dim_hospital", "fact_capacity_baseline"}
    produced = {"dim_hospital", "fact_capacity_baseline", "or_case"}
    missing = vgs.missing_tables(contract, produced)
    assert missing == set()


def test_parity_fails_when_missing():
    contract = {"dim_hospital", "fact_capacity_baseline"}
    produced = {"dim_hospital"}
    missing = vgs.missing_tables(contract, produced)
    assert missing == {"fact_capacity_baseline"}


def test_contract_excludes_bva(tmp_path):
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "dim_hospital.tmdl").write_text("table dim_hospital", encoding="utf-8")
    (tables / "bva_dim_hospital.tmdl").write_text("table bva_dim_hospital", encoding="utf-8")
    contract = vgs.contract_tables(tables)
    assert "dim_hospital" in contract
    assert "bva_dim_hospital" not in contract


def test_contract_excludes_import_mode(tmp_path):
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "dim_hospital.tmdl").write_text(
        "table dim_hospital\n\tpartition dim_hospital = entity\n\t\tmode: directLake\n",
        encoding="utf-8")
    (tables / "dim_persona.tmdl").write_text(
        "table dim_persona\n\tpartition dim_persona = m\n\t\tmode: import\n",
        encoding="utf-8")
    (tables / "param_capacity_measure.tmdl").write_text(
        "table param_capacity_measure\n\tpartition param_capacity_measure = calculated\n\t\tmode: import\n",
        encoding="utf-8")
    contract = vgs.contract_tables(tables)
    assert "dim_hospital" in contract
    assert "dim_persona" not in contract
    assert "param_capacity_measure" not in contract

