"""Gold-contract snapshot + parity regression for the org/skills expansion.

Sprint 23 WS-C3. The capacity-dashboard gold contract is *derived* from the
Direct-Lake (non-``bva_*``, non-``mode: import``) TMDL tables by
``verify_gold_schema.contract_tables``. Sprint 23 added the org spine
(WS-C1: ``dim_org_unit``, ``dim_department``) and the skills domain
(WS-C2: ``dim_care_setting``, ``dim_skill``, ``fact_skill_demand``,
``fact_skill_gap``, ``fact_skill_assertion``,
``bridge_worker_unit_eligibility``) to that model.

These tests lock the derived contract so a table cannot be silently dropped,
prove the new org/skills tables are part of the contract, and prove the parity
checker passes against the committed WS-B4 *target* gold set
(``fixtures/gold_tables_target.txt``). The parity run against the *live*
Fabric gold (via ``fabric/list_gold_tables.py``) is deferred to WS-B4, which
must produce these tables before a live Direct-Lake refresh.
"""
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_gold_schema.py"
spec = importlib.util.spec_from_file_location("verify_gold_schema", MODULE_PATH)
vgs = importlib.util.module_from_spec(spec)
sys.modules["verify_gold_schema"] = vgs
spec.loader.exec_module(vgs)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gold_tables_target.txt"

# Full derived gold contract after Sprint 23 WS-C1 + WS-C2. Any add/remove to
# the Direct-Lake TMDL tables must consciously update this snapshot.
EXPECTED_CONTRACT = frozenset({
    "bed_assignment",
    "bridge_worker_unit_eligibility",
    "dim_care_setting",
    "dim_department",
    "dim_disease",
    "dim_drg",
    "dim_hospital",
    "dim_hospital_service",
    "dim_org_unit",
    "dim_skill",
    "dim_specialty",
    "dim_treatment",
    "dim_ward_capacityunit",
    "encounter",
    "fact_capacity_baseline",
    "fact_skill_assertion",
    "fact_skill_demand",
    "fact_skill_gap",
    "map_disease_treatment_specialty_service",
    "or_case",
    "or_schedule",
})

# The tables Sprint 23 added to the gold contract (WS-C1 org spine + WS-C2 skills).
WSC_ORG_SKILLS_TABLES = frozenset({
    "dim_org_unit",
    "dim_department",
    "dim_care_setting",
    "dim_skill",
    "fact_skill_demand",
    "fact_skill_gap",
    "fact_skill_assertion",
    "bridge_worker_unit_eligibility",
})


def _real_contract() -> set:
    return vgs.contract_tables(vgs.TABLES_DIR)


def _target_set() -> set:
    return {ln.strip() for ln in FIXTURE.read_text(encoding="utf-8").splitlines() if ln.strip()}


def test_contract_matches_snapshot():
    assert _real_contract() == set(EXPECTED_CONTRACT)


def test_wsc_org_skills_tables_in_contract():
    assert WSC_ORG_SKILLS_TABLES <= _real_contract()


def test_skills_measures_excluded_import_mode():
    # skills_measures is a calculated (mode: import) holder, not a gold Delta table.
    assert "skills_measures" not in _real_contract()


def test_parity_passes_against_target_fixture():
    # Offline analog of `verify_gold_schema.py --produced <target>`: the WS-B4
    # target gold set must cover the derived contract with nothing missing.
    assert vgs.missing_tables(_real_contract(), _target_set()) == set()


def test_target_fixture_matches_snapshot():
    # The committed target list is the canonical WS-B4 gold set; keep it in sync.
    assert _target_set() == set(EXPECTED_CONTRACT)
