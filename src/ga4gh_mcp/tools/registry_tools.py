"""GA4GH Implementation Registry tools — 12 tools for Tier 1 discovery."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.registry import RegistryClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(ctx: ToolContext) -> RegistryClient:
    return RegistryClient(base_url=ctx.settings.registry.base_url)


async def list_standards(ctx: ToolContext, category: str | None = None, status: str | None = None) -> str:
    try:
        return json.dumps(await _client(ctx).list_standards(category=category, status=status), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def get_standard(ctx: ToolContext, standard_id: str) -> str:
    try:
        return json.dumps(await _client(ctx).get_standard(standard_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Standard '{standard_id}' not found")
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")


async def search_standards(ctx: ToolContext, q: str) -> str:
    try:
        return json.dumps(await _client(ctx).search_standards(q), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def list_services(ctx: ToolContext, standard: str | None = None, organization: str | None = None) -> str:
    try:
        return json.dumps(await _client(ctx).list_services(standard=standard, organization=organization), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def get_service(ctx: ToolContext, service_id: str) -> str:
    try:
        return json.dumps(await _client(ctx).get_service(service_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Service '{service_id}' not found")
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")


async def search_services(ctx: ToolContext, q: str) -> str:
    try:
        return json.dumps(await _client(ctx).search_services(q), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def list_implementations(ctx: ToolContext, standard: str | None = None) -> str:
    try:
        return json.dumps(await _client(ctx).list_implementations(standard=standard), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def get_implementation(ctx: ToolContext, implementation_id: str) -> str:
    try:
        return json.dumps(await _client(ctx).get_implementation(implementation_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Implementation '{implementation_id}' not found")
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")


async def search_implementations(ctx: ToolContext, q: str) -> str:
    try:
        return json.dumps(await _client(ctx).search_implementations(q), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def list_organizations(ctx: ToolContext) -> str:
    try:
        return json.dumps(await _client(ctx).list_organizations(), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


async def get_organization(ctx: ToolContext, organization_id: str) -> str:
    try:
        return json.dumps(await _client(ctx).get_organization(organization_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Organization '{organization_id}' not found")
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")


async def search_organizations(ctx: ToolContext, q: str) -> str:
    try:
        return json.dumps(await _client(ctx).search_organizations(q), indent=2)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach registry at {ctx.settings.registry.base_url}")
    except httpx.HTTPStatusError as e:
        return ctx.error("SERVICE_ERROR", f"Registry returned {e.response.status_code}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "list_standards": (
            Tool(
                name="list_standards",
                description="List all GA4GH standards in the Implementation Registry. Optionally filter by category or status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Filter by standard category (e.g. 'data', 'compute')"},
                        "status": {"type": "string", "description": "Filter by status (e.g. 'approved', 'deprecated')"},
                    },
                },
            ),
            list_standards,
        ),
        "get_standard": (
            Tool(
                name="get_standard",
                description="Get full details for a GA4GH standard by its ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "standard_id": {"type": "string", "description": "Standard ID (e.g. 'drs', 'wes')"},
                    },
                    "required": ["standard_id"],
                },
            ),
            get_standard,
        ),
        "search_standards": (
            Tool(
                name="search_standards",
                description="Free-text search across GA4GH standards by name, description, or keywords.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "description": "Search query"},
                    },
                    "required": ["q"],
                },
            ),
            search_standards,
        ),
        "list_services": (
            Tool(
                name="list_services",
                description="List services registered in the GA4GH Implementation Registry. Filter by standard or organization.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "standard": {"type": "string", "description": "Filter by standard (e.g. 'WES', 'DRS')"},
                        "organization": {"type": "string", "description": "Filter by organization name or ID"},
                    },
                },
            ),
            list_services,
        ),
        "get_service": (
            Tool(
                name="get_service",
                description="Get full details for a registered GA4GH service by its registry ID, including base URL and contact info.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string", "description": "Service registry ID"},
                    },
                    "required": ["service_id"],
                },
            ),
            get_service,
        ),
        "search_services": (
            Tool(
                name="search_services",
                description="Search GA4GH-registered services by keyword.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "description": "Search query"},
                    },
                    "required": ["q"],
                },
            ),
            search_services,
        ),
        "list_implementations": (
            Tool(
                name="list_implementations",
                description="List software implementations registered in the GA4GH Implementation Registry. Optionally filter by standard.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "standard": {"type": "string", "description": "Filter by standard (e.g. 'TES')"},
                    },
                },
            ),
            list_implementations,
        ),
        "get_implementation": (
            Tool(
                name="get_implementation",
                description="Get full details for a GA4GH software implementation by its registry ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "implementation_id": {"type": "string", "description": "Implementation registry ID"},
                    },
                    "required": ["implementation_id"],
                },
            ),
            get_implementation,
        ),
        "search_implementations": (
            Tool(
                name="search_implementations",
                description="Search GA4GH software implementations by keyword.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "description": "Search query"},
                    },
                    "required": ["q"],
                },
            ),
            search_implementations,
        ),
        "list_organizations": (
            Tool(
                name="list_organizations",
                description="List all organizations registered in the GA4GH Implementation Registry.",
                inputSchema={"type": "object", "properties": {}},
            ),
            list_organizations,
        ),
        "get_organization": (
            Tool(
                name="get_organization",
                description="Get full details for an organization by its registry ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "organization_id": {"type": "string", "description": "Organization registry ID"},
                    },
                    "required": ["organization_id"],
                },
            ),
            get_organization,
        ),
        "search_organizations": (
            Tool(
                name="search_organizations",
                description="Search GA4GH organizations by keyword.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "description": "Search query"},
                    },
                    "required": ["q"],
                },
            ),
            search_organizations,
        ),
    }
