"""Tests for the app evidence-fixture generator (Sprint 14.1 · T5).

Asserts the generated dataset that the Fluent app imports:

* satisfies the Evidence-tab card contract (>=25 BOM, >=10 ADR, >=1 PRD-req),
* stamps provenance (``sourceUrl`` + ``asOf``) on every card, and
* is byte-stable (regeneration is deterministic — the committed
  ``evidence-demo.json`` must match a fresh build).

Dependency-free apart from PyYAML (already an evidence-parser dependency). Run::

    python -m unittest scripts.evidence.tests.test_app_fixture
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.evidence.build_app_fixture import DEFAULT_OUT, build_dataset, write_dataset

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestAppFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = build_dataset(REPO_ROOT)

    def test_card_contract_counts(self):
        self.assertGreaterEqual(len(self.dataset["boms"]), 25)
        self.assertGreaterEqual(len(self.dataset["adrs"]), 10)
        self.assertGreaterEqual(len(self.dataset["requirements"]), 1)
        self.assertGreaterEqual(len(self.dataset["dependencies"]), 1)

    def test_every_card_has_provenance(self):
        groups = ("boms", "adrs", "requirements", "gaEvidence", "dependencies")
        for group in groups:
            for card in self.dataset[group]:
                prov = card["provenance"]
                self.assertTrue(prov.get("sourceUrl"), f"{group} card missing sourceUrl")
                self.assertTrue(prov.get("asOf"), f"{group} card missing asOf")

    def test_readiness_present_per_bom(self):
        for bom in self.dataset["boms"]:
            self.assertIn("tShow", bom["readiness"])
            self.assertIn("tProd", bom["readiness"])
            self.assertIn(bom["readiness"]["tShow"]["status"], {"Ready", "Blocked"})

    def test_no_phi_identifiers(self):
        # The dataset is derived purely from governance docs (PRD/ADR/BOM), which
        # carry no PHI. Guard against actual PHI markers/values — not domain words
        # like "inpatient(s)" that legitimately appear in requirement titles.
        import re

        blob = json.dumps(self.dataset).lower()
        for token in ("geburtsdatum", "ssn"):
            self.assertNotIn(token, blob)
        # Swiss AHV/social-security number (756.xxxx.xxxx.xx) must never appear.
        self.assertIsNone(re.search(r"756\.\d{4}\.\d{4}\.\d{2}", blob))

    def test_committed_fixture_matches_regen(self):
        committed = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
        self.assertEqual(
            committed,
            self.dataset,
            "evidence-demo.json is stale — run `python -m scripts.evidence.build_app_fixture`",
        )

    def test_byte_stable(self):
        second = build_dataset(REPO_ROOT)
        self.assertEqual(json.dumps(self.dataset, sort_keys=True), json.dumps(second, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
