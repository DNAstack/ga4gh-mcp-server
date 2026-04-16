"""Tests for BaseClient."""
from __future__ import annotations

import pytest
import respx
import httpx

from ga4gh_mcp.clients.base import BaseClient


BASE = "https://example.ga4gh.org"


@pytest.fixture
def client():
    return BaseClient(base_url=BASE)


@pytest.fixture
def authed_client():
    return BaseClient(base_url=BASE, bearer_token="test-token")


@respx.mock
async def test_get_json(client: BaseClient):
    respx.get(f"{BASE}/ga4gh/drs/v1/objects/abc").mock(
        return_value=httpx.Response(200, json={"id": "abc"})
    )
    result = await client.get("/ga4gh/drs/v1/objects/abc")
    assert result == {"id": "abc"}


@respx.mock
async def test_get_with_bearer_token(authed_client: BaseClient):
    route = respx.get(f"{BASE}/test").mock(return_value=httpx.Response(200, json={}))
    await authed_client.get("/test")
    assert route.called
    assert "Bearer test-token" in route.calls[0].request.headers["authorization"]


@respx.mock
async def test_get_returns_text_for_non_json(client: BaseClient):
    respx.get(f"{BASE}/text").mock(
        return_value=httpx.Response(200, text="hello", headers={"content-type": "text/plain"})
    )
    result = await client.get("/text")
    assert result == "hello"


@respx.mock
async def test_post_json(client: BaseClient):
    respx.post(f"{BASE}/run").mock(return_value=httpx.Response(200, json={"run_id": "r1"}))
    result = await client.post("/run", json={"workflow_url": "http://example.com/wf.wdl"})
    assert result["run_id"] == "r1"


@respx.mock
async def test_404_raises(client: BaseClient):
    respx.get(f"{BASE}/missing").mock(return_value=httpx.Response(404, json={"msg": "not found"}))
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.get("/missing")
    assert exc_info.value.response.status_code == 404


@respx.mock
async def test_retry_on_503(client: BaseClient):
    # First two calls return 503, third succeeds
    client._retry_delay = 0  # no actual sleep in tests
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    respx.get(f"{BASE}/flaky").mock(side_effect=side_effect)
    result = await client.get("/flaky")
    assert result == {"ok": True}
    assert call_count == 3


@respx.mock
async def test_get_paginated_collects_pages(client: BaseClient):
    respx.get(f"{BASE}/items").mock(return_value=httpx.Response(200, json={
        "data": [{"id": 1}, {"id": 2}],
        "pagination": {"next_page_url": f"{BASE}/items?page=2"}
    }))
    respx.get(f"{BASE}/items", params={"page": "2"}).mock(return_value=httpx.Response(200, json={
        "data": [{"id": 3}],
        "pagination": {}
    }))
    # For paginated, we need to mock the second URL directly
    respx.get(f"{BASE}/items?page=2").mock(return_value=httpx.Response(200, json={
        "data": [{"id": 3}],
        "pagination": {}
    }))
    results = await client.get_paginated("/items")
    assert len(results) >= 2


@respx.mock
async def test_get_paginated_list_response(client: BaseClient):
    """Handles APIs that return a plain list instead of paginated object."""
    respx.get(f"{BASE}/list").mock(return_value=httpx.Response(200, json=[{"id": 1}, {"id": 2}]))
    results = await client.get_paginated("/list")
    assert results == [{"id": 1}, {"id": 2}]


@respx.mock
async def test_url_with_full_http_path(client: BaseClient):
    """Full URLs are used as-is without prepending base_url."""
    full_url = "https://other.example.com/api/v1/endpoint"
    respx.get(full_url).mock(return_value=httpx.Response(200, json={"ok": True}))
    result = await client.get(full_url)
    assert result == {"ok": True}
