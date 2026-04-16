"""Tests for TRS tools."""
from __future__ import annotations

import json
from urllib.parse import quote

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.trs_tools import (
    get_trs_descriptor,
    get_trs_files,
    get_trs_service_info,
    get_trs_tool,
    get_trs_tool_version,
    list_trs_tool_classes,
    list_trs_tool_versions,
    list_trs_tools,
)

TRS_URL = "https://trs.example.org"
TOOL_ID = "biocontainers/samtools"
TOOL_ID_ENC = quote(TOOL_ID, safe="")


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_trs_service_info(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/service-info").mock(
        return_value=httpx.Response(200, json={"id": "trs-svc"})
    )
    result = json.loads(await get_trs_service_info(ctx, TRS_URL))
    assert result["id"] == "trs-svc"


@respx.mock
async def test_get_trs_service_info_connection_error(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_trs_service_info(ctx, TRS_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_list_trs_tools(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools").mock(
        return_value=httpx.Response(200, json=[{"id": TOOL_ID, "name": "samtools"}])
    )
    result = json.loads(await list_trs_tools(ctx, TRS_URL))
    assert result[0]["id"] == TOOL_ID


@respx.mock
async def test_list_trs_tools_with_descriptor_filter(ctx):
    route = respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools").mock(
        return_value=httpx.Response(200, json=[])
    )
    await list_trs_tools(ctx, TRS_URL, descriptor_type="WDL")
    assert "descriptorType=WDL" in str(route.calls[0].request.url)


@respx.mock
async def test_get_trs_tool(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}").mock(
        return_value=httpx.Response(200, json={"id": TOOL_ID, "name": "samtools"})
    )
    result = json.loads(await get_trs_tool(ctx, TRS_URL, TOOL_ID))
    assert result["name"] == "samtools"


@respx.mock
async def test_get_trs_tool_not_found(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_trs_tool(ctx, TRS_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_list_trs_tool_versions(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}/versions").mock(
        return_value=httpx.Response(200, json=[{"id": "1.15", "name": "samtools"}])
    )
    result = json.loads(await list_trs_tool_versions(ctx, TRS_URL, TOOL_ID))
    assert result[0]["id"] == "1.15"


@respx.mock
async def test_get_trs_tool_version(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}/versions/1.15").mock(
        return_value=httpx.Response(200, json={"id": "1.15", "is_production": True})
    )
    result = json.loads(await get_trs_tool_version(ctx, TRS_URL, TOOL_ID, "1.15"))
    assert result["is_production"] is True


@respx.mock
async def test_get_trs_descriptor(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}/versions/1.15/WDL/descriptor").mock(
        return_value=httpx.Response(200, json={"type": "WDL", "descriptor": "workflow {}"})
    )
    result = json.loads(await get_trs_descriptor(ctx, TRS_URL, TOOL_ID, "1.15", "WDL"))
    assert result["type"] == "WDL"


@respx.mock
async def test_get_trs_descriptor_not_found(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}/versions/1.15/WDL/descriptor").mock(
        return_value=httpx.Response(404, json={})
    )
    result = json.loads(await get_trs_descriptor(ctx, TRS_URL, TOOL_ID, "1.15", "WDL"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_trs_files(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/tools/{TOOL_ID_ENC}/versions/1.15/WDL/files").mock(
        return_value=httpx.Response(200, json=[{"path": "workflow.wdl", "file_type": "PRIMARY_DESCRIPTOR"}])
    )
    result = json.loads(await get_trs_files(ctx, TRS_URL, TOOL_ID, "1.15", "WDL"))
    assert result[0]["path"] == "workflow.wdl"


@respx.mock
async def test_list_trs_tool_classes(ctx):
    respx.get(f"{TRS_URL}/ga4gh/trs/v2/toolClasses").mock(
        return_value=httpx.Response(200, json=[{"id": "0", "name": "Workflow"}, {"id": "1", "name": "CommandLineTool"}])
    )
    result = json.loads(await list_trs_tool_classes(ctx, TRS_URL))
    assert result[0]["name"] == "Workflow"


def test_trs_register_returns_8_tools():
    from ga4gh_mcp.tools.trs_tools import register
    assert len(register()) == 8
