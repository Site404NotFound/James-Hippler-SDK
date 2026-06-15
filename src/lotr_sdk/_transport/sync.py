"""Synchronous HTTP transport."""

from __future__ import annotations

import time
from typing import Any

import httpx
from httpx_retries import Retry, RetryTransport

from lotr_sdk._transport.base import BaseTransport
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import TransportError

__all__ = ["SyncTransport"]


class SyncTransport(BaseTransport):
    """Synchronous transport backed by an :class:`httpx.Client` with retries."""

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        retry = Retry(total=config.max_retries, backoff_factor=config.backoff_factor)
        self._client = httpx.Client(timeout=config.timeout, transport=RetryTransport(retry=retry))

    def request(self, method: str, path: str, query_string: str = "") -> dict[str, Any]:
        request = self._build_request(method, path, query_string)
        start = time.perf_counter()
        try:
            response = self._client.send(request)
        except httpx.HTTPError as exc:
            error = TransportError(f"Request to {request.url} failed: {exc}")
            self._log_failure(method, path, type(error).__name__)
            raise error from exc
        return self._finish(method, path, response, start)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
