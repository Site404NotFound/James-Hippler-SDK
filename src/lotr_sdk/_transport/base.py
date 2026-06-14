"""Execution-agnostic transport behavior shared by the sync and async variants.

``BaseTransport`` owns request building, auth, response handling, error mapping,
and the retry *policy*. The concrete transports add only how a request is sent
and how the retry loop sleeps.
"""

from __future__ import annotations

import logging
import time
from http import HTTPStatus
from typing import Any

import httpx

from lotr_sdk._version import __version__
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import APIError, api_error_from_status

__all__ = ["BaseTransport"]

_USER_AGENT = f"lotr-sdk/{__version__}"

logger = logging.getLogger(__name__)


def _elapsed_ms(start: float) -> float:
    """Milliseconds elapsed since ``start`` (a ``time.perf_counter()`` reading)."""
    return round((time.perf_counter() - start) * 1000, 1)


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
            "Authorization": f"Bearer {self._config.api_key.get_secret_value()}",
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        }
        return httpx.Request(method, url, headers=headers)

    def _should_retry(self, status_code: int) -> bool:
        return (
            status_code == HTTPStatus.TOO_MANY_REQUESTS
            or status_code >= HTTPStatus.INTERNAL_SERVER_ERROR
        )

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

    def _finish(
        self, method: str, path: str, response: httpx.Response, start: float, attempt: int
    ) -> dict[str, Any]:
        """Process a terminal response, logging success or an exhausted-retry failure."""
        try:
            data = self._process_response(response)
        except APIError as exc:
            if self._should_retry(response.status_code):
                self._log_failure(method, path, attempt + 1, type(exc).__name__)
            raise
        self._log_request(method, path, response.status_code, _elapsed_ms(start))
        return data

    def _log_request(self, method: str, path: str, status: int, elapsed_ms: float) -> None:
        logger.debug(
            "request",
            extra={"method": method, "path": path, "status": status, "elapsed_ms": elapsed_ms},
        )

    def _log_retry(
        self, method: str, path: str, attempt: int, status: int | None, delay_s: float
    ) -> None:
        logger.warning(
            "retry",
            extra={
                "method": method,
                "path": path,
                "attempt": attempt,
                "status": status,
                "delay_s": delay_s,
            },
        )

    def _log_failure(self, method: str, path: str, attempts: int, reason: str) -> None:
        logger.error(
            "request_failed",
            extra={"method": method, "path": path, "attempts": attempts, "reason": reason},
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
