"""Sprint 43 WS-5 -- citations must reflect tables that actually returned
grounding rows, not every table configured in the manifest.

Found via live UI verification (2026-08-09): with WS-2's real Fabric read
blocked (pending a Fabric Administrator tenant-setting change), every
configured table returns ``[]``, yet the citations footer still listed all of
them (e.g. "Quellen: gold.or_schedule, gold.anaesthesia_status,
gold.staff_availability" for orsa-agent) even though the model's own prose
said it had no access to that data. A citation that names a source which
contributed zero rows is misleading -- exactly the fabrication risk the
platform's honesty contract is designed to prevent.
"""

from __future__ import annotations

from manifests.loader import AgentManifest
from orchestrator.dispatch import Orchestrator
from tools.fabric_adapter import FabricAdapter


class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return "stub answer"


def _manifest(tables: tuple[str, ...]) -> AgentManifest:
    return AgentManifest(
        agent="orsa-agent",
        version="1.0.0",
        runtime="agent-host",
        model_deployment_ref="gpt-5",
        system_prompt_ref="AGENT.md",
        grounding_tables=tables,
    )


def test_citations_exclude_tables_that_returned_no_rows():
    # gold.bed_assignment is in FabricAdapter's synthetic sample (non-empty);
    # gold.or_schedule is not configured there, so the default adapter
    # returns [] for it -- exactly the shape of a live-but-blocked read.
    fabric = FabricAdapter()
    orch = Orchestrator(chat_model=_StubModel(), fabric=fabric)

    reply = orch.dispatch(
        _manifest(("gold.bed_assignment", "gold.or_schedule")),
        "sys",
        "question",
        conversation_id="c1",
        caller_oid="oid1",
    )

    assert "gold.bed_assignment" in reply.citations
    assert "gold.or_schedule" not in reply.citations


def test_citations_empty_when_every_table_returns_no_rows():
    fabric = FabricAdapter()
    orch = Orchestrator(chat_model=_StubModel(), fabric=fabric)

    reply = orch.dispatch(
        _manifest(("gold.or_schedule", "gold.anaesthesia_status")),
        "sys",
        "question",
        conversation_id="c1",
        caller_oid="oid1",
    )

    assert reply.citations == ()
