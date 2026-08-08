"""Sprint 43 WS-2 -- live Fabric Gold table reads via direct OneLake access.

Reads Gold Delta tables directly from OneLake (bypasses the Fabric SQL
analytics endpoint, which lags and is not authoritative -- see
``data-platform/scripts/fabric/read_gold_evidence.py``, the proven pattern
this class mirrors).

Confirmed live contract (Sprint 43 WS-2 spike, 2026-08-08):
  URI: abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables/{schema}/{name}
  Auth: Bearer token, scope https://storage.azure.com/.default
  Read: DeltaTable(uri, storage_options={"bearer_token": token,
        "use_fabric_endpoint": "true"}), then transpose
        .to_pyarrow_table().to_pydict() into row dicts.

Missing tables are a genuine upstream data gap (6 of the 12 tables this
platform's manifests reference do not exist yet in the SIT lakehouse) --
``query()`` catches any read failure and returns ``[]``, matching
``FabricAdapter``'s existing graceful-miss behavior for unrecognized
tables. This is not error suppression for its own sake: a missing Gold
table should read as "no grounding available", the same as it does today.

Token provider and table reader are injected (mirrors
``tools/fabric_data_agent_client.py`` and
``orchestrator/foundry_chat_model.py``) so this class is unit-testable
without cloud access.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

_STORAGE_SCOPE = "https://storage.azure.com/.default"
_ONELAKE_HOST = "onelake.dfs.fabric.microsoft.com"

logger = logging.getLogger(__name__)


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token(_STORAGE_SCOPE).token


def _default_table_reader(uri: str, token: str) -> list[dict[str, Any]]:
    from deltalake import DeltaTable

    dt = DeltaTable(uri, storage_options={"bearer_token": token, "use_fabric_endpoint": "true"})
    pydict = dt.to_pyarrow_table().to_pydict()
    if not pydict:
        return []
    columns = list(pydict.keys())
    row_count = len(next(iter(pydict.values())))
    return [{col: pydict[col][i] for col in columns} for i in range(row_count)]


class FabricDeltaClient:
    """Reads Gold (or any schema) Delta tables directly from OneLake."""

    def __init__(
        self,
        workspace_id: str,
        lakehouse_id: str,
        token_provider: Callable[[], str] = _default_token_provider,
        table_reader: Callable[[str, str], list[dict[str, Any]]] = _default_table_reader,
    ):
        self._workspace_id = workspace_id
        self._lakehouse_id = lakehouse_id
        self._token_provider = token_provider
        self._table_reader = table_reader

    def query(self, table: str) -> list[dict[str, Any]]:
        schema, sep, name = table.partition(".")
        if not sep or not name:
            raise ValueError(f"expected 'schema.table', got {table!r}")
        uri = (
            f"abfss://{self._workspace_id}@{_ONELAKE_HOST}/"
            f"{self._lakehouse_id}/Tables/{schema}/{name}"
        )
        token = self._token_provider()
        try:
            return self._table_reader(uri, token)
        except Exception:
            logger.warning("Fabric Gold table '%s' unavailable; returning no grounding", table)
            return []
