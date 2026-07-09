import unittest

from scripts.evidence.parsers.region_availability_parser import parse_region_availability
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_provenance,
    assert_valid,
)


class TestRegionParser(unittest.TestCase):
    def setUp(self):
        self.rows = parse_region_availability(
            FIXTURE_REPO / "docs" / "region-availability.yaml", source_commit=FIXED_COMMIT
        )

    def test_rows_valid_and_provenanced(self):
        assert_valid(self.rows, "region_availability")
        # verifiedBy + asOf are mandatory provenance for availability facts.
        assert_provenance(self.rows, keys=("sourcePath", "sourceCommit", "verifiedBy", "asOf"))

    def test_maturity_values(self):
        by_id = {r["bomId"]: r for r in self.rows}
        self.assertEqual(by_id["bom-sample-capacity"]["maturity"], "GA")
        self.assertEqual(by_id["bom-sample-lakehouse"]["maturity"], "Preview")

    def test_real_catalog_valid(self):
        rows = parse_region_availability(
            REPO_ROOT / "docs" / "region-availability.yaml", source_commit=FIXED_COMMIT
        )
        assert_valid(rows, "region_availability")
        assert_provenance(rows, keys=("verifiedBy", "asOf"))
        self.assertGreaterEqual(len(rows), 50)


if __name__ == "__main__":
    unittest.main()
