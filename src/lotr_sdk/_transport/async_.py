"""Asynchronous HTTP transport."""

from __future__ import annotations

import asyncio
import time
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
        start = time.perf_counter()
        for attempt in range(self._config.max_retries + 1):
            is_last = attempt == self._config.max_retries
            try:
                response = await self._client.send(request)
            except httpx.HTTPError as exc:
                if is_last:
                    error = TransportError(f"Request to {request.url} failed: {exc}")
                    self._log_failure(method, path, attempt + 1, type(error).__name__)
                    raise error from exc
                delay = self._backoff(attempt)
                self._log_retry(method, path, attempt + 1, None, delay)
                await asyncio.sleep(delay)
                continue
            if not is_last and self._should_retry(response.status_code):
                delay = self._retry_delay(attempt, response)
                self._log_retry(method, path, attempt + 1, response.status_code, delay)
                await asyncio.sleep(delay)
                continue
            return self._finish(method, path, response, start, attempt)
        raise AssertionError("retry loop exited without returning")  # pragma: no cover

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
