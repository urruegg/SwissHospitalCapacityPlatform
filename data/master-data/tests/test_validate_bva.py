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


def _good_bva(tmp):
    bva = tmp / "bva"
    tenant = tmp / "curavias-org-skills"
    bva.mkdir(parents=True)
    tenant.mkdir(parents=True)

    _write(
        tenant,
        "dim_tenant.csv",
        ["tenant_id", "tenant_name"],
        [["CN", "CuraNova"], ["CP", "Curalp"], ["VT", "Vialta"]],
    )
    _write(
        bva,
        "bva_cost_element.csv",
        ["element_id", "cost_type", "element_name", "amount_chf", "driver_source"],
        [
            ["ot-build", "one_time", "MVP design/engineering/integration build", "640000", "bva_team_effort"],
            ["ot-security", "one_time", "Security & compliance hardening", "180000", "bva_bom"],
            ["ot-data", "one_time", "Data onboarding & contract implementation", "220000", "bva_bom"],
            ["ot-training", "one_time", "Training, change adoption & hypercare", "120000", "bva_team_effort"],
            ["ot-contingency", "one_time", "Program contingency reserve", "140000", "bva_cost_element"],
            ["run-azure", "annual_run", "Azure & platform service consumption", "760000", "bva_azure_cost_weekly"],
            ["run-ops", "annual_run", "Operations, support & reliability engineering", "260000", "bva_team_effort"],
            [
                "run-secops",
                "annual_run",
                "Security operations, audit evidence & compliance cadence",
                "140000",
                "bva_team_effort",
            ],
            ["run-monitoring", "annual_run", "Model monitoring & continuous evaluation", "90000", "bva_copilot_usage_weekly"],
        ],
    )
    _write(
        bva,
        "bva_hospital_profile.csv",
        ["tenant_id", "hospital_name", "beds", "occupancy_target", "archetype"],
        [
            ["CN", "CuraNova University Hospital", "920", "0.86", "acute"],
            ["CP", "Curalp Cantonal Hospital", "780", "0.84", "acute"],
            ["VT", "Vialta Regional Hospital", "190", "0.82", "rehab"],
        ],
    )
    _write(
        bva,
        "bva_bom.csv",
        ["resource_type", "resource_group", "env", "resource_id"],
        [
            ["resource-group", "rg-ihzhhpf-sit", "sit", "rg-ihzhhpf-sit"],
            ["fabric-capacity", "rg-ihzhhpf-sit", "sit", "fab-ihzhhpf-sit"],
            ["storage-account", "rg-ihzhhpf-sit", "sit", "stihzhhpfsit"],
            ["key-vault", "rg-ihzhhpf-prod", "prod", "kv-ihzhhpf-prod"],
            ["log-analytics", "rg-ihzhhpf-prod", "prod", "law-ihzhhpf-prod"],
            ["container-app", "rg-ihzhhpf-prod", "prod", "ca-ihzhhpf-prod"],
        ],
    )
    _write(
        bva,
        "bva_azure_cost_weekly.csv",
        ["service_name", "resource_group", "resource_id", "iso_week", "cost_usd"],
        [
            ["Microsoft Fabric", "rg-ihzhhpf-sit", "fab-ihzhhpf-sit", "2026-W20", "12400"],
            ["Storage", "rg-ihzhhpf-sit", "stihzhhpfsit", "2026-W20", "850"],
        ],
    )
    _write(
        bva,
        "bva_copilot_usage_weekly.csv",
        ["iso_week", "aiu", "tokens_in", "tokens_out", "cost_usd"],
        [["2026-W20", "320", "1800000", "420000", "2100"], ["2026-W21", "340", "1900000", "450000", "2230"]],
    )
    _write(
        bva,
        "bva_team_effort.csv",
        ["role", "iso_week", "elective_hours", "role_rate_chf"],
        [["Product Owner", "2026-W20", "24", "165"], ["Data Engineer", "2026-W20", "38", "155"]],
    )
    _write(bva, "bva_fx_rate.csv", ["period", "usd_to_chf"], [["2026-H1", "0.88"]])
    return bva, tenant


def test_valid_bva_passes(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    errors = vmd.validate_bva(bva, tenant)
    assert errors == []


def test_duplicate_pk_fails(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    _write(
        bva,
        "bva_cost_element.csv",
        ["element_id", "cost_type", "element_name", "amount_chf", "driver_source"],
        [
            ["ot-build", "one_time", "MVP design/engineering/integration build", "640000", "bva_team_effort"],
            ["ot-build", "one_time", "Duplicate build", "660000", "bva_team_effort"],
            ["run-azure", "annual_run", "Azure & platform service consumption", "1250000", "bva_azure_cost_weekly"],
        ],
    )
    errors = vmd.validate_bva(bva, tenant)
    assert any("duplicate" in e.lower() and "element_id" in e for e in errors)


def test_broken_fk_fails(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    _write(
        bva,
        "bva_hospital_profile.csv",
        ["tenant_id", "hospital_name", "beds", "occupancy_target", "archetype"],
        [["ZZ", "Unknown Hospital", "100", "0.80", "acute"]],
    )
    errors = vmd.validate_bva(bva, tenant)
    assert any("ZZ" in e for e in errors)


def test_missing_file_fails(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    (bva / "bva_fx_rate.csv").unlink()
    errors = vmd.validate_bva(bva, tenant)
    assert any("bva_fx_rate.csv" in e for e in errors)


def test_ledger_must_sum_to_rom(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    _write(
        bva,
        "bva_cost_element.csv",
        ["element_id", "cost_type", "element_name", "amount_chf", "driver_source"],
        [
            ["ot-build", "one_time", "MVP design/engineering/integration build", "640001", "bva_team_effort"],
            ["ot-security", "one_time", "Security & compliance hardening", "180000", "bva_bom"],
            ["ot-data", "one_time", "Data onboarding & contract implementation", "220000", "bva_bom"],
            ["ot-training", "one_time", "Training, change adoption & hypercare", "120000", "bva_team_effort"],
            ["ot-contingency", "one_time", "Program contingency reserve", "140000", "bva_cost_element"],
            ["run-azure", "annual_run", "Azure & platform service consumption", "760000", "bva_azure_cost_weekly"],
            ["run-ops", "annual_run", "Operations, support & reliability engineering", "260000", "bva_team_effort"],
            [
                "run-secops",
                "annual_run",
                "Security operations, audit evidence & compliance cadence",
                "140000",
                "bva_team_effort",
            ],
            ["run-monitoring", "annual_run", "Model monitoring & continuous evaluation", "90000", "bva_copilot_usage_weekly"],
        ],
    )
    errors = vmd.validate_bva(bva, tenant)
    assert any("ledger" in e.lower() and "ROM" in e for e in errors)


def test_bad_archetype_fails(tmp_path):
    bva, tenant = _good_bva(tmp_path)
    _write(
        bva,
        "bva_hospital_profile.csv",
        ["tenant_id", "hospital_name", "beds", "occupancy_target", "archetype"],
        [["CN", "CuraNova University Hospital", "920", "0.86", "foo"]],
    )
    errors = vmd.validate_bva(bva, tenant)
    assert any("archetype" in e and "foo" in e for e in errors)
