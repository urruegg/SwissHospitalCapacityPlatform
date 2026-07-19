import csv
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_master_data.py"
spec = importlib.util.spec_from_file_location("validate_master_data", MODULE_PATH)
vmd = importlib.util.module_from_spec(spec)
sys.modules["validate_master_data"] = vmd
spec.loader.exec_module(vmd)


def _write(dirpath, name, header, rows):
    with (dirpath / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _good_capacity(tmp):
    cap = tmp / "capacity"
    cap.mkdir(parents=True)
    _write(cap, "01_dim_hospital.csv", ["hospital_id", "name"], [["H1", "Alpha"]])
    _write(cap, "04_dim_disease.csv", ["disease_id", "name_de"], [["D1", "X"]])
    _write(cap, "02_dim_specialty.csv", ["specialty_hospital_id", "hospital_id", "specialty_id"], [["S1", "H1", "SP1"]])
    _write(cap, "03_dim_hospital_service.csv", ["service_id", "hospital_id"], [["SV1", "H1"]])
    _write(cap, "05_dim_treatment.csv", ["treatment_id", "disease_id"], [["T1", "D1"]])
    _write(cap, "06_dim_drg.csv", ["drg_code", "disease_id"], [["G1", "D1"]])
    _write(cap, "07_dim_ward_capacityunit.csv", ["ward_id", "hospital_id"], [["W1", "H1"]])
    _write(cap, "08_fact_capacity_baseline.csv", ["hospital_id", "metric", "value"], [["H1", "beds", "10"]])
    _write(cap, "09_map_disease_treatment_specialty_service.csv",
           ["map_id", "hospital_id", "disease_id", "treatment_id", "drg_code", "capacity_unit_ward_id"],
           [["M1", "H1", "D1", "T1", "G1", "W1"]])
    return cap


def test_valid_capacity_passes(tmp_path):
    cap = _good_capacity(tmp_path)
    errors = vmd.validate_capacity(cap)
    assert errors == []


def test_duplicate_pk_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    _write(cap, "01_dim_hospital.csv", ["hospital_id", "name"], [["H1", "Alpha"], ["H1", "Dup"]])
    errors = vmd.validate_capacity(cap)
    assert any("duplicate" in e.lower() and "hospital_id" in e for e in errors)


def test_broken_fk_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    _write(cap, "08_fact_capacity_baseline.csv", ["hospital_id", "metric", "value"], [["H_MISSING", "beds", "10"]])
    errors = vmd.validate_capacity(cap)
    assert any("H_MISSING" in e for e in errors)


def test_missing_file_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    (cap / "06_dim_drg.csv").unlink()
    errors = vmd.validate_capacity(cap)
    assert any("06_dim_drg.csv" in e for e in errors)
