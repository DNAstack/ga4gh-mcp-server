"""GA4GH TES tools — 5 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.tes import TesClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> TesClient:
    return TesClient(base_url=service_url, bearer_token=bearer_token)


async def get_tes_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TES service at {service_url}")


async def list_tes_tasks(
    ctx: ToolContext,
    service_url: str,
    name_prefix: str | None = None,
    state: str | None = None,
    page_size: int = 100,
    page_token: str | None = None,
    view: str = "MINIMAL",
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).list_tasks(
                name_prefix=name_prefix, state=state,
                page_size=page_size, page_token=page_token, view=view,
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TES service at {service_url}")


async def get_tes_task(
    ctx: ToolContext,
    service_url: str,
    task_id: str,
    view: str = "FULL",
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_task(task_id, view=view), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"TES task '{task_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TES service at {service_url}")


async def create_tes_task(
    ctx: ToolContext,
    service_url: str,
    name: str,
    executors: list,
    inputs: list | None = None,
    outputs: list | None = None,
    resources: dict | None = None,
    bearer_token: str | None = None,
) -> str:
    task: dict = {"name": name, "executors": executors}
    if inputs:
        task["inputs"] = inputs
    if outputs:
        task["outputs"] = outputs
    if resources:
        task["resources"] = resources
    try:
        return json.dumps(await _client(service_url, bearer_token).create_task(task), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return ctx.error("INVALID_REQUEST", f"Invalid task definition: {e.response.text[:200]}")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TES service at {service_url}")


async def cancel_tes_task(ctx: ToolContext, service_url: str, task_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).cancel_task(task_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"TES task '{task_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TES service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_tes_service_info": (
            Tool(
                name="get_tes_service_info",
                description="Get service-info for a TES endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TES service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_tes_service_info,
        ),
        "list_tes_tasks": (
            Tool(
                name="list_tes_tasks",
                description="List tasks on a TES service. Filter by name prefix or state (QUEUED, INITIALIZING, RUNNING, PAUSED, COMPLETE, EXECUTOR_ERROR, SYSTEM_ERROR, CANCELED, CANCELING). View: MINIMAL, BASIC, or FULL.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TES service"},
                        "name_prefix": {"type": "string", "description": "Filter tasks by name prefix"},
                        "state": {"type": "string", "description": "Filter by task state"},
                        "page_size": {"type": "integer", "description": "Number of tasks per page (default 100)", "default": 100},
                        "page_token": {"type": "string", "description": "Pagination token"},
                        "view": {"type": "string", "description": "Detail level: MINIMAL, BASIC, or FULL (default MINIMAL)", "default": "MINIMAL"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_tes_tasks,
        ),
        "get_tes_task": (
            Tool(
                name="get_tes_task",
                description="Get full details for a TES task including logs, state, and executor outputs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TES service"},
                        "task_id": {"type": "string", "description": "TES task ID"},
                        "view": {"type": "string", "description": "Detail level: MINIMAL, BASIC, or FULL (default FULL)", "default": "FULL"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "task_id"],
                },
            ),
            get_tes_task,
        ),
        "create_tes_task": (
            Tool(
                name="create_tes_task",
                description="Create and submit a new computational task to a TES service.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TES service"},
                        "name": {"type": "string", "description": "Human-readable task name"},
                        "executors": {
                            "type": "array",
                            "description": "List of executors (each with image, command, env, workdir)",
                            "items": {"type": "object"},
                        },
                        "inputs": {"type": "array", "description": "Input files to stage", "items": {"type": "object"}},
                        "outputs": {"type": "array", "description": "Output files to collect", "items": {"type": "object"}},
                        "resources": {"type": "object", "description": "Resource requirements (cpu_cores, ram_gb, disk_gb)"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "name", "executors"],
                },
            ),
            create_tes_task,
        ),
        "cancel_tes_task": (
            Tool(
                name="cancel_tes_task",
                description="Cancel a running or queued TES task.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TES service"},
                        "task_id": {"type": "string", "description": "TES task ID to cancel"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "task_id"],
                },
            ),
            cancel_tes_task,
        ),
    }
