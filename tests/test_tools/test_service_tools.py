"""Tests for service_info and service_registry tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.service_info_tools import get_service_info
from ga4gh_mcp.tools.service_registry_tools import (
    get_registered_service,
    get_service_registry_info,
    list_registered_services,
)

SVC_URL = "https://registry.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


# --- get_service_info ---

@respx.mock
async def test_get_service_info_happy_path(ctx):
    respx.get(f"{SVC_URL}/service-info").mock(
        return_value=httpx.Response(200, json={"id": "test-svc", "type": {"group": "org.ga4gh", "artifact": "wes", "version": "1.1.0"}})
    )
    result = json.loads(await get_service_info(ctx, SVC_URL))
    assert result["id"] == "test-svc"


@respx.mock
async def test_get_service_info_auth_error(ctx):
    respx.get(f"{SVC_URL}/service-info").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await get_service_info(ctx, SVC_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_service_info_connection_error(ctx):
    respx.get(f"{SVC_URL}/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_service_info(ctx, SVC_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


# --- list_registered_services ---

@respx.mock
async def test_list_registered_services_happy_path(ctx):
    respx.get(f"{SVC_URL}/services").mock(
        return_value=httpx.Response(200, json={"services": [{"id": "drs-1"}, {"id": "wes-1"}]})
    )
    result = json.loads(await list_registered_services(ctx, SVC_URL))
    assert len(result) == 2
    assert result[0]["id"] == "drs-1"


@respx.mock
async def test_list_registered_services_with_bearer(ctx):
    route = respx.get(f"{SVC_URL}/services").mock(
        return_value=httpx.Response(200, json={"services": []})
    )
    await list_registered_services(ctx, SVC_URL, bearer_token="my-token")
    assert "Bearer my-token" in route.calls[0].request.headers["authorization"]


@respx.mock
async def test_list_registered_services_auth_error(ctx):
    respx.get(f"{SVC_URL}/services").mock(return_value=httpx.Response(403, json={}))
    result = json.loads(await list_registered_services(ctx, SVC_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


# --- get_registered_service ---

@respx.mock
async def test_get_registered_service_happy_path(ctx):
    respx.get(f"{SVC_URL}/services/drs-1").mock(
        return_value=httpx.Response(200, json={"id": "drs-1", "url": "https://drs.example.org"})
    )
    result = json.loads(await get_registered_service(ctx, SVC_URL, "drs-1"))
    assert result["url"] == "https://drs.example.org"


@respx.mock
async def test_get_registered_service_not_found(ctx):
    respx.get(f"{SVC_URL}/services/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_registered_service(ctx, SVC_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


# --- get_service_registry_info ---

@respx.mock
async def test_get_service_registry_info(ctx):
    respx.get(f"{SVC_URL}/service-info").mock(
        return_value=httpx.Response(200, json={"id": "reg-1"})
    )
    result = json.loads(await get_service_registry_info(ctx, SVC_URL))
    assert result["id"] == "reg-1"


# --- register() counts ---

def test_service_info_register_count():
    from ga4gh_mcp.tools.service_info_tools import register
    assert len(register()) == 1


def test_service_registry_register_count():
    from ga4gh_mcp.tools.service_registry_tools import register
    assert len(register()) == 3
