"""Client for GA4GH htsget v1.3."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class HtsgetClient(BaseClient):
    async def get_reads(
        self,
        read_id: str,
        reference_name: str | None = None,
        start: int | None = None,
        end: int | None = None,
        format: str | None = None,
    ) -> dict[str, Any]:
        params: dict = {}
        if reference_name:
            params["referenceName"] = reference_name
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if format:
            params["format"] = format
        return await self.get(f"/reads/{read_id}", params=params or None)

    async def get_variants(
        self,
        variant_id: str,
        reference_name: str | None = None,
        start: int | None = None,
        end: int | None = None,
        format: str | None = None,
    ) -> dict[str, Any]:
        params: dict = {}
        if reference_name:
            params["referenceName"] = reference_name
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if format:
            params["format"] = format
        return await self.get(f"/variants/{variant_id}", params=params or None)

    async def get_reads_post(self, read_id: str, regions: list[dict]) -> dict[str, Any]:
        return await self.post(f"/reads/{read_id}", json={"regions": regions})

    async def get_variants_post(self, variant_id: str, regions: list[dict]) -> dict[str, Any]:
        return await self.post(f"/variants/{variant_id}", json={"regions": regions})
