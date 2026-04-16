"""Client for GA4GH TES (Task Execution Service) v1.1."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class TesClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/ga4gh/tes/v1/service-info")

    async def list_tasks(
        self,
        name_prefix: str | None = None,
        state: str | None = None,
        page_size: int = 100,
        page_token: str | None = None,
        view: str = "MINIMAL",
    ) -> dict[str, Any]:
        params: dict = {"page_size": page_size, "view": view}
        if name_prefix:
            params["name_prefix"] = name_prefix
        if state:
            params["state"] = state
        if page_token:
            params["page_token"] = page_token
        return await self.get("/ga4gh/tes/v1/tasks", params=params)

    async def get_task(self, task_id: str, view: str = "FULL") -> dict[str, Any]:
        return await self.get(f"/ga4gh/tes/v1/tasks/{task_id}", params={"view": view})

    async def create_task(self, task: dict) -> dict[str, Any]:
        return await self.post("/ga4gh/tes/v1/tasks", json=task)

    async def cancel_task(self, task_id: str) -> dict[str, Any]:
        return await self.post(f"/ga4gh/tes/v1/tasks/{task_id}:cancel")
