"""Client for GA4GH refget v2."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class RefgetClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/sequence/service-info")

    async def get_metadata(self, sequence_id: str) -> dict[str, Any]:
        return await self.get(f"/sequence/{sequence_id}/metadata")

    async def get_sequence(
        self,
        sequence_id: str,
        start: int | None = None,
        end: int | None = None,
    ) -> str:
        params: dict = {}
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        return await self.get(f"/sequence/{sequence_id}", params=params or None)
