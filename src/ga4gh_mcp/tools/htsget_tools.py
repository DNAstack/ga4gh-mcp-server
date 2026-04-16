"""GA4GH htsget tools — 4 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.htsget import HtsgetClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> HtsgetClient:
    return HtsgetClient(base_url=service_url, bearer_token=bearer_token)


def _handle_error(ctx: ToolContext, e: httpx.HTTPStatusError) -> str:
    if e.response.status_code == 404:
        return ctx.error("NOT_FOUND", "Resource not found")
    if e.response.status_code in (401, 403):
        return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
    return ctx.error("SERVICE_ERROR", f"Service returned {e.response.status_code}")


async def get_htsget_reads(
    ctx: ToolContext,
    service_url: str,
    read_id: str,
    reference_name: str | None = None,
    start: int | None = None,
    end: int | None = None,
    format: str | None = None,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_reads(
                read_id, reference_name=reference_name, start=start, end=end, format=format
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach htsget service at {service_url}")


async def get_htsget_variants(
    ctx: ToolContext,
    service_url: str,
    variant_id: str,
    reference_name: str | None = None,
    start: int | None = None,
    end: int | None = None,
    format: str | None = None,
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(
            await _client(service_url, bearer_token).get_variants(
                variant_id, reference_name=reference_name, start=start, end=end, format=format
            ),
            indent=2,
        )
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach htsget service at {service_url}")


async def get_htsget_reads_post(
    ctx: ToolContext,
    service_url: str,
    read_id: str,
    regions: list[dict],
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_reads_post(read_id, regions), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach htsget service at {service_url}")


async def get_htsget_variants_post(
    ctx: ToolContext,
    service_url: str,
    variant_id: str,
    regions: list[dict],
    bearer_token: str | None = None,
) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_variants_post(variant_id, regions), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach htsget service at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_htsget_reads": (
            Tool(
                name="get_htsget_reads",
                description="Retrieve reads for a genomic region via htsget (BAM/CRAM format). Returns ticket with download URLs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the htsget service"},
                        "read_id": {"type": "string", "description": "Read dataset ID"},
                        "reference_name": {"type": "string", "description": "Chromosome (e.g. 'chr1', '1')"},
                        "start": {"type": "integer", "description": "Start position (0-based, inclusive)"},
                        "end": {"type": "integer", "description": "End position (0-based, exclusive)"},
                        "format": {"type": "string", "description": "Output format: BAM or CRAM"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "read_id"],
                },
            ),
            get_htsget_reads,
        ),
        "get_htsget_variants": (
            Tool(
                name="get_htsget_variants",
                description="Retrieve variants for a genomic region via htsget (VCF/BCF format). Returns ticket with download URLs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the htsget service"},
                        "variant_id": {"type": "string", "description": "Variant dataset ID"},
                        "reference_name": {"type": "string", "description": "Chromosome"},
                        "start": {"type": "integer", "description": "Start position (0-based, inclusive)"},
                        "end": {"type": "integer", "description": "End position (0-based, exclusive)"},
                        "format": {"type": "string", "description": "Output format: VCF or BCF"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "variant_id"],
                },
            ),
            get_htsget_variants,
        ),
        "get_htsget_reads_post": (
            Tool(
                name="get_htsget_reads_post",
                description="POST-based reads retrieval for multiple genomic regions in a single request.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the htsget service"},
                        "read_id": {"type": "string", "description": "Read dataset ID"},
                        "regions": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of regions: [{\"referenceName\": \"chr1\", \"start\": 0, \"end\": 1000}]",
                        },
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "read_id", "regions"],
                },
            ),
            get_htsget_reads_post,
        ),
        "get_htsget_variants_post": (
            Tool(
                name="get_htsget_variants_post",
                description="POST-based variants retrieval for multiple genomic regions in a single request.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the htsget service"},
                        "variant_id": {"type": "string", "description": "Variant dataset ID"},
                        "regions": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of regions: [{\"referenceName\": \"chr1\", \"start\": 0, \"end\": 1000}]",
                        },
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url", "variant_id", "regions"],
                },
            ),
            get_htsget_variants_post,
        ),
    }
