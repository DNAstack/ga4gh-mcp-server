"""Configuration loading for the GA4GH MCP Server."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    transport: str = "streamable-http"  # stdio | streamable-http | sse
    log_level: str = "info"
    session_ttl_minutes: int = 480
    max_sessions: int = 1000


class RegistryConfig(BaseModel):
    base_url: str = "https://registry.ga4gh.org/v1"


class ApiKeyEntry(BaseModel):
    user_id: str
    key_hash: str
    description: str = ""
    created_at: str = ""


class Settings(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    api_keys: list[ApiKeyEntry] = Field(default_factory=list)


def _load_yaml(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_settings(config_dir: str | Path | None = None) -> Settings:
    """Load settings from config directory. Env var GA4GH_MCP_CONFIG_DIR overrides."""
    if config_dir is None:
        config_dir = os.environ.get("GA4GH_MCP_CONFIG_DIR", "./config")
    config_dir = Path(config_dir)

    server_data = _load_yaml(config_dir / "server.yaml")
    keys_data = _load_yaml(config_dir / "api-keys.yaml")

    server_block = server_data.get("server", {})
    if port := os.environ.get("GA4GH_MCP_PORT"):
        server_block["port"] = int(port)
    if log_level := os.environ.get("GA4GH_MCP_LOG_LEVEL"):
        server_block["log_level"] = log_level
    if host := os.environ.get("GA4GH_MCP_HOST"):
        server_block["host"] = host
    if transport := os.environ.get("GA4GH_MCP_TRANSPORT"):
        server_block["transport"] = transport

    return Settings(
        server=ServerConfig(**server_block),
        registry=RegistryConfig(**server_data.get("registry", {})),
        api_keys=[ApiKeyEntry(**k) for k in keys_data.get("keys", [])],
    )
