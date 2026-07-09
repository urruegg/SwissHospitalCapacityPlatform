import unittest

from scripts.evidence.parsers.infra_parser import parse_infra
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_provenance,
    assert_valid,
)


class TestInfraParser(unittest.TestCase):
    def test_fixture_snapshot(self):
        rows = parse_infra(
            FIXTURE_REPO / "infra", repo_root=FIXTURE_REPO, source_commit=FIXED_COMMIT
        )
        assert_valid(rows, "deployed_bom")
        assert_provenance(rows)
        types = {r["resourceType"] for r in rows}
        self.assertIn("Microsoft.KeyVault/vaults", types)
        self.assertIn("Microsoft.Storage/storageAccounts", types)

    def test_module_path_is_repo_relative(self):
        rows = parse_infra(
            FIXTURE_REPO / "infra", repo_root=FIXTURE_REPO, source_commit=FIXED_COMMIT
        )
        self.assertTrue(all(r["modulePath"].startswith("infra/") for r in rows))

    def test_real_infra_snapshot(self):
        rows = parse_infra(REPO_ROOT / "infra", repo_root=REPO_ROOT, source_commit=FIXED_COMMIT)
        assert_valid(rows, "deployed_bom")
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
