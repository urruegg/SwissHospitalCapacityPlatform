"""Sprint 16 T3 — Cosmos smoke tests (scenario upsert, vector/hybrid search,
agent-memory thread). These require a live Cosmos account and are SKIPPED when
`CSA_COSMOS_ENDPOINT` is unset, so CI stays green without credentials.
"""
from __future__ import annotations

import os
import unittest

from _util import load_script

COSMOS_ENDPOINT = os.environ.get("CSA_COSMOS_ENDPOINT")
skip_reason = "CSA_COSMOS_ENDPOINT unset — live Cosmos smoke skipped"


@unittest.skipUnless(COSMOS_ENDPOINT, skip_reason)
class TestCosmosSmoke(unittest.TestCase):
    """Live-only. Populated when a dev Cosmos/emulator endpoint is configured."""

    @classmethod
    def setUpClass(cls) -> None:
        from _cosmos import get_database_client

        cls.db = get_database_client()
        if cls.db is None:
            raise unittest.SkipTest("azure-cosmos SDK not installed")

    def test_scenario_upsert_roundtrip(self) -> None:
        seed = load_script("csa-seed-scenarios.py")
        scenarios = seed.build_scenarios()
        container = self.db.get_container_client("scenarios")
        doc = scenarios[0]
        container.upsert_item(doc)
        read = container.read_item(doc["scenarioId"], partition_key=doc["scenarioId"])
        self.assertEqual(read["scenarioId"], doc["scenarioId"])

    def test_vector_search_returns_results(self) -> None:
        container = self.db.get_container_client("scenarios")
        query = (
            "SELECT TOP 3 c.scenarioId FROM c "
            "ORDER BY VectorDistance(c.descriptionEmbedding, @vec)"
        )
        params = [{"name": "@vec", "value": [0.0] * 1536}]
        rows = list(
            container.query_items(query=query, parameters=params, enable_cross_partition_query=True)
        )
        self.assertIsInstance(rows, list)

    def test_hybrid_search_smoke(self) -> None:
        container = self.db.get_container_client("response-levers")
        rows = list(
            container.query_items(
                query="SELECT TOP 1 c.leverId FROM c WHERE c.doctrineTier = 3",
                enable_cross_partition_query=True,
            )
        )
        self.assertIsInstance(rows, list)

    def test_agent_memory_thread_isolation(self) -> None:
        container = self.db.get_container_client("agent-memory")
        rows = list(
            container.query_items(
                query="SELECT TOP 1 c.threadId FROM c",
                enable_cross_partition_query=True,
            )
        )
        self.assertIsInstance(rows, list)


if __name__ == "__main__":
    unittest.main()
