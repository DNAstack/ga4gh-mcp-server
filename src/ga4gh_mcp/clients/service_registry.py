"""Client for GA4GH Service Registry API."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class ServiceRegistryClient(BaseClient):
    async def list_services(self) -> list[dict]:
        return await self.get_paginated("/services", items_key="services")

    async def get_service(self, service_id: str) -> dict[str, Any]:
        return await self.get(f"/services/{service_id}")

    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/service-info")
