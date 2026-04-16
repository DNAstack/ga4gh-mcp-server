"""Shared test fixtures."""
from __future__ import annotations

import hashlib
import secrets
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory with test configs."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    raw_key = f"gam_{secrets.token_hex(32)}"
    key_hash = f"sha256:{hashlib.sha256(raw_key.encode()).hexdigest()}"

    server = {
        "server": {
            "host": "127.0.0.1",
            "port": 9090,
            "transport": "stdio",
            "log_level": "debug",
            "session_ttl_minutes": 60,
            "max_sessions": 10,
        },
        "registry": {
            "base_url": "https://registry.ga4gh.org/v1",
        },
    }
    keys = {
        "keys": [
            {
                "user_id": "test-user",
                "key_hash": key_hash,
                "description": "Test key",
                "created_at": "2026-04-16",
            }
        ]
    }

    (config_dir / "server.yaml").write_text(yaml.dump(server))
    (config_dir / "api-keys.yaml").write_text(yaml.dump(keys))
    return config_dir


@pytest.fixture
def test_api_key() -> tuple[str, str]:
    """Return (raw_key, key_hash) pair for testing."""
    raw_key = f"gam_{secrets.token_hex(32)}"
    key_hash = f"sha256:{hashlib.sha256(raw_key.encode()).hexdigest()}"
    return raw_key, key_hash
