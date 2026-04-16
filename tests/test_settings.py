"""Tests for config/settings."""
from __future__ import annotations

from pathlib import Path

import pytest

from ga4gh_mcp.config.settings import ApiKeyEntry, Settings, load_settings


def test_load_settings_from_tmp_config(tmp_config_dir: Path):
    settings = load_settings(tmp_config_dir)
    assert settings.server.transport == "stdio"
    assert settings.server.port == 9090
    assert settings.registry.base_url == "https://registry.ga4gh.org/v1"
    assert len(settings.api_keys) == 1
    assert settings.api_keys[0].user_id == "test-user"


def test_load_settings_defaults_when_no_files(tmp_path: Path):
    config_dir = tmp_path / "empty"
    config_dir.mkdir()
    settings = load_settings(config_dir)
    assert settings.server.host == "0.0.0.0"
    assert settings.server.port == 8080
    assert settings.registry.base_url == "https://registry.ga4gh.org/v1"
    assert settings.api_keys == []


def test_load_settings_env_override(tmp_config_dir: Path, monkeypatch):
    monkeypatch.setenv("GA4GH_MCP_PORT", "9999")
    monkeypatch.setenv("GA4GH_MCP_LOG_LEVEL", "debug")
    settings = load_settings(tmp_config_dir)
    assert settings.server.port == 9999
    assert settings.server.log_level == "debug"


def test_settings_default_factory():
    s = Settings()
    assert isinstance(s.api_keys, list)
    assert s.server.max_sessions == 1000
