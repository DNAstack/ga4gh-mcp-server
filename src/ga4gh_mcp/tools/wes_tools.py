"""GA4GH WES tools — 6 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.wes import WesClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> WesClient:
    return WesClient(base_url=service_url, bearer_token=bearer_token)


async def get_wes_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


async def list_wes_runs(
    ctx: ToolContext,
    service_url: str,
    page_size: int = 100,
    page_token: str | None = None,
    state_filter: str | None = None,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).list_runs(
                page_size=page_size, page_token=page_token, state_filter=state_filter
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


async def get_wes_run(ctx: ToolContext, service_url: str, run_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_run(run_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"WES run '{run_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


async def submit_wes_run(
    ctx: ToolContext,
    service_url: str,
    workflow_url: str,
    workflow_type: str,
    workflow_type_version: str,
    workflow_params: dict | None = None,
    tags: dict | None = None,
    bearer_token: str | None = None,
) -> str:
    body: dict = {
        "workflow_url": workflow_url,
        "workflow_type": workflow_type,
        "workflow_type_version": workflow_type_version,
    }
    if workflow_params:
        body["workflow_params"] = json.dumps(workflow_params)
    if tags:
        body["tags"] = json.dumps(tags)
    try:
        return json.dumps(await _client(service_url, bearer_token).submit_run(body), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return ctx.error("INVALID_REQUEST", f"Invalid workflow submission: {e.response.text[:200]}")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


async def cancel_wes_run(ctx: ToolContext, service_url: str, run_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).cancel_run(run_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"WES run '{run_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


async def get_wes_run_log(ctx: ToolContext, service_url: str, run_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_run_log(run_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"WES run '{run_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach WES service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_wes_service_info": (
            Tool(
                name="get_wes_service_info",
                description="Get service-info for a WES endpoint, including supported workflow types (CWL, WDL, Nextflow).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_wes_service_info,
        ),
        "list_wes_runs": (
            Tool(
                name="list_wes_runs",
                description="List workflow runs on a WES service. Optionally filter by state (QUEUED, INITIALIZING, RUNNING, PAUSED, COMPLETE, EXECUTOR_ERROR, SYSTEM_ERROR, CANCELED, CANCELING).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "page_size": {"type": "integer", "description": "Number of runs to return (default 100)", "default": 100},
                        "page_token": {"type": "string", "description": "Pagination token from previous response"},
                        "state_filter": {"type": "string", "description": "Filter by run state"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_wes_runs,
        ),
        "get_wes_run": (
            Tool(
                name="get_wes_run",
                description="Get status and full details for a specific WES workflow run.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "run_id": {"type": "string", "description": "WES run ID"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "run_id"],
                },
            ),
            get_wes_run,
        ),
        "submit_wes_run": (
            Tool(
                name="submit_wes_run",
                description="Submit a new workflow run to a WES service (CWL, WDL, Nextflow, etc.).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "workflow_url": {"type": "string", "description": "URL or path to the workflow descriptor"},
                        "workflow_type": {"type": "string", "description": "Workflow language (CWL, WDL, NFL, SMK)"},
                        "workflow_type_version": {"type": "string", "description": "Workflow language version"},
                        "workflow_params": {"type": "object", "description": "Workflow input parameters"},
                        "tags": {"type": "object", "description": "Optional key-value tags for the run"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "workflow_url", "workflow_type", "workflow_type_version"],
                },
            ),
            submit_wes_run,
        ),
        "cancel_wes_run": (
            Tool(
                name="cancel_wes_run",
                description="Cancel a running or queued WES workflow run.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "run_id": {"type": "string", "description": "WES run ID to cancel"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "run_id"],
                },
            ),
            cancel_wes_run,
        ),
        "get_wes_run_log": (
            Tool(
                name="get_wes_run_log",
                description="Retrieve task logs and status for a completed or running WES workflow run.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the WES service"},
                        "run_id": {"type": "string", "description": "WES run ID"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "run_id"],
                },
            ),
            get_wes_run_log,
        ),
    }
