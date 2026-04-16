"""GA4GH refget tools — 3 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.refget import RefgetClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> RefgetClient:
    return RefgetClient(base_url=service_url, bearer_token=bearer_token)


async def get_refget_service_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_service_info(), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach refget service at {service_url}")


async def get_refget_metadata(ctx: ToolContext, service_url: str, sequence_id: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_metadata(sequence_id), indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Sequence '{sequence_id}' not found")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach refget service at {service_url}")


async def get_refget_sequence(
    ctx: ToolContext,
    service_url: str,
    sequence_id: str,
    start: int | None = None,
    end: int | None = None,
    bearer_token: str | None = None,
) -> str:
    try:
        seq = await _client(service_url, bearer_token).get_sequence(sequence_id, start=start, end=end)
        # refget returns plain text sequence
        if isinstance(seq, str):
            return json.dumps({"sequence_id": sequence_id, "sequence": seq, "start": start, "end": end}, indent=2)
        return json.dumps(seq, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return ctx.error("NOT_FOUND", f"Sequence '{sequence_id}' not found")
        if e.response.status_code == 416:
            return ctx.error("INVALID_REQUEST", "Range out of bounds for this sequence")
        if e.response.status_code in (401, 403):
            return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
        return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach refget service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_refget_service_info": (
            Tool(
                name="get_refget_service_info",
                description="Get service-info for a refget endpoint, including supported algorithms and circular sequence support.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the refget service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_refget_service_info,
        ),
        "get_refget_metadata": (
            Tool(
                name="get_refget_metadata",
                description="Get metadata for a reference sequence by ID (length, aliases, checksums).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the refget service"},
                        "sequence_id": {"type": "string", "description": "Sequence ID (MD5, SHA-512, or accession)"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "sequence_id"],
                },
            ),
            get_refget_metadata,
        ),
        "get_refget_sequence": (
            Tool(
                name="get_refget_sequence",
                description="Retrieve a reference sequence or subsequence by ID. Optionally specify start/end coordinates.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the refget service"},
                        "sequence_id": {"type": "string", "description": "Sequence ID (MD5, SHA-512, or accession)"},
                        "start": {"type": "integer", "description": "Start position (0-based, inclusive)"},
                        "end": {"type": "integer", "description": "End position (0-based, exclusive)"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "sequence_id"],
                },
            ),
            get_refget_sequence,
        ),
    }
