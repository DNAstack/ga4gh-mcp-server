"""Client for GA4GH DRS (Data Repository Service) v1.4."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class DrsClient(BaseClient):
    async def get_object(self, object_id: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/drs/v1/objects/{object_id}")

    async def get_access_url(self, object_id: str, access_id: str) -> dict[str, Any]:
        return await self.post(f"/ga4gh/drs/v1/objects/{object_id}/access/{access_id}")

    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/service-info")
