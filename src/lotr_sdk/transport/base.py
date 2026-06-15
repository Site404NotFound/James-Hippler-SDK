"""Execution-agnostic transport behavior shared by the sync and async variants.

``BaseTransport`` owns request building, auth, response handling, and error
mapping. Retries are handled by the ``httpx-retries`` ``RetryTransport`` wired
into each client; the concrete transports add only how a request is sent.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import APIError, api_error_from_status
from lotr_sdk.version import __version__

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

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return float(raw)  # delta-seconds form
        except ValueError:
            pass
        try:
            when = parsedate_to_datetime(raw)  # HTTP-date form
        except (TypeError, ValueError):
            return None
        # The cool-off is the time remaining until that date, never negative.
        return max((when - datetime.now(when.tzinfo)).total_seconds(), 0.0)

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
        self, method: str, path: str, response: httpx.Response, start: float
    ) -> dict[str, Any]:
        """Log the request outcome, then process the response.

        A successful response logs at ``DEBUG``; an error status logs at
        ``WARNING`` before :meth:`_process_response` raises the typed
        :class:`APIError`. Network give-ups are logged separately, by the
        concrete ``request``.
        """
        elapsed_ms = _elapsed_ms(start)
        if response.is_success:
            self._log_request(method, path, response.status_code, elapsed_ms)
        else:
            self._log_error_response(method, path, response.status_code, elapsed_ms)
        return self._process_response(response)

    def _log_request(self, method: str, path: str, status: int, elapsed_ms: float) -> None:
        logger.debug(
            "request",
            extra={"method": method, "path": path, "status": status, "elapsed_ms": elapsed_ms},
        )

    def _log_error_response(self, method: str, path: str, status: int, elapsed_ms: float) -> None:
        logger.warning(
            "request_failed",
            extra={"method": method, "path": path, "status": status, "elapsed_ms": elapsed_ms},
        )

    def _log_failure(self, method: str, path: str, reason: str) -> None:
        logger.error(
            "request_failed",
            extra={"method": method, "path": path, "reason": reason},
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
