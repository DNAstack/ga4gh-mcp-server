"""Tests for GA4GH registry tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.registry_tools import (
    get_implementation,
    get_organization,
    get_service,
    get_standard,
    list_implementations,
    list_organizations,
    list_services,
    list_standards,
    search_implementations,
    search_organizations,
    search_services,
    search_standards,
)

REGISTRY_BASE = "https://registry.ga4gh.org/v1"


@pytest.fixture
def ctx():
    settings = Settings(
        server=ServerConfig(),
        registry=RegistryConfig(base_url=REGISTRY_BASE),
    )
    return ToolContext(session=Session("test-user"), settings=settings)


# --- list_standards ---

@respx.mock
async def test_list_standards_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/standards").mock(
        return_value=httpx.Response(200, json={"standards": [{"id": "drs", "name": "DRS"}]})
    )
    result = json.loads(await list_standards(ctx))
    assert result[0]["id"] == "drs"


@respx.mock
async def test_list_standards_with_filters(ctx):
    route = respx.get(f"{REGISTRY_BASE}/standards").mock(
        return_value=httpx.Response(200, json={"standards": []})
    )
    await list_standards(ctx, category="data", status="approved")
    assert "category=data" in str(route.calls[0].request.url)


@respx.mock
async def test_list_standards_connection_error(ctx):
    respx.get(f"{REGISTRY_BASE}/standards").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await list_standards(ctx))
    assert result["error"]["code"] == "CONNECTION_ERROR"


# --- get_standard ---

@respx.mock
async def test_get_standard_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/standards/drs").mock(
        return_value=httpx.Response(200, json={"id": "drs", "name": "Data Repository Service"})
    )
    result = json.loads(await get_standard(ctx, "drs"))
    assert result["id"] == "drs"


@respx.mock
async def test_get_standard_not_found(ctx):
    respx.get(f"{REGISTRY_BASE}/standards/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_standard(ctx, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


# --- search_standards ---

@respx.mock
async def test_search_standards(ctx):
    respx.get(f"{REGISTRY_BASE}/standards").mock(
        return_value=httpx.Response(200, json={"standards": [{"id": "wes"}]})
    )
    result = json.loads(await search_standards(ctx, "workflow"))
    assert result[0]["id"] == "wes"


# --- list_services ---

@respx.mock
async def test_list_services_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/services").mock(
        return_value=httpx.Response(200, json={"services": [{"id": "svc-1"}]})
    )
    result = json.loads(await list_services(ctx))
    assert result[0]["id"] == "svc-1"


@respx.mock
async def test_list_services_with_standard_filter(ctx):
    route = respx.get(f"{REGISTRY_BASE}/services").mock(
        return_value=httpx.Response(200, json={"services": []})
    )
    await list_services(ctx, standard="WES")
    assert "standard=WES" in str(route.calls[0].request.url)


# --- get_service ---

@respx.mock
async def test_get_service_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/services/svc-1").mock(
        return_value=httpx.Response(200, json={"id": "svc-1", "base_url": "https://wes.example.org"})
    )
    result = json.loads(await get_service(ctx, "svc-1"))
    assert result["base_url"] == "https://wes.example.org"


@respx.mock
async def test_get_service_not_found(ctx):
    respx.get(f"{REGISTRY_BASE}/services/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_service(ctx, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


# --- search_services ---

@respx.mock
async def test_search_services(ctx):
    respx.get(f"{REGISTRY_BASE}/services").mock(
        return_value=httpx.Response(200, json={"services": [{"id": "svc-ebi"}]})
    )
    result = json.loads(await search_services(ctx, "ebi"))
    assert result[0]["id"] == "svc-ebi"


# --- list_implementations ---

@respx.mock
async def test_list_implementations(ctx):
    respx.get(f"{REGISTRY_BASE}/implementations").mock(
        return_value=httpx.Response(200, json={"implementations": [{"id": "impl-1"}]})
    )
    result = json.loads(await list_implementations(ctx))
    assert result[0]["id"] == "impl-1"


# --- get_implementation ---

@respx.mock
async def test_get_implementation_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/implementations/impl-1").mock(
        return_value=httpx.Response(200, json={"id": "impl-1", "name": "Toil"})
    )
    result = json.loads(await get_implementation(ctx, "impl-1"))
    assert result["name"] == "Toil"


@respx.mock
async def test_get_implementation_not_found(ctx):
    respx.get(f"{REGISTRY_BASE}/implementations/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_implementation(ctx, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


# --- search_implementations ---

@respx.mock
async def test_search_implementations(ctx):
    respx.get(f"{REGISTRY_BASE}/implementations").mock(
        return_value=httpx.Response(200, json={"implementations": [{"id": "toil"}]})
    )
    result = json.loads(await search_implementations(ctx, "toil"))
    assert result[0]["id"] == "toil"


# --- list_organizations ---

@respx.mock
async def test_list_organizations(ctx):
    respx.get(f"{REGISTRY_BASE}/organizations").mock(
        return_value=httpx.Response(200, json={"organizations": [{"id": "ga4gh"}]})
    )
    result = json.loads(await list_organizations(ctx))
    assert result[0]["id"] == "ga4gh"


# --- get_organization ---

@respx.mock
async def test_get_organization_happy_path(ctx):
    respx.get(f"{REGISTRY_BASE}/organizations/ga4gh").mock(
        return_value=httpx.Response(200, json={"id": "ga4gh", "name": "GA4GH"})
    )
    result = json.loads(await get_organization(ctx, "ga4gh"))
    assert result["name"] == "GA4GH"


@respx.mock
async def test_get_organization_not_found(ctx):
    respx.get(f"{REGISTRY_BASE}/organizations/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_organization(ctx, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


# --- search_organizations ---

@respx.mock
async def test_search_organizations(ctx):
    respx.get(f"{REGISTRY_BASE}/organizations").mock(
        return_value=httpx.Response(200, json={"organizations": [{"id": "elixir"}]})
    )
    result = json.loads(await search_organizations(ctx, "elixir"))
    assert result[0]["id"] == "elixir"


# --- register() ---

def test_register_returns_12_tools():
    from ga4gh_mcp.tools.registry_tools import register
    tools = register()
    assert len(tools) == 12
    expected = {
        "list_standards", "get_standard", "search_standards",
        "list_services", "get_service", "search_services",
        "list_implementations", "get_implementation", "search_implementations",
        "list_organizations", "get_organization", "search_organizations",
    }
    assert set(tools.keys()) == expected
