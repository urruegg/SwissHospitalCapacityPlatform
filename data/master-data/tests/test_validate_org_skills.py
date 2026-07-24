import csv
import importlib.util
import shutil
import sys
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_master_data.py"
spec = importlib.util.spec_from_file_location("validate_master_data", MODULE_PATH)
vmd = importlib.util.module_from_spec(spec)
sys.modules["validate_master_data"] = vmd
spec.loader.exec_module(vmd)


def _gln_with_check(body12: str) -> str:
    """Append the correct GS1 mod-10 check digit to a 12-digit body."""
    total = sum(int(ch) * (3 if i % 2 == 0 else 1) for i, ch in enumerate(reversed(body12)))
    return body12 + str((10 - (total % 10)) % 10)


def _copy_real(tmp_path):
    dest = tmp_path / "curavias-org-skills"
    shutil.copytree(vmd.ORG_SKILLS_DIR, dest)
    return dest


def _patch_first_cell(dir_path, filename, column, new_value):
    """Overwrite the first data row's ``column`` in ``filename`` with ``new_value``."""
    path = dir_path / filename
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    header = list(rows[0].keys())
    assert column in header, f"{column} not in {filename}"
    rows[0][column] = new_value
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


# --- gln_is_valid (pure function) -------------------------------------------

def test_gln_is_valid_accepts_correct_check_digit():
    assert vmd.gln_is_valid(_gln_with_check("760100100001")) is True


def test_gln_is_valid_rejects_bad_check_digit():
    good = _gln_with_check("760100100001")
    bad = good[:12] + str((int(good[12]) + 1) % 10)
    assert vmd.gln_is_valid(bad) is False


def test_gln_is_valid_rejects_non_13_digit():
    assert vmd.gln_is_valid("76010010000") is False
    assert vmd.gln_is_valid("7601001000012345") is False
    assert vmd.gln_is_valid("76010010000AB") is False


# --- happy path against the real, valid-by-construction CSVs -----------------

def test_real_org_skills_validate_clean():
    assert vmd.validate_org_skills(vmd.ORG_SKILLS_DIR) == []


# --- each rule catches an injected violation ---------------------------------

def test_out_of_domain_enum_fails(tmp_path):
    d = _copy_real(tmp_path)
    _patch_first_cell(d, "dim_org_unit.csv", "entity_type", "Bogus-Type")
    errors = vmd.validate_org_skills(d)
    assert any("entity_type" in e and "not in domain" in e for e in errors)


def test_dangling_foreign_key_fails(tmp_path):
    d = _copy_real(tmp_path)
    _patch_first_cell(d, "fact_skill_assertion.csv", "skill_id", "SK-DOES-NOT-EXIST")
    errors = vmd.validate_org_skills(d)
    assert any("SK-DOES-NOT-EXIST" in e and "dim_skill.csv" in e for e in errors)


def test_bad_worker_gln_fails(tmp_path):
    d = _copy_real(tmp_path)
    _patch_first_cell(d, "dim_employee.csv", "worker_gln", "7601009999999")
    errors = vmd.validate_org_skills(d)
    assert any("worker_gln" in e and "GLN mod-10" in e for e in errors)


def test_duplicate_primary_key_fails(tmp_path):
    d = _copy_real(tmp_path)
    path = d / "dim_tenant.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    header = list(rows[0].keys())
    rows.append(dict(rows[0]))  # duplicate the first tenant row wholesale
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)
    errors = vmd.validate_org_skills(d)
    assert any("duplicate primary key" in e for e in errors)


def test_load_order_violation_detected():
    # Reverse the declared load order so every FK parent loads after its child.
    reversed_order = list(reversed(vmd.ORG_SKILLS_LOAD_ORDER))
    with mock.patch.object(vmd, "ORG_SKILLS_LOAD_ORDER", reversed_order):
        errors = vmd.validate_org_skills(vmd.ORG_SKILLS_DIR)
    assert any(e.startswith("load-order:") for e in errors)
