"""HTTP transport layer over httpx.

A :class:`BaseTransport` holds everything that does not depend on the execution
model — request building, auth, error mapping, and the retry policy. The sync
and async subclasses differ only in how they send a request and sleep between
retries, keeping the shared behavior in one place.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ._version import __version__
from .config import ClientConfig
from .exceptions import APIError, TransportError, api_error_from_status

__all__ = ["AsyncTransport", "BaseTransport", "SyncTransport"]


class BaseTransport:
    """Shared request building, response handling, and retry policy."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config

    def _build_request(self, method: str, path: str, query_string: str) -> httpx.Request:
        url = httpx.URL(f"{self._config.base_url}/{path}")
        if query_string:
            # Use the pre-encoded query verbatim; httpx would otherwise re-encode
            # the operator characters the API expects.
            url = url.copy_with(query=query_string.encode("ascii"))
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Accept": "application/json",
            "User-Agent": f"lotr-sdk/{__version__}",
        }
        return httpx.Request(method, url, headers=headers)

    def _should_retry(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def _backoff(self, attempt: int) -> float:
        return self._config.backoff_factor * (2.0**attempt)

    def _retry_delay(self, attempt: int, response: httpx.Response) -> float:
        return self._retry_after(response) or self._backoff(attempt)

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _process_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.is_success:
            data = self._safe_json(response)
            if not isinstance(data, dict):
                raise APIError(
                    response.status_code,
                    "Expected a JSON object in the response body",
                    response=response,
                )
            return data
        raise api_error_from_status(
            response.status_code,
            self._error_message(response),
            retry_after=self._retry_after(response),
            response=response,
        )

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return None

    def _error_message(self, response: httpx.Response) -> str:
        body = self._safe_json(response)
        if isinstance(body, dict):
            message = body.get("message")
            if isinstance(message, str):
                return message
        return response.text or "API request failed"


class SyncTransport(BaseTransport):
    """Synchronous transport backed by an :class:`httpx.Client`."""

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self._client = httpx.Client(timeout=config.timeout)

    def request(self, method: str, path: str, query_string: str = "") -> dict[str, Any]:
        request = self._build_request(method, path, query_string)
        for attempt in range(self._config.max_retries + 1):
            is_last = attempt == self._config.max_retries
            try:
                response = self._client.send(request)
            except httpx.HTTPError as exc:
                if is_last:
                    raise TransportError(f"Request to {request.url} failed: {exc}") from exc
                time.sleep(self._backoff(attempt))
                continue
            if not is_last and self._should_retry(response.status_code):
                time.sleep(self._retry_delay(attempt, response))
                continue
            return self._process_response(response)
        raise AssertionError("retry loop exited without returning")  # pragma: no cover

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


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
