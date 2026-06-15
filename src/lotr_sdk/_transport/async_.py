"""Asynchronous HTTP transport."""

from __future__ import annotations

import time
from typing import Any

import httpx
from httpx_retries import Retry, RetryTransport

from lotr_sdk._transport.base import BaseTransport
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import TransportError

__all__ = ["AsyncTransport"]


class AsyncTransport(BaseTransport):
    """Asynchronous transport backed by an :class:`httpx.AsyncClient` with retries."""

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        retry = Retry(total=config.max_retries, backoff_factor=config.backoff_factor)
        self._client = httpx.AsyncClient(
            timeout=config.timeout, transport=RetryTransport(retry=retry)
        )

    async def request(self, method: str, path: str, query_string: str = "") -> dict[str, Any]:
        request = self._build_request(method, path, query_string)
        start = time.perf_counter()
        try:
            response = await self._client.send(request)
        except httpx.HTTPError as exc:
            error = TransportError(f"Request to {request.url} failed: {exc}")
            self._log_failure(method, path, type(error).__name__)
            raise error from exc
        return self._finish(method, path, response, start)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
