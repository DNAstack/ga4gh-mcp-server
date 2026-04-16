"""Tests for TES tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.tes_tools import (
    cancel_tes_task,
    create_tes_task,
    get_tes_service_info,
    get_tes_task,
    list_tes_tasks,
)

TES_URL = "https://tes.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_tes_service_info(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/service-info").mock(
        return_value=httpx.Response(200, json={"id": "tes-svc", "name": "Example TES"})
    )
    result = json.loads(await get_tes_service_info(ctx, TES_URL))
    assert result["id"] == "tes-svc"


@respx.mock
async def test_get_tes_service_info_connection_error(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/service-info").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_tes_service_info(ctx, TES_URL))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_list_tes_tasks(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/tasks").mock(
        return_value=httpx.Response(200, json={"tasks": [{"id": "t1", "state": "COMPLETE"}], "next_page_token": ""})
    )
    result = json.loads(await list_tes_tasks(ctx, TES_URL))
    assert result["tasks"][0]["id"] == "t1"


@respx.mock
async def test_list_tes_tasks_with_state_filter(ctx):
    route = respx.get(f"{TES_URL}/ga4gh/tes/v1/tasks").mock(
        return_value=httpx.Response(200, json={"tasks": []})
    )
    await list_tes_tasks(ctx, TES_URL, state="RUNNING")
    assert "state=RUNNING" in str(route.calls[0].request.url)


@respx.mock
async def test_list_tes_tasks_auth_error(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/tasks").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await list_tes_tasks(ctx, TES_URL))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_tes_task(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/tasks/task-abc").mock(
        return_value=httpx.Response(200, json={"id": "task-abc", "state": "RUNNING", "logs": []})
    )
    result = json.loads(await get_tes_task(ctx, TES_URL, "task-abc"))
    assert result["state"] == "RUNNING"


@respx.mock
async def test_get_tes_task_not_found(ctx):
    respx.get(f"{TES_URL}/ga4gh/tes/v1/tasks/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_tes_task(ctx, TES_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_create_tes_task(ctx):
    respx.post(f"{TES_URL}/ga4gh/tes/v1/tasks").mock(
        return_value=httpx.Response(200, json={"id": "new-task-123"})
    )
    result = json.loads(await create_tes_task(
        ctx, TES_URL,
        name="test-task",
        executors=[{"image": "ubuntu:22.04", "command": ["echo", "hello"]}],
        resources={"cpu_cores": 2, "ram_gb": 4.0},
    ))
    assert result["id"] == "new-task-123"


@respx.mock
async def test_create_tes_task_invalid(ctx):
    respx.post(f"{TES_URL}/ga4gh/tes/v1/tasks").mock(
        return_value=httpx.Response(400, text="Missing executors")
    )
    result = json.loads(await create_tes_task(ctx, TES_URL, "bad", []))
    assert result["error"]["code"] == "INVALID_REQUEST"


@respx.mock
async def test_cancel_tes_task(ctx):
    respx.post(f"{TES_URL}/ga4gh/tes/v1/tasks/task-abc:cancel").mock(
        return_value=httpx.Response(200, json={})
    )
    result = json.loads(await cancel_tes_task(ctx, TES_URL, "task-abc"))
    assert result == {}


@respx.mock
async def test_cancel_tes_task_not_found(ctx):
    respx.post(f"{TES_URL}/ga4gh/tes/v1/tasks/nope:cancel").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await cancel_tes_task(ctx, TES_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


def test_tes_register_returns_5_tools():
    from ga4gh_mcp.tools.tes_tools import register
    assert len(register()) == 5
