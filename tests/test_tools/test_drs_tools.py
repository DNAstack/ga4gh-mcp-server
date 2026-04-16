"""Tests for DRS tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.drs_tools import get_drs_access_url, get_drs_object, get_drs_service_info

DRS_URL = "https://drs.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


# --- get_drs_object ---

@respx.mock
async def test_get_drs_object_happy_path(ctx):
    respx.get(f"{DRS_URL}/ga4gh/drs/v1/objects/abc123").mock(
        return_value=httpx.Response(200, json={"id": "abc123", "size": 1024, "checksums": [{"checksum": "deadbeef", "type": "md5"}]})
    )
    result = json.loads(await get_drs_object(ctx, DRS_URL, "abc123"))
    assert result["id"] == "abc123"
    assert result["size"] == 1024


@respx.mock
async def test_get_drs_object_not_found(ctx):
    respx.get(f"{DRS_URL}/ga4gh/drs/v1/objects/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_drs_object(ctx, DRS_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"
    assert "nope" in result["error"]["message"]


@respx.mock
async def test_get_drs_object_auth_required(ctx):
    respx.get(f"{DRS_URL}/ga4gh/drs/v1/objects/secure").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await get_drs_object(ctx, DRS_URL, "secure"))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_drs_object_connection_error(ctx):
    respx.get(f"{DRS_URL}/ga4gh/drs/v1/objects/abc").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_drs_object(ctx, DRS_URL, "abc"))
    assert result["error"]["code"] == "CONNECTION_ERROR"


# --- get_drs_access_url ---

@respx.mock
async def test_get_drs_access_url_happy_path(ctx):
    respx.post(f"{DRS_URL}/ga4gh/drs/v1/objects/abc123/access/s3").mock(
        return_value=httpx.Response(200, json={"url": "https://s3.example.com/signed-url", "headers": {}})
    )
    result = json.loads(await get_drs_access_url(ctx, DRS_URL, "abc123", "s3"))
    assert "signed-url" in result["url"]


@respx.mock
async def test_get_drs_access_url_not_found(ctx):
    respx.post(f"{DRS_URL}/ga4gh/drs/v1/objects/abc/access/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_drs_access_url(ctx, DRS_URL, "abc", "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_drs_access_url_auth_required(ctx):
    respx.post(f"{DRS_URL}/ga4gh/drs/v1/objects/abc/access/s3").mock(return_value=httpx.Response(403, json={}))
    result = json.loads(await get_drs_access_url(ctx, DRS_URL, "abc", "s3"))
    assert result["error"]["code"] == "AUTH_REQUIRED"


# --- get_drs_service_info ---

@respx.mock
async def test_get_drs_service_info(ctx):
    respx.get(f"{DRS_URL}/service-info").mock(
        return_value=httpx.Response(200, json={"id": "drs-svc", "type": {"group": "org.ga4gh", "artifact": "drs", "version": "1.4.0"}})
    )
    result = json.loads(await get_drs_service_info(ctx, DRS_URL))
    assert result["type"]["artifact"] == "drs"


@respx.mock
async def test_get_drs_service_info_connection_error(ctx):
    respx.get(f"{DRS_URL}/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_drs_service_info(ctx, DRS_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


# --- register() ---

def test_drs_register_returns_3_tools():
    from ga4gh_mcp.tools.drs_tools import register
    tools = register()
    assert len(tools) == 3
    assert "get_drs_object" in tools
    assert "get_drs_access_url" in tools
    assert "get_drs_service_info" in tools
