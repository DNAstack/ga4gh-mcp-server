"""Client for the GA4GH Implementation Registry (registry.ga4gh.org/v1)."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class RegistryClient(BaseClient):
    """Client for the GA4GH Implementation Registry."""

    async def list_standards(self, category: str | None = None, status: str | None = None) -> list[dict]:
        params = {}
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        return await self.get_paginated("/standards", items_key="standards", params=params or None)

    async def get_standard(self, standard_id: str) -> dict[str, Any]:
        return await self.get(f"/standards/{standard_id}")

    async def search_standards(self, q: str) -> list[dict]:
        return await self.get_paginated("/standards", items_key="standards", params={"q": q})

    async def list_services(self, standard: str | None = None, organization: str | None = None) -> list[dict]:
        params = {}
        if standard:
            params["standard"] = standard
        if organization:
            params["organization"] = organization
        return await self.get_paginated("/services", items_key="services", params=params or None)

    async def get_service(self, service_id: str) -> dict[str, Any]:
        return await self.get(f"/services/{service_id}")

    async def search_services(self, q: str) -> list[dict]:
        return await self.get_paginated("/services", items_key="services", params={"q": q})

    async def list_implementations(self, standard: str | None = None) -> list[dict]:
        params = {"standard": standard} if standard else None
        return await self.get_paginated("/implementations", items_key="implementations", params=params)

    async def get_implementation(self, implementation_id: str) -> dict[str, Any]:
        return await self.get(f"/implementations/{implementation_id}")

    async def search_implementations(self, q: str) -> list[dict]:
        return await self.get_paginated("/implementations", items_key="implementations", params={"q": q})

    async def list_organizations(self) -> list[dict]:
        return await self.get_paginated("/organizations", items_key="organizations")

    async def get_organization(self, organization_id: str) -> dict[str, Any]:
        return await self.get(f"/organizations/{organization_id}")

    async def search_organizations(self, q: str) -> list[dict]:
        return await self.get_paginated("/organizations", items_key="organizations", params={"q": q})
