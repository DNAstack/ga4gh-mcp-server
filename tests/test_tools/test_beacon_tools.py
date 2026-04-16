"""Tests for Beacon v2 tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.beacon_tools import (
    get_beacon_configuration,
    get_beacon_filtering_terms,
    get_beacon_info,
    get_beacon_map,
    list_beacon_entry_types,
    query_beacon_individuals,
    query_beacon_variants,
)

BEACON_URL = "https://beacon.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_beacon_info(ctx):
    respx.get(f"{BEACON_URL}/").mock(
        return_value=httpx.Response(200, json={"id": "beacon-1", "name": "Example Beacon"})
    )
    result = json.loads(await get_beacon_info(ctx, BEACON_URL))
    assert result["id"] == "beacon-1"


@respx.mock
async def test_get_beacon_info_connection_error(ctx):
    respx.get(f"{BEACON_URL}/").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_beacon_info(ctx, BEACON_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_get_beacon_configuration(ctx):
    respx.get(f"{BEACON_URL}/configuration").mock(
        return_value=httpx.Response(200, json={"meta": {}, "response": {"entryTypes": {}}})
    )
    result = json.loads(await get_beacon_configuration(ctx, BEACON_URL))
    assert "response" in result


@respx.mock
async def test_get_beacon_map(ctx):
    respx.get(f"{BEACON_URL}/map").mock(
        return_value=httpx.Response(200, json={"meta": {}, "response": {"endpointSets": {}}})
    )
    result = json.loads(await get_beacon_map(ctx, BEACON_URL))
    assert "response" in result


@respx.mock
async def test_list_beacon_entry_types(ctx):
    respx.get(f"{BEACON_URL}/entry_types").mock(
        return_value=httpx.Response(200, json={"entryTypes": {"genomicVariant": {}, "individual": {}}})
    )
    result = json.loads(await list_beacon_entry_types(ctx, BEACON_URL))
    assert "entryTypes" in result


@respx.mock
async def test_get_beacon_filtering_terms(ctx):
    respx.get(f"{BEACON_URL}/filtering_terms").mock(
        return_value=httpx.Response(200, json={"filteringTerms": [{"id": "HP:0001250", "label": "Seizure"}]})
    )
    result = json.loads(await get_beacon_filtering_terms(ctx, BEACON_URL))
    assert result["filteringTerms"][0]["id"] == "HP:0001250"


@respx.mock
async def test_query_beacon_variants(ctx):
    respx.post(f"{BEACON_URL}/g_variants").mock(
        return_value=httpx.Response(200, json={"responseSummary": {"exists": True, "numTotalResults": 3}})
    )
    result = json.loads(await query_beacon_variants(
        ctx, BEACON_URL,
        reference_name="17",
        start=[43044295],
        reference_bases="A",
        alternate_bases="T",
        assembly_id="GRCh38",
    ))
    assert result["responseSummary"]["exists"] is True


@respx.mock
async def test_query_beacon_variants_auth_error(ctx):
    respx.post(f"{BEACON_URL}/g_variants").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await query_beacon_variants(ctx, BEACON_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_query_beacon_individuals(ctx):
    respx.post(f"{BEACON_URL}/individuals").mock(
        return_value=httpx.Response(200, json={"responseSummary": {"exists": True, "numTotalResults": 5}})
    )
    result = json.loads(await query_beacon_individuals(
        ctx, BEACON_URL,
        filters=[{"id": "HP:0001250", "operator": "=", "value": "true"}],
    ))
    assert result["responseSummary"]["numTotalResults"] == 5


@respx.mock
async def test_query_beacon_individuals_auth_error(ctx):
    respx.post(f"{BEACON_URL}/individuals").mock(return_value=httpx.Response(403, json={}))
    result = json.loads(await query_beacon_individuals(ctx, BEACON_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


def test_beacon_register_returns_7_tools():
    from ga4gh_mcp.tools.beacon_tools import register
    assert len(register()) == 7
