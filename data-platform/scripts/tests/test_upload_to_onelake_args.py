import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "upload_to_onelake.py"
spec = importlib.util.spec_from_file_location("upload_to_onelake", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["upload_to_onelake"] = mod
spec.loader.exec_module(mod)


def test_parse_args_requires_ids():
    ns = mod.parse_args([
        "--workspace-id", "WS", "--lakehouse-id", "LH",
        "--source-root", "data/master-data/capacity", "--target", "master-data/capacity",
    ])
    assert ns.workspace_id == "WS"
    assert ns.lakehouse_id == "LH"
    assert ns.source_root == "data/master-data/capacity"
    assert ns.target == "master-data/capacity"
