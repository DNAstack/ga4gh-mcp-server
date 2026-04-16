"""GA4GH DRS tools — 3 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.drs import DrsClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> DrsClient:
    return DrsClient(base_url=service_url, bearer_token=bearer_token)


async def get_drs_object(ctx: ToolContext, service_url: str, object_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_object(object_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"DRS object '{object_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach DRS service at {service_url}")


async def get_drs_access_url(ctx: ToolContext, service_url: str, object_id: str, access_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_access_url(object_id, access_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"DRS object '{object_id}' or access method '{access_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach DRS service at {service_url}")


async def get_drs_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach DRS service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_drs_object": (
            Tool(
                name="get_drs_object",
                description="Retrieve DRS object metadata: checksums, size, access methods, and timestamps.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the DRS service"},
                        "object_id": {"type": "string", "description": "DRS object ID (e.g. 'abc123' or full DRS URI)"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token for authenticated services"},
                    },
                    "required": ["service_url", "object_id"],
                },
            ),
            get_drs_object,
        ),
        "get_drs_access_url": (
            Tool(
                name="get_drs_access_url",
                description="Get a signed/presigned access URL for a DRS object using a specific access method.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the DRS service"},
                        "object_id": {"type": "string", "description": "DRS object ID"},
                        "access_id": {"type": "string", "description": "Access method ID (from get_drs_object response)"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "object_id", "access_id"],
                },
            ),
            get_drs_access_url,
        ),
        "get_drs_service_info": (
            Tool(
                name="get_drs_service_info",
                description="Get service-info metadata for a DRS endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the DRS service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_drs_service_info,
        ),
    }
