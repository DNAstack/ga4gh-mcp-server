"""Client for GA4GH WES (Workflow Execution Service) v1.1."""

from __future__ import annotations

from typing import Any

from ga4gh_mcp.clients.base import BaseClient


class WesClient(BaseClient):
    async def get_service_info(self) -> dict[str, Any]:
        return await self.get("/ga4gh/wes/v1/service-info")

    async def list_runs(self, page_size: int = 100, page_token: str | None = None, state_filter: str | None = None) -> dict[str, Any]:
        params: dict = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        if state_filter:
            params["state"] = state_filter
        return await self.get("/ga4gh/wes/v1/runs", params=params)

    async def get_run(self, run_id: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/wes/v1/runs/{run_id}")

    async def submit_run(self, workflow_params: dict) -> dict[str, Any]:
        return await self.post("/ga4gh/wes/v1/runs", json=workflow_params)

    async def cancel_run(self, run_id: str) -> dict[str, Any]:
        return await self.post(f"/ga4gh/wes/v1/runs/{run_id}/cancel")

    async def get_run_log(self, run_id: str) -> dict[str, Any]:
        return await self.get(f"/ga4gh/wes/v1/runs/{run_id}/status")
