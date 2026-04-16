"""Tests for ToolContext and server wiring."""
from __future__ import annotations

import json

import pytest

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import RegistryConfig, ServerConfig, Settings
from ga4gh_mcp.tools.registry import ToolContext


@pytest.fixture
def ctx():
    settings = Settings(
        server=ServerConfig(),
        registry=RegistryConfig(base_url="https://registry.ga4gh.org/v1"),
    )
    session = Session("test-user")
    return ToolContext(session=session, settings=settings)


def test_tool_context_error_returns_json(ctx: ToolContext):
    result = ctx.error("NOT_FOUND", "Resource not found")
    parsed = json.loads(result)
    assert parsed["error"]["code"] == "NOT_FOUND"
    assert parsed["error"]["message"] == "Resource not found"


def test_tool_context_has_session(ctx: ToolContext):
    assert ctx.session.user_id == "test-user"


def test_tool_context_has_settings(ctx: ToolContext):
    assert ctx.settings.registry.base_url == "https://registry.ga4gh.org/v1"
