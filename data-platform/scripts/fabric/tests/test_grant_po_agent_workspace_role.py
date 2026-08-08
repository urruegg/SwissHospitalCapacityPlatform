import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from grant_po_agent_workspace_role import ensure_role_assignment


class _FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def read(self):
        return self._body


def test_skips_when_principal_already_has_a_role():
    calls = []

    def fake_get(method, url, token):
        calls.append((method, url))
        return _FakeResponse(200, {"value": [{"principal": {"id": "po-mi-123"}, "role": "Viewer"}]})

    def fake_post(method, url, token, body=None):
        raise AssertionError("must not POST when a role already exists")

    result = ensure_role_assignment(
        workspace_id="f3af9733-9503-4e92-98f9-a901d96f1c87",
        principal_id="po-mi-123",
        role="Viewer",
        token="fake-token",
        http_get=fake_get,
        http_post=fake_post,
    )
    assert result == "already-granted"
    assert len(calls) == 1


def test_grants_role_when_missing():
    posted = {}

    def fake_get(method, url, token):
        return _FakeResponse(200, {"value": [{"principal": {"id": "someone-else"}, "role": "Viewer"}]})

    def fake_post(method, url, token, body=None):
        posted["url"] = url
        posted["body"] = body
        return _FakeResponse(201, {})

    result = ensure_role_assignment(
        workspace_id="f3af9733-9503-4e92-98f9-a901d96f1c87",
        principal_id="po-mi-123",
        role="Viewer",
        token="fake-token",
        http_get=fake_get,
        http_post=fake_post,
    )
    assert result == "granted"
    assert posted["body"]["principal"]["id"] == "po-mi-123"
    assert posted["body"]["role"] == "Viewer"
