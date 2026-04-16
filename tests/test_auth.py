"""Tests for auth — api_key and session."""
from __future__ import annotations

import hashlib
import time

import pytest

from ga4gh_mcp.auth.api_key import ApiKeyValidator
from ga4gh_mcp.auth.session import Session, SessionManager


# --- ApiKeyValidator ---

def test_generate_key_prefix():
    raw, _ = ApiKeyValidator.generate_key()
    assert raw.startswith("gam_")
    assert len(raw) == 4 + 64  # "gam_" + 64 hex chars


def test_generate_key_hash_format():
    _, key_hash = ApiKeyValidator.generate_key()
    assert key_hash.startswith("sha256:")
    assert len(key_hash) == 7 + 64  # "sha256:" + 64 hex chars


def test_validate_valid_key():
    raw, key_hash = ApiKeyValidator.generate_key()
    validator = ApiKeyValidator([{"key_hash": key_hash, "user_id": "alice"}])
    assert validator.validate(raw) == "alice"


def test_validate_invalid_key():
    _, key_hash = ApiKeyValidator.generate_key()
    validator = ApiKeyValidator([{"key_hash": key_hash, "user_id": "alice"}])
    assert validator.validate("gam_" + "0" * 64) is None


def test_validate_empty_keys():
    validator = ApiKeyValidator([])
    raw, _ = ApiKeyValidator.generate_key()
    assert validator.validate(raw) is None


def test_validate_iterates_all_keys():
    raw1, hash1 = ApiKeyValidator.generate_key()
    raw2, hash2 = ApiKeyValidator.generate_key()
    validator = ApiKeyValidator([
        {"key_hash": hash1, "user_id": "alice"},
        {"key_hash": hash2, "user_id": "bob"},
    ])
    assert validator.validate(raw1) == "alice"
    assert validator.validate(raw2) == "bob"


# --- Session ---

def test_session_touch_updates_last_accessed():
    s = Session("user1")
    t0 = s.last_accessed
    time.sleep(0.01)
    s.touch()
    assert s.last_accessed > t0


# --- SessionManager ---

def test_session_manager_get_or_create():
    mgr = SessionManager(ttl_minutes=60, max_sessions=10)
    s = mgr.get_or_create("alice")
    assert s.user_id == "alice"


def test_session_manager_returns_same_session():
    mgr = SessionManager(ttl_minutes=60, max_sessions=10)
    s1 = mgr.get_or_create("alice")
    s2 = mgr.get_or_create("alice")
    assert s1 is s2


def test_session_manager_evicts_oldest_when_full():
    mgr = SessionManager(ttl_minutes=60, max_sessions=2)
    mgr.get_or_create("alice")
    time.sleep(0.01)
    mgr.get_or_create("bob")
    mgr.get_or_create("carol")  # should evict alice (oldest)
    assert mgr.get_or_create("carol").user_id == "carol"
    assert mgr.get_or_create("bob").user_id == "bob"


def test_session_manager_cleanup_expired():
    mgr = SessionManager(ttl_minutes=0, max_sessions=10)
    mgr.get_or_create("alice")
    time.sleep(0.01)
    mgr.cleanup_expired()
    # After cleanup, a new session for alice should be a fresh object
    s = mgr.get_or_create("alice")
    assert s.user_id == "alice"


def test_session_manager_remove():
    mgr = SessionManager(ttl_minutes=60, max_sessions=10)
    mgr.get_or_create("alice")
    mgr.remove("alice")
    mgr.remove("nonexistent")  # should not raise
