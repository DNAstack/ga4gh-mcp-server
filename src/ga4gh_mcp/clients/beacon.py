"""Client for GA4GH Beacon v2."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class BeaconClient(BaseClient):
    async def get_info(self) -> dict[str, Any]:
        return await self.get("/")

    async def get_configuration(self) -> dict[str, Any]:
        return await self.get("/configuration")

    async def get_map(self) -> dict[str, Any]:
        return await self.get("/map")

    async def list_entry_types(self) -> dict[str, Any]:
        return await self.get("/entry_types")

    async def get_filtering_terms(self) -> dict[str, Any]:
        return await self.get("/filtering_terms")

    async def query_variants(self, params: dict) -> dict[str, Any]:
        return await self.post("/g_variants", json=params)

    async def query_individuals(self, params: dict) -> dict[str, Any]:
        return await self.post("/individuals", json=params)
