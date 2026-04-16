"""Tests for refget tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.refget_tools import (
    get_refget_metadata,
    get_refget_sequence,
    get_refget_service_info,
)

REFGET_URL = "https://refget.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_refget_service_info(ctx):
    respx.get(f"{REFGET_URL}/sequence/service-info").mock(
        return_value=httpx.Response(200, json={"service": {"circular_supported": True, "algorithms": ["md5", "ga4gh"]}})
    )
    result = json.loads(await get_refget_service_info(ctx, REFGET_URL))
    assert result["service"]["circular_supported"] is True


@respx.mock
async def test_get_refget_service_info_connection_error(ctx):
    respx.get(f"{REFGET_URL}/sequence/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_refget_service_info(ctx, REFGET_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_get_refget_metadata(ctx):
    seq_id = "6681ac2f62509cfc220d78751b8dc524"
    respx.get(f"{REFGET_URL}/sequence/{seq_id}/metadata").mock(
        return_value=httpx.Response(200, json={"metadata": {"md5": seq_id, "length": 248956422}})
    )
    result = json.loads(await get_refget_metadata(ctx, REFGET_URL, seq_id))
    assert result["metadata"]["length"] == 248956422


@respx.mock
async def test_get_refget_metadata_not_found(ctx):
    respx.get(f"{REFGET_URL}/sequence/nope/metadata").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_refget_metadata(ctx, REFGET_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_refget_sequence(ctx):
    seq_id = "6681ac2f62509cfc220d78751b8dc524"
    respx.get(f"{REFGET_URL}/sequence/{seq_id}").mock(
        return_value=httpx.Response(200, text="ACGTACGT", headers={"content-type": "text/vnd.ga4gh.refget.v2.0.0+plain"})
    )
    result = json.loads(await get_refget_sequence(ctx, REFGET_URL, seq_id, start=0, end=8))
    assert result["sequence"] == "ACGTACGT"
    assert result["sequence_id"] == seq_id


@respx.mock
async def test_get_refget_sequence_range_error(ctx):
    seq_id = "6681ac2f62509cfc220d78751b8dc524"
    respx.get(f"{REFGET_URL}/sequence/{seq_id}").mock(return_value=httpx.Response(416, json={}))
    result = json.loads(await get_refget_sequence(ctx, REFGET_URL, seq_id, start=999999999, end=1000000000))
    assert result["error"]["code"] == "INVALID_REQUEST"


@respx.mock
async def test_get_refget_sequence_not_found(ctx):
    respx.get(f"{REFGET_URL}/sequence/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_refget_sequence(ctx, REFGET_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


def test_refget_register_returns_3_tools():
    from ga4gh_mcp.tools.refget_tools import register
    assert len(register()) == 3
