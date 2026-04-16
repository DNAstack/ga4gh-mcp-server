"""GA4GH Service Info tool — 1 tool."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.service_info import ServiceInfoClient
from ga4gh_mcp.tools.registry import ToolContext


async def get_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    client = ServiceInfoClient(base_url=service_url, bearer_token=bearer_token)
    try:
        return json.dumps(await client.get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", f"Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_service_info": (
            Tool(
                name="get_service_info",
                description="Get GA4GH service-info metadata from any GA4GH-compliant service. Returns service type, version, organization, and capabilities.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the GA4GH service (e.g. 'https://drs.example.org')"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token for authenticated services"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_service_info,
        ),
    }
