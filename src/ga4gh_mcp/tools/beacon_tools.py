"""GA4GH Beacon v2 tools — 7 tools."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.types import Tool

from ga4gh_mcp.clients.beacon import BeaconClient
from ga4gh_mcp.tools.registry import ToolContext


def _client(service_url: str, bearer_token: str | None = None) -> BeaconClient:
    return BeaconClient(base_url=service_url, bearer_token=bearer_token)


def _handle_error(ctx: ToolContext, e: httpx.HTTPStatusError, service_url: str) -> str:
    if e.response.status_code in (401, 403):
        return ctx.error("AUTH_REQUIRED", "Service requires authentication. Supply bearer_token.")
    return ctx.error("SERVICE_ERROR", f"Beacon returned {e.response.status_code}")


async def get_beacon_info(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_info(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def get_beacon_configuration(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_configuration(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def get_beacon_map(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_map(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def list_beacon_entry_types(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).list_entry_types(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def get_beacon_filtering_terms(ctx: ToolContext, service_url: str, bearer_token: str | None = None) -> str:
    try:
        return json.dumps(await _client(service_url, bearer_token).get_filtering_terms(), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def query_beacon_variants(
    ctx: ToolContext,
    service_url: str,
    reference_name: str | None = None,
    start: list[int] | None = None,
    end: list[int] | None = None,
    reference_bases: str | None = None,
    alternate_bases: str | None = None,
    gene_id: str | None = None,
    assembly_id: str | None = None,
    filters: list[dict] | None = None,
    bearer_token: str | None = None,
) -> str:
    query: dict = {"meta": {"apiVersion": "v2.0"}, "query": {"requestParameters": {}}}
    rp = query["query"]["requestParameters"]
    if reference_name:
        rp["referenceName"] = reference_name
    if start:
        rp["start"] = start
    if end:
        rp["end"] = end
    if reference_bases:
        rp["referenceBases"] = reference_bases
    if alternate_bases:
        rp["alternateBases"] = alternate_bases
    if gene_id:
        rp["geneId"] = gene_id
    if assembly_id:
        rp["assemblyId"] = assembly_id
    if filters:
        query["query"]["filters"] = filters
    try:
        return json.dumps(await _client(service_url, bearer_token).query_variants(query), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


async def query_beacon_individuals(
    ctx: ToolContext,
    service_url: str,
    filters: list[dict] | None = None,
    include_resultset_responses: str = "HIT",
    pagination_skip: int = 0,
    pagination_limit: int = 10,
    bearer_token: str | None = None,
) -> str:
    query: dict = {
        "meta": {"apiVersion": "v2.0"},
        "query": {
            "pagination": {"skip": pagination_skip, "limit": pagination_limit},
            "includeResultsetResponses": include_resultset_responses,
        },
    }
    if filters:
        query["query"]["filters"] = filters
    try:
        return json.dumps(await _client(service_url, bearer_token).query_individuals(query), indent=2)
    except httpx.HTTPStatusError as e:
        return _handle_error(ctx, e, service_url)
    except httpx.ConnectError:
        return ctx.error("CONNECTION_ERROR", f"Cannot reach Beacon at {service_url}")


def register() -> dict[str, tuple[Tool, Any]]:
    return {
        "get_beacon_info": (
            Tool(
                name="get_beacon_info",
                description="Get Beacon metadata and capabilities including organization, description, and supported entry types.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_beacon_info,
        ),
        "get_beacon_configuration": (
            Tool(
                name="get_beacon_configuration",
                description="Get Beacon v2 configuration including entry types, schemas, and security attributes.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_beacon_configuration,
        ),
        "get_beacon_map": (
            Tool(
                name="get_beacon_map",
                description="Get the map of implemented Beacon endpoints and their configurations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_beacon_map,
        ),
        "list_beacon_entry_types": (
            Tool(
                name="list_beacon_entry_types",
                description="List all entry types supported by this Beacon (variants, individuals, biosamples, cohorts, etc.).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            list_beacon_entry_types,
        ),
        "get_beacon_filtering_terms": (
            Tool(
                name="get_beacon_filtering_terms",
                description="Get accepted filtering terms and ontologies for queries to this Beacon.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            get_beacon_filtering_terms,
        ),
        "query_beacon_variants": (
            Tool(
                name="query_beacon_variants",
                description="Query a Beacon for genomic variants by chromosomal position, allele, or gene.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "reference_name": {"type": "string", "description": "Chromosome (e.g. '17', 'X')"},
                        "start": {"type": "array", "items": {"type": "integer"}, "description": "Start position(s) (0-based)"},
                        "end": {"type": "array", "items": {"type": "integer"}, "description": "End position(s)"},
                        "reference_bases": {"type": "string", "description": "Reference allele (e.g. 'A')"},
                        "alternate_bases": {"type": "string", "description": "Alternate allele (e.g. 'T')"},
                        "gene_id": {"type": "string", "description": "Gene identifier (e.g. 'BRCA2')"},
                        "assembly_id": {"type": "string", "description": "Genome assembly (e.g. 'GRCh38')"},
                        "filters": {"type": "array", "items": {"type": "object"}, "description": "Ontology filters"},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            query_beacon_variants,
        ),
        "query_beacon_individuals": (
            Tool(
                name="query_beacon_individuals",
                description="Query a Beacon for individuals matching phenotypic or clinical criteria using ontology filters.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_url": {"type": "string", "description": "Base URL of the Beacon service"},
                        "filters": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Ontology filters (e.g. [{\"id\": \"HP:0001250\", \"operator\": \"=\", \"value\": \"true\"}])",
                        },
                        "include_resultset_responses": {
                            "type": "string",
                            "description": "Which datasets to include: HIT, MISS, ALL, NONE (default HIT)",
                            "default": "HIT",
                        },
                        "pagination_skip": {"type": "integer", "description": "Pagination skip (default 0)", "default": 0},
                        "pagination_limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                        "bearer_token": {"type": "string", "description": "Optional Bearer token"},
                    },
                    "required": ["service_url"],
                },
            ),
            query_beacon_individuals,
        ),
    }
