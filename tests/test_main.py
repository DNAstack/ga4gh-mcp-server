"""Tests for __main__ entry point."""
from __future__ import annotations

import subprocess
import sys


def test_generate_key_output():
    result = subprocess.run(
        ["uv", "run", "ga4gh-mcp", "generate-key", "--user", "alice", "--description", "Test key"],
        capture_output=True,
        text=True,
        cwd="/Users/mfiume/Development/ga4gh-mcp-server",
    )
    assert result.returncode == 0
    assert "gam_" in result.stdout
    assert "sha256:" in result.stdout
    assert "alice" in result.stdout
    assert "Test key" in result.stdout
