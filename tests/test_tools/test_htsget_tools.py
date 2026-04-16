"""Tests for htsget tools."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext
from ga4gh_mcp.tools.htsget_tools import (
    get_htsget_reads,
    get_htsget_reads_post,
    get_htsget_variants,
    get_htsget_variants_post,
)

HTSGET_URL = "https://htsget.example.org"


@pytest.fixture
def ctx():
    settings = Settings(server=ServerConfig(), registry=RegistryConfig())
    return ToolContext(session=Session("test-user"), settings=settings)


@respx.mock
async def test_get_htsget_reads(ctx):
    respx.get(f"{HTSGET_URL}/reads/NA12878").mock(
        return_value=httpx.Response(200, json={"htsget": {"format": "BAM", "urls": [{"url": "https://example.com/data.bam"}]}})
    )
    result = json.loads(await get_htsget_reads(ctx, HTSGET_URL, "NA12878", reference_name="chr1", start=0, end=10000))
    assert result["htsget"]["format"] == "BAM"


@respx.mock
async def test_get_htsget_reads_not_found(ctx):
    respx.get(f"{HTSGET_URL}/reads/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_htsget_reads(ctx, HTSGET_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_htsget_reads_auth_error(ctx):
    respx.get(f"{HTSGET_URL}/reads/secure").mock(return_value=httpx.Response(401, json={}))
    result = json.loads(await get_htsget_reads(ctx, HTSGET_URL, "secure"))
    assert result["error"]["code"] == "AUTH_REQUIRED"


@respx.mock
async def test_get_htsget_reads_connection_error(ctx):
    respx.get(f"{HTSGET_URL}/reads/NA12878").mock(side_effect=httpx.ConnectError("refused"))
    result = json.loads(await get_htsget_reads(ctx, HTSGET_URL, "NA12878"))
    assert result["error"]["code"] == "CONNECTION_ERROR"


@respx.mock
async def test_get_htsget_variants(ctx):
    respx.get(f"{HTSGET_URL}/variants/giab").mock(
        return_value=httpx.Response(200, json={"htsget": {"format": "VCF", "urls": []}})
    )
    result = json.loads(await get_htsget_variants(ctx, HTSGET_URL, "giab"))
    assert result["htsget"]["format"] == "VCF"


@respx.mock
async def test_get_htsget_variants_not_found(ctx):
    respx.get(f"{HTSGET_URL}/variants/nope").mock(return_value=httpx.Response(404, json={}))
    result = json.loads(await get_htsget_variants(ctx, HTSGET_URL, "nope"))
    assert result["error"]["code"] == "NOT_FOUND"


@respx.mock
async def test_get_htsget_reads_post(ctx):
    respx.post(f"{HTSGET_URL}/reads/NA12878").mock(
        return_value=httpx.Response(200, json={"htsget": {"format": "BAM", "urls": []}})
    )
    result = json.loads(await get_htsget_reads_post(
        ctx, HTSGET_URL, "NA12878",
        regions=[{"referenceName": "chr1", "start": 0, "end": 1000}]
    ))
    assert result["htsget"]["format"] == "BAM"


@respx.mock
async def test_get_htsget_variants_post(ctx):
    respx.post(f"{HTSGET_URL}/variants/giab").mock(
        return_value=httpx.Response(200, json={"htsget": {"format": "VCF", "urls": []}})
    )
    result = json.loads(await get_htsget_variants_post(
        ctx, HTSGET_URL, "giab",
        regions=[{"referenceName": "chr17", "start": 43000000, "end": 43100000}]
    ))
    assert result["htsget"]["format"] == "VCF"


def test_htsget_register_returns_4_tools():
    from ga4gh_mcp.tools.htsget_tools import register
    assert len(register()) == 4
