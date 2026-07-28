"""Sprint 30 — app <-> IaC parity for the agent-host Cosmos containers.

Locks the drift found after Sprint 30: the app persists to the
``agent_interactions`` container (``persistence.cosmos_client``), but the
Bicep module ``infra/modules/agent-host/cosmos.bicep`` must actually provision
every container the app writes to, each with the matching partition key. Without
this test the capture sink can silently be absent in a deployed environment.
"""

from __future__ import annotations

import re
from pathlib import Path

from persistence.cosmos_client import CONTAINERS, PARTITION_KEYS

REPO_ROOT = Path(__file__).resolve().parents[4]
COSMOS_BICEP = REPO_ROOT / "infra" / "modules" / "agent-host" / "cosmos.bicep"


def _declared_containers() -> dict[str, str]:
    """Parse ``name: 'X' ... partitionKey: '/Y'`` pairs from the containers var."""
    text = COSMOS_BICEP.read_text(encoding="utf-8")
    pairs = re.findall(
        r"name:\s*'([^']+)'\s*partitionKey:\s*'/([^']+)'",
        text,
    )
    return {name: pk for name, pk in pairs}


def test_bicep_declares_every_app_container_with_matching_partition_key():
    declared = _declared_containers()
    for container in CONTAINERS:
        assert container in declared, (
            f"container '{container}' is written by the app but not provisioned "
            f"in cosmos.bicep (declared: {sorted(declared)})"
        )
        assert declared[container] == PARTITION_KEYS[container], (
            f"container '{container}' partition key mismatch: bicep declares "
            f"'/{declared[container]}' but app expects '/{PARTITION_KEYS[container]}'"
        )
