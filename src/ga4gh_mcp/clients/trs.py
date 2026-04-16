"""Client for GA4GH TRS (Tool Registry Service) v2."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class TrsClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/ga4gh/trs/v2/service-info")

    async def list_tools(
        self,
        name: str | None = None,
        tool_class: str | None = None,
        descriptor_type: str | None = None,
        registry: str | None = None,
        organization: str | None = None,
        author: str | None = None,
        checker: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        params: dict = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name
        if tool_class:
            params["toolClass"] = tool_class
        if descriptor_type:
            params["descriptorType"] = descriptor_type
        if registry:
            params["registry"] = registry
        if organization:
            params["organization"] = organization
        if author:
            params["author"] = author
        if checker is not None:
            params["checker"] = str(checker).lower()
        return await self.get("/ga4gh/trs/v2/tools", params=params)

    async def get_tool(self, tool_id: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/trs/v2/tools/{tool_id}")

    async def list_versions(self, tool_id: str) -> list[dict]:
        return await self.get(f"/ga4gh/trs/v2/tools/{tool_id}/versions")

    async def get_version(self, tool_id: str, version_id: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/trs/v2/tools/{tool_id}/versions/{version_id}")

    async def get_descriptor(self, tool_id: str, version_id: str, descriptor_type: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/trs/v2/tools/{tool_id}/versions/{version_id}/{descriptor_type}/descriptor")

    async def get_files(self, tool_id: str, version_id: str, descriptor_type: str) -> list[dict]:
        return await self.get(f"/ga4gh/trs/v2/tools/{tool_id}/versions/{version_id}/{descriptor_type}/files")

    async def list_tool_classes(self) -> list[dict]:
        return await self.get("/ga4gh/trs/v2/toolClasses")
