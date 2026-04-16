"""GA4GH Service Registry tools — 3 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.service_registry import ServiceRegistryClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> ServiceRegistryClient:
    return ServiceRegistryClient(base_url=service_url, bearer_token=bearer_token)


async def list_registered_services(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).list_services(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach service at {service_url}")


async def get_registered_service(ctx: ToolContext, service_url: str, service_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service(service_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Service '{service_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach service at {service_url}")


async def get_service_registry_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "list_registered_services": (
            Tool(
                name="list_registered_services",
                description="List all services registered in a GA4GH Service Registry instance.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Service Registry"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_registered_services,
        ),
        "get_registered_service": (
            Tool(
                name="get_registered_service",
                description="Get a specific service by ID from a GA4GH Service Registry.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Service Registry"},
                        "service_id": {"type": "string", "description": "Service ID to retrieve"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "service_id"],
                },
            ),
            get_registered_service,
        ),
        "get_service_registry_info": (
            Tool(
                name="get_service_registry_info",
                description="Get service-info metadata for a GA4GH Service Registry endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Service Registry"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_service_registry_info,
        ),
    }
