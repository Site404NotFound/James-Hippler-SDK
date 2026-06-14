"""Asynchronous HTTP transport."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from lotr_sdk._transport.base import BaseTransport
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import TransportError

__all__ = ["AsyncTransport"]


class AsyncTransport(BaseTransport):
    """Asynchronous transport backed by an :class:`httpx.AsyncClient`."""

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self._client = httpx.AsyncClient(timeout=config.timeout)

    async def request(self, method: str, path: str, query_string: str = "") -> dict[str, Any]:
        request = self._build_request(method, path, query_string)
        for attempt in range(self._config.max_retries + 1):
            is_last = attempt == self._config.max_retries
            try:
                response = await self._client.send(request)
            except httpx.HTTPError as exc:
                if is_last:
                    raise TransportError(f"Request to {request.url} failed: {exc}") from exc
                await asyncio.sleep(self._backoff(attempt))
                continue
            if not is_last and self._should_retry(response.status_code):
                await asyncio.sleep(self._retry_delay(attempt, response))
                continue
            return self._process_response(response)
        raise AssertionError("retry loop exited without returning")  # pragma: no cover

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
