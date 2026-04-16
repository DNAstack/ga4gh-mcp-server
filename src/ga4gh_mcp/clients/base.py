"""Base HTTP client with retry, pagination, and structured error handling."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30.0
_DATA_TIMEOUT = 120.0
_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
_MAX_RETRIES = 3


class BaseClient:
    """Base async HTTP client for GA4GH service APIs."""

    def __init__(
        self,
        base_url: str,
        bearer_token: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        retry_delay: float = 1.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._bearer_token = bearer_token
        self._timeout = timeout
        self._retry_delay = retry_delay

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        return headers

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self._base_url}{path}"

    async def get(self, path: str, params: dict | None = None, timeout: float | None = None) -> Any:
        return await self._request("GET", path, params=params, timeout=timeout)

    async def post(self, path: str, json: dict | None = None, timeout: float | None = None) -> Any:
        return await self._request("POST", path, json=json, timeout=timeout)

    async def delete(self, path: str, timeout: float | None = None) -> Any:
        return await self._request("DELETE", path, timeout=timeout)

    async def get_paginated(
        self,
        path: str,
        items_key: str = "data",
        params: dict | None = None,
        max_pages: int = 100,
    ) -> list[dict]:
        """Follow pagination and collect all results. Handles next_page_url pattern."""
        all_results: list[dict] = []
        url = self._url(path)
        current_params = params

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for _ in range(max_pages):
                resp = await client.get(url, headers=self._headers(), params=current_params)
                resp.raise_for_status()
                body = resp.json()

                if isinstance(body, list):
                    all_results.extend(body)
                    break
                else:
                    items = body.get(items_key, [])
                    all_results.extend(items)
                    pagination = body.get("pagination") or {}
                    next_url = pagination.get("next_page_url")
                    if not next_url:
                        break
                    url = next_url
                    current_params = None

        return all_results

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        timeout = kwargs.pop("timeout", None) or self._timeout
        url = self._url(path)
        logger.debug(f"{method} {url}")

        async with httpx.AsyncClient(timeout=timeout) as client:
            last_resp = None
            for attempt in range(_MAX_RETRIES):
                try:
                    resp = await client.request(method, url, headers=self._headers(), **kwargs)
                except httpx.ConnectError as e:
                    raise httpx.ConnectError(str(e), request=None) from e

                if resp.status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES - 1:
                    last_resp = resp
                    delay = self._retry_delay * (2 ** attempt)
                    logger.warning(f"Retryable {resp.status_code} on {url}, retry in {delay}s")
                    await asyncio.sleep(delay)
                    continue

                resp.raise_for_status()
                ct = resp.headers.get("content-type", "")
                if "application/json" in ct:
                    return resp.json()
                return resp.text

            raise httpx.HTTPStatusError(
                f"Max retries exceeded for {method} {url}",
                request=last_resp.request,
                response=last_resp,
            )
