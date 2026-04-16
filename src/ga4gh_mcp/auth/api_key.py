"""API key validation with timing-safe comparison."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any


class ApiKeyValidator:
    """Validates API keys against stored hashes using timing-safe comparison."""

    def __init__(self, keys: list[dict[str, Any]]):
        # key_hash -> user_id
        self._keys = {entry["key_hash"]: entry["user_id"] for entry in keys}

    def validate(self, raw_key: str) -> str | None:
        """Validate a raw API key. Returns user_id if valid, None otherwise."""
        incoming_hash = f"sha256:{hashlib.sha256(raw_key.encode()).hexdigest()}"

        # Iterate all keys to prevent timing-based enumeration
        matched_user = None
        for stored_hash, user_id in self._keys.items():
            if hmac.compare_digest(incoming_hash, stored_hash):
                matched_user = user_id

        return matched_user

    @staticmethod
    def generate_key() -> tuple[str, str]:
        """Generate a new API key. Returns (raw_key, key_hash)."""
        raw_key = f"gam_{secrets.token_hex(32)}"
        key_hash = f"sha256:{hashlib.sha256(raw_key.encode()).hexdigest()}"
        return raw_key, key_hash
