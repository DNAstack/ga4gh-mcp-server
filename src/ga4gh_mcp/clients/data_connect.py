"""Client for GA4GH Data Connect (Tables API + SQL query)."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class DataConnectClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/service-info")

    async def list_tables(self) -> list[dict]:
        return await self.get_paginated("/tables", items_key="tables")

    async def get_table_info(self, table_name: str) -> dict[str, Any]:
        return await self.get(f"/table/{table_name}/info")

    async def get_table_data(
        self,
        table_name: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        params: dict = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        return await self.get(f"/table/{table_name}/data", params=params)

    async def query(self, sql: str) -> dict[str, Any]:
        return await self.post("/search", json={"query": sql})
