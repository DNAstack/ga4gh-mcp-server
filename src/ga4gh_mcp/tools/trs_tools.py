"""GA4GH TRS tools — 8 tools."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.trs import TrsClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> TrsClient:
    return TrsClient(base_url=service_url, bearer_token=bearer_token)


def _handle_http_error(ctx: ToolContext, e: httpx.HTTPStatusError, resource: str = "resource") -> str:
    if e.response.status_code == 404:
        return ctx.error("NOT_FOUND", f"{resource} not found")
    if e.response.status_code in (401, 403):
        return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
    return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")


async def get_trs_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def list_trs_tools(
    ctx: ToolContext,
    service_url: str,
    name: str | None = None,
    tool_class: str | None = None,
    descriptor_type: str | None = None,
    offset: int = 0,
    limit: int = 100,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).list_tools(
                name=name, tool_class=tool_class, descriptor_type=descriptor_type,
                offset=offset, limit=limit,
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def get_trs_tool(ctx: ToolContext, service_url: str, tool_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_tool(quote(tool_id, safe="")), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e, f"Tool '{tool_id}'")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def list_trs_tool_versions(ctx: ToolContext, service_url: str, tool_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).list_versions(quote(tool_id, safe="")), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e, f"Tool '{tool_id}'")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def get_trs_tool_version(
    ctx: ToolContext, service_url: str, tool_id: str, version_id: str, bearer_token: str | None = None
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_version(quote(tool_id, safe=""), version_id),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e, f"Tool '{tool_id}' version '{version_id}'")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def get_trs_descriptor(
    ctx: ToolContext,
    service_url: str,
    tool_id: str,
    version_id: str,
    descriptor_type: str,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_descriptor(
                quote(tool_id, safe=""), version_id, descriptor_type
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e, f"Descriptor for '{tool_id}' version '{version_id}'")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def get_trs_files(
    ctx: ToolContext,
    service_url: str,
    tool_id: str,
    version_id: str,
    descriptor_type: str,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_files(
                quote(tool_id, safe=""), version_id, descriptor_type
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e, f"Files for '{tool_id}' version '{version_id}'")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


async def list_trs_tool_classes(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).list_tool_classes(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_http_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach TRS service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_trs_service_info": (
            Tool(
                name="get_trs_service_info",
                description="Get service-info for a TRS endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_trs_service_info,
        ),
        "list_trs_tools": (
            Tool(
                name="list_trs_tools",
                description="List tools/workflows in a TRS registry. Filter by name, toolClass (Workflow, CommandLineTool), or descriptorType (CWL, WDL, NFL, Galaxy).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "name": {"type": "string", "description": "Filter by tool name"},
                        "tool_class": {"type": "string", "description": "Filter by tool class (Workflow, CommandLineTool)"},
                        "descriptor_type": {"type": "string", "description": "Filter by descriptor type (CWL, WDL, NFL, Galaxy)"},
                        "offset": {"type": "integer", "description": "Pagination offset (default 0)", "default": 0},
                        "limit": {"type": "integer", "description": "Max results (default 100)", "default": 100},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_trs_tools,
        ),
        "get_trs_tool": (
            Tool(
                name="get_trs_tool",
                description="Get metadata for a specific TRS tool/workflow by ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "tool_id": {"type": "string", "description": "Tool ID (e.g. '#workflow/myworkflow' or 'biocontainers/samtools')"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "tool_id"],
                },
            ),
            get_trs_tool,
        ),
        "list_trs_tool_versions": (
            Tool(
                name="list_trs_tool_versions",
                description="List all versions of a tool in a TRS registry.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "tool_id": {"type": "string", "description": "Tool ID"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "tool_id"],
                },
            ),
            list_trs_tool_versions,
        ),
        "get_trs_tool_version": (
            Tool(
                name="get_trs_tool_version",
                description="Get metadata for a specific version of a TRS tool.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "tool_id": {"type": "string", "description": "Tool ID"},
                        "version_id": {"type": "string", "description": "Version ID (e.g. '1.0', 'v2.3.1')"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "tool_id", "version_id"],
                },
            ),
            get_trs_tool_version,
        ),
        "get_trs_descriptor": (
            Tool(
                name="get_trs_descriptor",
                description="Get the workflow descriptor source (CWL, WDL, Nextflow, Galaxy) for a specific tool version.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "tool_id": {"type": "string", "description": "Tool ID"},
                        "version_id": {"type": "string", "description": "Version ID"},
                        "descriptor_type": {"type": "string", "description": "Descriptor type: CWL, WDL, NFL (Nextflow), SMK, Galaxy"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "tool_id", "version_id", "descriptor_type"],
                },
            ),
            get_trs_descriptor,
        ),
        "get_trs_files": (
            Tool(
                name="get_trs_files",
                description="List all files associated with a specific tool version in a TRS registry.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "tool_id": {"type": "string", "description": "Tool ID"},
                        "version_id": {"type": "string", "description": "Version ID"},
                        "descriptor_type": {"type": "string", "description": "Descriptor type: CWL, WDL, NFL, Galaxy"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "tool_id", "version_id", "descriptor_type"],
                },
            ),
            get_trs_files,
        ),
        "list_trs_tool_classes": (
            Tool(
                name="list_trs_tool_classes",
                description="List all tool classes available in a TRS registry (e.g. Workflow, CommandLineTool).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the TRS service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_trs_tool_classes,
        ),
    }
