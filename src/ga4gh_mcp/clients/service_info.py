"""Client for GA4GH Service Info (any compliant service)."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class ServiceInfoClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/service-info")
