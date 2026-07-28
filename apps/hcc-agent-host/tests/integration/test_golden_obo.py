"""#424 M5 — integration test: OBO context flows into the golden RLS path.

With ``OBO_ENABLED=false`` (the SIT default) the golden read is unchanged from
M4 (simulated, deny-by-default). With OBO enabled and an injected exchange, the
endpoint must build a per-request RLS provider that *receives* the OBO token —
proven by the M4 ``FabricDataAgentRlsProvider`` refusal flipping from the
"without an OBO token" message to the M5 "dynamic-RLS TMDL pending" message.
No live Entra or Fabric.
"""

from __future__ import annotations

import pytest

from golden.rls import FabricDataAgentRlsProvider, RlsProviderError


def test_fabric_provider_without_obo_refuses_mi_scope():
    provider = FabricDataAgentRlsProvider(client=object(), obo_token=None)
    with pytest.raises(RlsProviderError) as exc:
        provider.scope([], hospital_scope="hospital-usz", user_oid="u1")
    assert "without an OBO token" in str(exc.value)


def test_fabric_provider_with_obo_reaches_tmdl_pending():
    # An OBO token is present → the MI-scope refusal no longer applies; the read
    # now blocks only on the deferred dynamic-RLS TMDL predicate (#510).
    provider = FabricDataAgentRlsProvider(client=object(), obo_token="obo-token-xyz")
    with pytest.raises(RlsProviderError) as exc:
        provider.scope([], hospital_scope="hospital-usz", user_oid="u1")
    message = str(exc.value)
    assert "OBO token present" in message
    assert "dynamic-RLS TMDL" in message
    assert "without an OBO token" not in message
