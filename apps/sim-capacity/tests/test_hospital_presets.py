import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.hospital_presets import HospitalPreset, load_preset


def test_usz_preset_loads():
    p = load_preset("USZ")
    assert isinstance(p, HospitalPreset)
    assert p.hospital_id == "H_USZ"
    assert p.stationary_cases_yr == 41151
    assert p.beds_quality == "inferred"
    assert p.inferred_bed_count is not None  # ~950 per design spec §4.5


def test_luks_preset_loads():
    p = load_preset("LUKS")
    assert p.beds == 839
    assert p.beds_quality == "explicit"
    assert p.staff == 8628


def test_szb_preset_loads():
    p = load_preset("SZB")
    assert p.beds == 174
    assert p.canton == "ZH"
    assert p.staff == 1200


def test_hsl_preset_raises_deferred():
    with pytest.raises(ValueError, match="deferred"):
        load_preset("HSL")


def test_unknown_preset_raises():
    with pytest.raises(KeyError):
        load_preset("XYZ")
