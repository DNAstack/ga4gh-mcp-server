"""GA4GH Data Connect tools — 5 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.data_connect import DataConnectClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> DataConnectClient:
    return DataConnectClient(base_url=service_url, bearer_token=bearer_token)


async def get_data_connect_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Data Connect service at {service_url}")


async def list_data_connect_tables(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).list_tables(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Data Connect service at {service_url}")


async def get_data_connect_table_info(
    ctx: ToolContext, service_url: str, table_name: str, bearer_token: str | None = None
) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_table_info(table_name), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Table '{table_name}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Data Connect service at {service_url}")


async def get_data_connect_table_data(
    ctx: ToolContext,
    service_url: str,
    table_name: str,
    page_size: int = 100,
    page_token: str | None = None,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_table_data(
                table_name, page_size=page_size, page_token=page_token
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Table '{table_name}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Data Connect service at {service_url}")


async def query_data_connect(
    ctx: ToolContext, service_url: str, sql: str, bearer_token: str | None = None
) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).query(sql), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return ctx.error("INVALID_REQUEST", f"Invalid SQL query: {e.response.text[:200]}")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Data Connect service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_data_connect_service_info": (
            Tool(
                name="get_data_connect_service_info",
                description="Get service-info metadata for a Data Connect endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Data Connect service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_data_connect_service_info,
        ),
        "list_data_connect_tables": (
            Tool(
                name="list_data_connect_tables",
                description="List all tables available at a Data Connect endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Data Connect service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_data_connect_tables,
        ),
        "get_data_connect_table_info": (
            Tool(
                name="get_data_connect_table_info",
                description="Get schema and metadata for a specific table at a Data Connect endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Data Connect service"},
                        "table_name": {"type": "string", "description": "Table name (e.g. 'public.sample_metadata')"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "table_name"],
                },
            ),
            get_data_connect_table_info,
        ),
        "get_data_connect_table_data": (
            Tool(
                name="get_data_connect_table_data",
                description="Retrieve paginated rows from a table at a Data Connect endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Data Connect service"},
                        "table_name": {"type": "string", "description": "Table name"},
                        "page_size": {"type": "integer", "description": "Rows per page (default 100)", "default": 100},
                        "page_token": {"type": "string", "description": "Pagination token from previous response"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "table_name"],
                },
            ),
            get_data_connect_table_data,
        ),
        "query_data_connect": (
            Tool(
                name="query_data_connect",
                description="Execute a SQL query against a Data Connect endpoint and return matching rows.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Data Connect service"},
                        "sql": {"type": "string", "description": "SQL SELECT query (e.g. 'SELECT * FROM public.samples WHERE phenotype = \\'epilepsy\\' LIMIT 10')"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "sql"],
                },
            ),
            query_data_connect,
        ),
    }
