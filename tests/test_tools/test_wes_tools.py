"""Tests for WES tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.wes_tools import (
    cancel_wes_run,
    get_wes_run,
    get_wes_run_log,
    get_wes_service_info,
    list_wes_runs,
    submit_wes_run,
)

WES_URL = "https://wes.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_wes_service_info(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/service-info").mock(
        return_value=httpx.Response(200, json={"workflow_type_versions": {"WDL": ["1.0", "1.1"]}})
    )
    result = json.loads(await get_wes_service_info(ctx, WES_URL))
    assert "WDL" in result["workflow_type_versions"]


@respx.mock
async def test_get_wes_service_info_connection_error(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_wes_service_info(ctx, WES_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_list_wes_runs(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/runs").mock(
        return_value=httpx.Response(200, json={"runs": [{"run_id": "r1", "state": "COMPLETE"}], "next_page_token": ""})
    )
    result = json.loads(await list_wes_runs(ctx, WES_URL))
    assert result["runs"][0]["run_id"] == "r1"


@respx.mock
async def test_list_wes_runs_auth_error(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/runs").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await list_wes_runs(ctx, WES_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_wes_run(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/runs/run-abc").mock(
        return_value=httpx.Response(200, json={"run_id": "run-abc", "state": "RUNNING"})
    )
    result = json.loads(await get_wes_run(ctx, WES_URL, "run-abc"))
    assert result["state"] == "RUNNING"


@respx.mock
async def test_get_wes_run_not_found(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/runs/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_wes_run(ctx, WES_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_submit_wes_run(ctx):
    respx.post(f"{WES_URL}/ga4gh/wes/v1/runs").mock(
        return_value=httpx.Response(200, json={"run_id": "new-run-123"})
    )
    result = json.loads(await submit_wes_run(
        ctx, WES_URL,
        workflow_url="https://example.com/wf.wdl",
        workflow_type="WDL",
        workflow_type_version="1.0",
        workflow_params={"sample": "NA12878"},
    ))
    assert result["run_id"] == "new-run-123"


@respx.mock
async def test_submit_wes_run_invalid_request(ctx):
    respx.post(f"{WES_URL}/ga4gh/wes/v1/runs").mock(
        return_value=httpx.Response(400, text="Invalid workflow type")
    )
    result = json.loads(await submit_wes_run(ctx, WES_URL, "bad-url", "INVALID", "1.0"))
    assert result["error"]["code"] == "INVALID_REQUEST"


@respx.mock
async def test_cancel_wes_run(ctx):
    respx.post(f"{WES_URL}/ga4gh/wes/v1/runs/run-abc/cancel").mock(
        return_value=httpx.Response(200, json={"run_id": "run-abc"})
    )
    result = json.loads(await cancel_wes_run(ctx, WES_URL, "run-abc"))
    assert result["run_id"] == "run-abc"


@respx.mock
async def test_cancel_wes_run_not_found(ctx):
    respx.post(f"{WES_URL}/ga4gh/wes/v1/runs/nope/cancel").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await cancel_wes_run(ctx, WES_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_wes_run_log(ctx):
    respx.get(f"{WES_URL}/ga4gh/wes/v1/runs/run-abc/status").mock(
        return_value=httpx.Response(200, json={"run_id": "run-abc", "state": "COMPLETE"})
    )
    result = json.loads(await get_wes_run_log(ctx, WES_URL, "run-abc"))
    assert result["state"] == "COMPLETE"


def test_wes_register_returns_6_tools():
    from ga4gh_mcp.tools.wes_tools import register
    assert len(register()) == 6
