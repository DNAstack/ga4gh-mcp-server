"""Tool registration context and error helpers."""

from __future__ import annotations

import json
import logging

from ga4gh_mcp.auth.session import Session
from ga4gh_mcp.config.settings import Settings

logger = logging.getLogger(__name__)

ERROR_CODES = {
    "INVALID_REQUEST",
    "AUTH_REQUIRED",
    "NOT_FOUND",
    "RATE_LIMITED",
    "SERVICE_ERROR",
    "CONNECTION_ERROR",
    "INTERNAL_ERROR",
}


class ToolContext:
    """Context passed to every tool handler."""

    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def error(self, code: str, message: str) -> str:
        """Return a structured JSON error string."""
        return json.dumps({"error": {"code": code, "message": message}}, indent=2)
