"""Tests for Data Connect tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.data_connect_tools import (
    get_data_connect_service_info,
    get_data_connect_table_data,
    get_data_connect_table_info,
    list_data_connect_tables,
    query_data_connect,
)

DC_URL = "https://data-connect.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_data_connect_service_info(ctx):
    respx.get(f"{DC_URL}/service-info").mock(
        return_value=httpx.Response(200, json={"id": "dc-svc", "name": "Example Data Connect"})
    )
    result = json.loads(await get_data_connect_service_info(ctx, DC_URL))
    assert result["id"] == "dc-svc"


@respx.mock
async def test_get_data_connect_service_info_connection_error(ctx):
    respx.get(f"{DC_URL}/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_data_connect_service_info(ctx, DC_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_list_data_connect_tables(ctx):
    respx.get(f"{DC_URL}/tables").mock(
        return_value=httpx.Response(200, json={"tables": [{"name": "public.samples"}, {"name": "public.variants"}]})
    )
    result = json.loads(await list_data_connect_tables(ctx, DC_URL))
    assert len(result) == 2
    assert result[0]["name"] == "public.samples"


@respx.mock
async def test_list_data_connect_tables_auth_error(ctx):
    respx.get(f"{DC_URL}/tables").mock(return_value=httpx.Response(403, json={}))
    result = json.loads(await list_data_connect_tables(ctx, DC_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_data_connect_table_info(ctx):
    respx.get(f"{DC_URL}/table/public.samples/info").mock(
        return_value=httpx.Response(200, json={
            "name": "public.samples",
            "data_model": {"$schema": "http://json-schema.org/draft-07/schema#", "properties": {"sample_id": {"type": "string"}}}
        })
    )
    result = json.loads(await get_data_connect_table_info(ctx, DC_URL, "public.samples"))
    assert result["name"] == "public.samples"
    assert "data_model" in result


@respx.mock
async def test_get_data_connect_table_info_not_found(ctx):
    respx.get(f"{DC_URL}/table/nope/info").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_data_connect_table_info(ctx, DC_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"
    assert "nope" in result["error"]["message"]


@respx.mock
async def test_get_data_connect_table_data(ctx):
    respx.get(f"{DC_URL}/table/public.samples/data").mock(
        return_value=httpx.Response(200, json={
            "data": [{"sample_id": "s1"}, {"sample_id": "s2"}],
            "pagination": {}
        })
    )
    result = json.loads(await get_data_connect_table_data(ctx, DC_URL, "public.samples"))
    assert result["data"][0]["sample_id"] == "s1"


@respx.mock
async def test_get_data_connect_table_data_not_found(ctx):
    respx.get(f"{DC_URL}/table/nope/data").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_data_connect_table_data(ctx, DC_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_query_data_connect(ctx):
    respx.post(f"{DC_URL}/search").mock(
        return_value=httpx.Response(200, json={
            "data": [{"sample_id": "s1", "phenotype": "epilepsy"}],
            "pagination": {}
        })
    )
    result = json.loads(await query_data_connect(
        ctx, DC_URL, "SELECT * FROM public.samples WHERE phenotype = 'epilepsy' LIMIT 10"
    ))
    assert result["data"][0]["phenotype"] == "epilepsy"


@respx.mock
async def test_query_data_connect_invalid_sql(ctx):
    respx.post(f"{DC_URL}/search").mock(
        return_value=httpx.Response(400, text="Syntax error near 'SELEKT'")
    )
    result = json.loads(await query_data_connect(ctx, DC_URL, "SELEKT * FROM foo"))
    assert result["error"]["code"] == "INVALID_REQUEST"


@respx.mock
async def test_query_data_connect_auth_error(ctx):
    respx.post(f"{DC_URL}/search").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await query_data_connect(ctx, DC_URL, "SELECT 1"))
    assert result["error"]["code"] == "AUTH_REQUIRED"


def test_data_connect_register_returns_5_tools():
    from ga4gh_mcp.tools.data_connect_tools import register
    assert len(register()) == 5
    expected = {
        "get_data_connect_service_info",
        "list_data_connect_tables",
        "get_data_connect_table_info",
        "get_data_connect_table_data",
        "query_data_connect",
    }
    assert set(register().keys()) == expected
